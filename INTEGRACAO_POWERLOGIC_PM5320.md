# Integração de referência — PowerLogic PM5320

## Objetivo

Preparar o primeiro piloto com um medidor trifásico Schneider Electric PowerLogic PM5320, mantendo o VoltGuard apenas em monitoramento. O medidor fornece as grandezas elétricas; um gateway instalado na rede local faz a leitura Modbus TCP e encaminha os dados ao VoltGuard por HTTPS.

## Arquitetura

```text
PowerLogic PM5320
    │ Modbus TCP (rede local; porta 502 não exposta à Internet)
    ▼
Gateway local (Node-RED ou serviço equivalente)
    │ HTTPS POST + token exclusivo do dispositivo
    ▼
VoltGuard: POST /api/device/telemetry
```

O gateway deve iniciar a conexão de saída com o VoltGuard. A aplicação hospedada não deve abrir conexão direta para dentro da rede industrial do cliente.

## Modelo escolhido

O PM5320 é o modelo de referência porque a documentação da Schneider lista Ethernet com Modbus TCP para esse modelo. A família PM5300 não tem a mesma interface em todas as variantes: PM5310 e PM5330, por exemplo, aparecem com comunicação serial, enquanto PM5320/PM5340 têm Ethernet com Modbus TCP. Confirmar o código comercial completo e a revisão de firmware antes de configurar o gateway.

## Contrato atual do VoltGuard

O endpoint de dispositivo é `POST /api/device/telemetry`, com `Authorization: Bearer <token>` e JSON no formato:

```json
{
  "panel_id": "ID_DO_PAINEL",
  "current": 118.4,
  "voltage_v": 380,
  "active_power_kw": 76.2,
  "active_energy_kwh": 1842.7,
  "frequency_hz": 60,
  "power_factor": 0.96,
  "gateway_qr": "IDENTIFICADOR_DO_GATEWAY"
}
```

O endpoint aceita qualquer uma dessas grandezas individualmente ou em conjunto, mas exige ao menos uma leitura numérica. Os valores são persistidos no painel e no histórico. O campo textual `voltage` permanece aceito para gateways antigos. Leituras sem temperatura não disparam nem limpam alarmes térmicos. O token deve permanecer no gateway, nunca em fluxo exportado publicamente, navegador ou repositório. A temperatura do painel precisará de sensor separado caso seja um requisito do piloto; o medidor sozinho não deve ser tratado como fonte dessa medição.

## Mapa de registradores

Não fixar endereços Modbus neste documento. A Schneider publica mapas associados às versões de firmware; usar o mapa correspondente ao modelo exato e firmware instalado. Validar endereço inicial, tipo de dado, escala, ordem de palavras e sinal com leituras do equipamento antes de enviar valores ao VoltGuard.

## Sequência de implementação e homologação

1. Confirmar o código completo do PM5320, firmware e grandezas habilitadas.
2. Obter o mapa Modbus correspondente e testar leitura somente na rede de bancada.
3. Protótipo criado em `gateway/`: coletor Modbus TCP configurável, somente leitura, com envio HTTPS e token exclusivo. Continua sem perfil de registradores PM5320 homologado.
4. Implementado nesta etapa: ampliar e documentar o schema de telemetria do VoltGuard sem quebrar os gateways já existentes.
5. Validar leituras, escala/unidades, perda de conexão, reconexão, timestamps e alarmes com equipamento real.
6. Fazer um piloto isolado, de monitoramento, sem qualquer comando, intertravamento ou função de proteção.

## Critérios de aceite do piloto

- Leituras do VoltGuard conferem com o visor/software local do medidor dentro da precisão e periodicidade acordadas.
- Perda de conectividade é distinguida de alarme elétrico e mostrada com o horário da última leitura.
- Credencial pode ser revogada e não aparece em logs ou no frontend.
- Rede Modbus fica restrita ao segmento local; apenas o gateway envia dados para fora.
- O cliente aprova os limites, as unidades e a finalidade de cada alarme antes de habilitá-los.

## Referências oficiais

- [Schneider Electric Brasil — mapa de registradores Modbus PM5100/PM5300 e downloads por firmware](https://www.se.com/br/pt/faqs/FA283821/)
- [Schneider Electric — opções de comunicação da família PM5300](https://productinfo.se.com/pm5300/5be97f3b347bdf0001d99c87/PM5300%20User%20Manual/English/R_MeterOverview_FeaturesOptionsPM5300_0000082140.xml)
