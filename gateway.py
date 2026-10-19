"""Read-only Modbus TCP gateway that forwards measurements to VoltGuard."""

from __future__ import annotations

import json
import logging
import math
import os
import signal
import struct
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from pymodbus.client import ModbusTcpClient

LOG = logging.getLogger("voltguard-gateway")
DATA_TYPES = {"uint16": 1, "int16": 1, "uint32": 2, "int32": 2, "float32": 2}
MEASUREMENT_RANGES = {
    "temperature": (-50, 250), "current": (0, 100000), "voltage_v": (0, 100000),
    "active_power_kw": (-1000000, 1000000), "active_energy_kwh": (0, 1e15),
    "frequency_hz": (0, 1000), "power_factor": (-1, 1),
}
STOP = False


def stop_handler(_signum: int, _frame: Any) -> None:
    global STOP
    STOP = True


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not config.get("panel_id") or not config.get("voltguard_url"):
        raise ValueError("Configure panel_id e voltguard_url.")
    if len(config["panel_id"]) > 100:
        raise ValueError("panel_id excede o limite de 100 caracteres da API.")
    if not str(config["voltguard_url"]).startswith("https://"):
        raise ValueError("voltguard_url precisa usar HTTPS.")
    if not isinstance(config.get("modbus"), dict) or not config["modbus"].get("host"):
        raise ValueError("Configure o host Modbus local.")
    if not isinstance(config.get("metrics"), dict):
        raise ValueError("Configure metrics conforme o mapa Modbus validado.")
    modbus = config["modbus"]
    device_id = int(modbus.get("device_id", 1))
    timeout = float(modbus.get("timeout_seconds", 3))
    interval = int(config.get("poll_interval_seconds", 10))
    if not 0 <= device_id <= 255 or not 0.5 <= timeout <= 30 or not 2 <= interval <= 3600:
        raise ValueError("Confira device_id (0–255), timeout_seconds (0,5–30) e poll_interval_seconds (2–3600).")
    if config.get("gateway_qr") is not None and len(config["gateway_qr"]) > 160:
        raise ValueError("gateway_qr excede o limite de 160 caracteres da API.")
    usable = [entry for entry in config["metrics"].values() if entry.get("address") is not None]
    if not usable:
        raise ValueError("Nenhum endereço Modbus configurado; use o mapa do modelo e firmware instalados.")
    for name, entry in config["metrics"].items():
        if entry.get("address") is None:
            continue
        if name not in MEASUREMENT_RANGES:
            raise ValueError(f"Grandeza não aceita pelo VoltGuard: {name}")
        address = int(entry["address"])
        if not 0 <= address <= 65535 or address + DATA_TYPES.get(entry.get("data_type"), 1) > 65536:
            raise ValueError(f"Endereço Modbus inválido para {name}.")
        if entry.get("register_type", "input") not in {"input", "holding"}:
            raise ValueError(f"register_type inválido para {name}")
        if entry.get("data_type") not in DATA_TYPES:
            raise ValueError(f"data_type inválido para {name}")
        if entry.get("word_order", "big") not in {"big", "little"}:
            raise ValueError(f"word_order inválido para {name}")
        scale = float(entry.get("scale", 1.0))
        if not math.isfinite(scale) or scale == 0:
            raise ValueError(f"scale precisa ser finito e diferente de zero para {name}.")
    return config


def decode_registers(registers: list[int], data_type: str, word_order: str) -> float:
    if data_type == "uint16":
        return float(registers[0])
    if data_type == "int16":
        return float(struct.unpack(">h", struct.pack(">H", registers[0]))[0])
    words = registers if word_order == "big" else list(reversed(registers))
    raw = struct.pack(">HH", *words)
    formats = {"uint32": ">I", "int32": ">i", "float32": ">f"}
    return float(struct.unpack(formats[data_type], raw)[0])


def read_measurements(client: ModbusTcpClient, config: dict[str, Any]) -> dict[str, float]:
    modbus = config["modbus"]
    readings: dict[str, float] = {}
    for name, entry in config["metrics"].items():
        address = entry.get("address")
        if address is None:
            continue
        count = DATA_TYPES[entry["data_type"]]
        method = client.read_input_registers if entry.get("register_type", "input") == "input" else client.read_holding_registers
        response = method(address=int(address), count=count, device_id=int(modbus.get("device_id", 1)))
        if response.isError() or len(response.registers) != count:
            raise RuntimeError(f"Falha Modbus ao ler a grandeza {name} no endereço configurado.")
        value = decode_registers(response.registers, entry["data_type"], entry.get("word_order", "big"))
        value *= float(entry.get("scale", 1.0))
        if not math.isfinite(value):
            raise RuntimeError(f"Leitura inválida para {name}.")
        minimum, maximum = MEASUREMENT_RANGES[name]
        if not minimum <= value <= maximum:
            raise RuntimeError(f"Leitura de {name} fora do intervalo aceito pelo VoltGuard; confira mapa e escala.")
        readings[name] = value
    return readings


def run(config_path: Path) -> None:
    config = load_config(config_path)
    # Keep the secret outside the config file and source tree.
    token = os.environ.get("VOLTGUARD_DEVICE_TOKEN")
    if not token:
        raise RuntimeError("Defina a variável de ambiente VOLTGUARD_DEVICE_TOKEN.")

    modbus = config["modbus"]
    client = ModbusTcpClient(
        host=modbus["host"], port=int(modbus.get("port", 502)),
        timeout=float(modbus.get("timeout_seconds", 3)), retries=1,
    )
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = config["voltguard_url"].rstrip("/") + "/api/device/telemetry"
    interval = max(2, int(config.get("poll_interval_seconds", 10)))
    LOG.info("Gateway iniciado para o painel %s.", config["panel_id"])
    try:
        with httpx.Client(timeout=10, verify=True) as http:
            while not STOP:
                started = time.monotonic()
                try:
                    if not client.connected and not client.connect():
                        raise RuntimeError("Não foi possível conectar ao medidor Modbus.")
                    payload = {"panel_id": config["panel_id"], **read_measurements(client, config)}
                    if config.get("gateway_qr"):
                        payload["gateway_qr"] = config["gateway_qr"]
                    response = http.post(endpoint, json=payload, headers=headers)
                    response.raise_for_status()
                    LOG.info("Telemetria enviada (%d grandeza(s)).", len(payload) - 1 - int("gateway_qr" in payload))
                except Exception as exc:
                    client.close()
                    LOG.warning("Ciclo de aquisição/envio falhou: %s", exc)
                remaining = interval - (time.monotonic() - started)
                if remaining > 0:
                    time.sleep(min(remaining, 1) if STOP else remaining)
    finally:
        client.close()
        LOG.info("Gateway encerrado.")


if __name__ == "__main__":
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("gateway-config.json")
    try:
        run(path)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        LOG.error("Configuração/execução interrompida: %s", error)
        raise SystemExit(2)
