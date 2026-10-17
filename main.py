import os
import io
import random
import hashlib
import secrets
import hmac
import socket
import ipaddress
from urllib.parse import urlparse
import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
import jwt
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Configurações de Segurança e JWT
# Configure SECRET_KEY in the environment for deployments. The fallback is intentionally
# ephemeral: tokens are invalidated when the process restarts if no key is configured.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY and os.getenv("RENDER"):
    raise RuntimeError("Configure SECRET_KEY nos Environment Variables do Render.")
SECRET_KEY = SECRET_KEY or secrets.token_urlsafe(48)
if len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY deve ter pelo menos 32 caracteres.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Configuração da Base de Dados SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voltguard.db")
# Render pode fornecer URLs PostgreSQL com o esquema postgres://. SQLAlchemy 2
# usa o driver psycopg explicitamente para evitar depender de psycopg2.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS DA BASE DE DADOS ---
class PanelModel(Base):
    __tablename__ = "panels"
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, default="HITECH-DEFAULT", index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    voltage = Column(String, nullable=False)
    current = Column(Float, default=0.0)
    temperature = Column(Float, default=0.0)
    gateway_qr = Column(String, nullable=True, index=True)
    status = Column(String, default="NORMAL")
    component = Column(String, default="Disjuntor Principal")
    predictive_failure_hours = Column(Integer, default=120)
    recommendation = Column(String, default="Operação nominal estável.")
    esg_waste_kwh = Column(Float, default=1.2)
    assigned_to = Column(String, nullable=True)

class PanelHistoryModel(Base):
    __tablename__ = "panel_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    panel_id = Column(String, index=True, nullable=False)
    tenant_id = Column(String, index=True, nullable=False, default="HITECH-DEFAULT")
    timestamp = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(String, default="HITECH-DEFAULT", index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=False)

class TenantSubscriptionModel(Base):
    __tablename__ = "subscriptions"
    tenant_id = Column(String, primary_key=True, index=True)
    plan_name = Column(String, default="Enterprise")
    status = Column(String, default="ACTIVE")
    expires_at = Column(DateTime, default=datetime.utcnow() + timedelta(days=365))
    max_panels = Column(Integer, default=25)
    webhook_url = Column(String, nullable=True, default="https://httpbin.org/post")

class TenantRuleModel(Base):
    __tablename__ = "tenant_rules"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(String, index=True, nullable=False)
    max_temperature = Column(Float, default=85.0)
    max_current = Column(Float, default=500.0)

class WorkOrderModel(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(String, default="HITECH-DEFAULT", index=True)
    panel_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    priority = Column(String, default="ALTA")
    status = Column(String, default="ABERTA")
    assigned_technician = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)

class InventoryModel(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(String, default="HITECH-DEFAULT", index=True)
    part_name = Column(String, nullable=False)
    category = Column(String, default="Elétrica / Manutenção")
    quantity_in_stock = Column(Integer, default=10)
    min_threshold = Column(Integer, default=3)
    unit_cost = Column(Float, default=150.0)

class AlarmModel(Base):
    __tablename__ = "alarms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, index=True, nullable=False)
    panel_id = Column(String, index=True, nullable=False)
    alarm_type = Column(String, nullable=False)
    severity = Column(String, default="WARNING", nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="ACTIVE", nullable=False)  # ACTIVE, ACKNOWLEDGED, CLEARED
    first_triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    cleared_at = Column(DateTime, nullable=True)


class UserModel(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="CEO")
    tenant_id = Column(String, default="HITECH-DEFAULT")
    plan = Column(String, default="Enterprise")

def validate_webhook_url(value: str) -> str:
    """Permite apenas HTTPS público, sem credenciais, IPs privados ou hosts locais."""
    if not value:
        return ""
    if len(value) > 2048:
        raise HTTPException(status_code=422, detail="URL de webhook demasiado longa.")
    try:
        parsed = urlparse(value)
        port = parsed.port or 443
    except ValueError:
        raise HTTPException(status_code=422, detail="URL de webhook inválida.")
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(status_code=422, detail="O webhook deve ser uma URL HTTPS pública válida.")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost")):
        raise HTTPException(status_code=422, detail="Host local não permitido para webhook.")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    except OSError:
        raise HTTPException(status_code=422, detail="Não foi possível resolver o host do webhook.")
    if not addresses:
        raise HTTPException(status_code=422, detail="Host do webhook sem endereço válido.")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise HTTPException(status_code=422, detail="Webhooks para endereços privados ou especiais não são permitidos.")
    return value

# Instanciação primária da aplicação FastAPI
app = FastAPI(
    title="HITECH VoltGuard SCADA Enterprise",
    description="MVP SaaS de demonstração para monitoramento e manutenção. Não certificado para proteção ou comando industrial.",
    version="0.3.0",
)
limiter = Limiter(key_func=get_remote_address, default_limits=[])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/") or request.url.path == "/health":
        response.headers["Cache-Control"] = "no-store"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/health", tags=["Operations"])
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Banco de dados indisponível.")
    return {"status": "ok", "service": "voltguard", "mode": "simulation" if os.getenv("SIMULATE_TELEMETRY", "0").lower() in {"1", "true", "yes"} else "stored-data"}


# Gestor de Conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str):
        await websocket.accept()
        self.active_connections[websocket] = tenant_id

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    async def broadcast(self, message: dict, tenant_id: str):
        stale = []
        for connection, connection_tenant in list(self.active_connections.items()):
            if connection_tenant != tenant_id:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)

manager = ConnectionManager()

# Funções Utilitárias de Criptografia
def hash_password(password: str) -> str:
    """Hash adaptativo com scrypt, usando apenas a biblioteca padrão."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$%s$%s" % (salt.hex(), digest.hex())

def verify_password(plain_password: str, stored_password: str) -> bool:
    if not stored_password:
        return False
    try:
        if stored_password.startswith("scrypt$"):
            _, salt_hex, digest_hex = stored_password.split("$", 2)
            actual = hashlib.scrypt(plain_password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
            return hmac.compare_digest(actual.hex(), digest_hex)
        # Compatibilidade temporária com hashes SHA-256 antigos; o login migra o hash.
        legacy = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(legacy, stored_password)
    except (ValueError, TypeError):
        return False

# Gestão de Sessões e Inicialização da Base de Dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = SessionLocal()
    try:
        # Compatibility migration for deployments created before panel_history.tenant_id existed.
        # This is deliberately narrow; structural changes beyond this must use a formal migration.
        with engine.begin() as connection:
            inspector = __import__("sqlalchemy").inspect(connection)
            if "panel_history" in inspector.get_table_names():
                columns = {col["name"] for col in inspector.get_columns("panel_history")}
                if "tenant_id" not in columns:
                    connection.execute(text("ALTER TABLE panel_history ADD COLUMN tenant_id VARCHAR"))
                    connection.execute(text("UPDATE panel_history SET tenant_id = COALESCE((SELECT panels.tenant_id FROM panels WHERE panels.id = panel_history.panel_id), 'ORPHANED') WHERE tenant_id IS NULL"))
        Base.metadata.create_all(bind=engine)
        
        # Não criar contas de demonstração com senhas conhecidas. Todas as contas
        # devem ser criadas explicitamente pelo fluxo de cadastro da organização.

        # Fresh installations start empty. The registration flow creates each tenant's
        # subscription, rules, and clearly marked demonstration panels.
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

init_db()

# Esquemas Pydantic
class User(BaseModel):
    username: str
    role: str
    tenant_id: str
    plan: str

class TelemetryData(BaseModel):
    panel_id: str
    temperature: float
    current: float
    voltage: Optional[str] = "380V AC"
    gateway_qr: Optional[str] = None


# Dependência de Autenticação JWT
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        tenant_id = payload.get("tenant_id")
        plan = payload.get("plan")
        if not username or not role or not tenant_id or not plan:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return User(username=username, role=role, tenant_id=tenant_id, plan=plan)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

# --- ROTAS DA API ---

@app.get("/logo.jpg")
def get_logo():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "logo.jpg")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    raise HTTPException(status_code=404, detail="Logo não encontrada.")

@app.post("/api/token")
@limiter.limit("10/minute")
def login(request: Request, credentials: dict, db: Session = Depends(get_db)):
    raw_username = credentials.get("username", "")
    username = raw_username.strip() if isinstance(raw_username, str) else ""
    password = credentials.get("password", "")
    if not isinstance(password, str) or not username or len(username) > 120 or len(password) > 256:
        raise HTTPException(status_code=401, detail="Utilizador ou senha incorretos.")
    
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Utilizador ou senha incorretos.")
    if not db_user.password.startswith("scrypt$"):
        db_user.password = hash_password(password)
        db.commit()
    
    token = jwt.encode({"sub": db_user.username, "role": db_user.role, "tenant_id": db_user.tenant_id, "plan": db_user.plan, "exp": datetime.utcnow() + timedelta(days=1)}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "role": db_user.role, "plan": db_user.plan}

@app.post("/api/tenant/register")
@limiter.limit("5/hour")
def register_tenant(request: Request, data: dict, db: Session = Depends(get_db)):
    raw_tenant = data.get("tenant_id", "")
    raw_user = data.get("username", "")
    tenant_id = raw_tenant.upper().strip() if isinstance(raw_tenant, str) else ""
    admin_user = raw_user.strip() if isinstance(raw_user, str) else ""
    password = data.get("password", "")
    
    if not tenant_id or not admin_user or not isinstance(password, str) or not password.strip():
        raise HTTPException(status_code=400, detail="Dados de registo incompletos.")
    if len(password) < 12:
        raise HTTPException(status_code=400, detail="A senha deve ter pelo menos 12 caracteres.")
    if len(password) > 256:
        raise HTTPException(status_code=422, detail="A senha excede o tamanho permitido.")
    if len(tenant_id) > 80 or len(admin_user) > 120:
        raise HTTPException(status_code=400, detail="Identificador ou utilizador demasiado longo.")
    import re
    if not re.fullmatch(r"[A-Z0-9_-]{2,80}", tenant_id) or not re.fullmatch(r"[A-Za-z0-9_.-]{3,120}", admin_user):
        raise HTTPException(status_code=422, detail="Identificador da organização ou utilizador inválido.")
    if db.query(TenantSubscriptionModel).filter(TenantSubscriptionModel.tenant_id == tenant_id).first():
        raise HTTPException(status_code=409, detail="Esta organização já está registada.")
    
    existing = db.query(UserModel).filter(UserModel.username == admin_user).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nome de utilizador já existe.")
        
    new_user = UserModel(username=admin_user, password=hash_password(password), role="CEO", tenant_id=tenant_id, plan="Piloto")
    db.add(new_user)
    db.add(TenantSubscriptionModel(tenant_id=tenant_id, plan_name="Piloto", status="ACTIVE", max_panels=25, webhook_url=None))
    db.add(TenantRuleModel(tenant_id=tenant_id, max_temperature=85.0, max_current=500.0))

    # Dados explicitamente demonstrativos para que uma organização recém-criada
    # possa avaliar a interface sem conectar equipamentos físicos.
    demo_suffix = secrets.token_hex(3).upper()
    demo_panels = [
        ("01", "Alimentação trifásica — DEMO", "Ambiente simulado", "380 V AC", 118.4, 42.5, "NORMAL", "Valores fictícios para demonstração."),
        ("02", "Carga industrial — DEMO", "Ambiente simulado", "380 V AC", 286.7, 68.2, "NORMAL", "Valores fictícios para demonstração."),
        ("03", "Cenário de alerta — DEMO", "Ambiente simulado", "380 V AC", 515.0, 91.0, "CRITICO", "ALERTA SIMULADO: limites demonstrativos excedidos; não representa condição elétrica real."),
    ]
    for suffix, name, location, voltage, current, temperature, panel_status, recommendation in demo_panels:
        panel_id = f"{tenant_id[:55]}-{demo_suffix}-PANEL-{suffix}"
        panel = PanelModel(
            id=panel_id, tenant_id=tenant_id, name=name, location=location,
            voltage=voltage, current=current, temperature=temperature,
            gateway_qr=f"DEMO-{demo_suffix}-{suffix}", status=panel_status,
            component="Simulador VoltGuard", predictive_failure_hours=0,
            recommendation=recommendation, esg_waste_kwh=0.0,
        )
        db.add(panel)
        db.add(PanelHistoryModel(panel_id=panel_id, tenant_id=tenant_id, timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z", temperature=temperature))

    db.add(AuditLogModel(tenant_id=tenant_id, user_name=admin_user, role="CEO", action="REGISTO_TENANT", details=f"Organização {tenant_id} registada com três painéis demonstrativos."))
    db.commit()
    
    return {"status": "success", "message": f"Organização {tenant_id} criada com sucesso!"}

@app.post("/api/tenant/webhook")
def save_webhook(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "CEO":
        raise HTTPException(status_code=403, detail="Acesso restrito a CEO.")
    webhook_url = validate_webhook_url(str(data.get("webhook_url", "")).strip())
    sub = db.query(TenantSubscriptionModel).filter(TenantSubscriptionModel.tenant_id == current_user.tenant_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura da organização não encontrada.")
    sub.webhook_url = webhook_url or None
    db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="CONFIGURAR_WEBHOOK", details="Webhook atualizado."))
    db.commit()
    return {"status": "success", "message": "Webhook atualizado com sucesso."}

@app.post("/api/tenant/rules")
def update_tenant_rules(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["CEO", "Gerente"]:
        raise HTTPException(status_code=403, detail="Acesso restrito para alterar regras de alarme.")
        
    try:
        max_temp = float(data.get("max_temperature", 85.0))
        max_curr = float(data.get("max_current", 500.0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Os limites devem ser numéricos.")
    import math
    if not math.isfinite(max_temp) or not 0 < max_temp <= 250 or not math.isfinite(max_curr) or not 0 < max_curr <= 100000:
        raise HTTPException(status_code=422, detail="Limites fora dos intervalos permitidos.")
    
    rule = db.query(TenantRuleModel).filter(TenantRuleModel.tenant_id == current_user.tenant_id).first()
    if rule:
        rule.max_temperature = max_temp
        rule.max_current = max_curr
    else:
        db.add(TenantRuleModel(tenant_id=current_user.tenant_id, max_temperature=max_temp, max_current=max_curr))
        
    db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="CONFIGURAR_REGRAS", details=f"Limites alterados: Temp={max_temp}°C"))
    db.commit()
    return {"status": "success", "message": f"Regras de alarme atualizadas para Limite Térmico: {max_temp}°C"}

@app.post("/api/panels/add")
def add_panel(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["CEO", "Gerente"]:
        raise HTTPException(status_code=403, detail="Acesso restrito para adicionar painéis.")
    
    raw_id = data.get("id", "")
    raw_name = data.get("name", "")
    raw_location = data.get("location", "")
    raw_voltage = data.get("voltage", "380V AC")
    raw_component = data.get("component", "Disjuntor Principal")
    raw_qr = data.get("gateway_qr", f"QR-GW-{random.randint(2000,9999)}")
    if not all(isinstance(value, str) for value in (raw_id, raw_name, raw_location, raw_voltage, raw_component, raw_qr)):
        raise HTTPException(status_code=422, detail="Os campos do painel devem ser textos.")
    panel_id = raw_id.strip().upper()
    name = raw_name.strip()
    location = raw_location.strip()
    voltage = raw_voltage.strip()
    component = raw_component.strip()
    gateway_qr = raw_qr.strip()

    if not panel_id or not name or not location:
        raise HTTPException(status_code=400, detail="Preencha os campos obrigatórios do painel.")
    import re
    if not re.fullmatch(r"[A-Z0-9_-]{1,100}", panel_id):
        raise HTTPException(status_code=422, detail="ID deve conter apenas letras, números, hífen e sublinhado.")

    if len(panel_id) > 100 or len(name) > 200 or len(location) > 200 or len(voltage) > 80 or len(component) > 160 or len(gateway_qr) > 160:
        raise HTTPException(status_code=422, detail="Um ou mais campos excedem o tamanho permitido.")
    existing = db.query(PanelModel).filter(PanelModel.id == panel_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Este ID de painel já está em uso. IDs de painéis são globalmente únicos nesta versão.")
    subscription = db.query(TenantSubscriptionModel).filter(TenantSubscriptionModel.tenant_id == current_user.tenant_id).first()
    panel_count = db.query(PanelModel).filter(PanelModel.tenant_id == current_user.tenant_id).count()
    if subscription and panel_count >= subscription.max_panels:
        raise HTTPException(status_code=409, detail="Limite de painéis do plano atingido.")

    new_panel = PanelModel(
        id=panel_id, tenant_id=current_user.tenant_id, name=name, location=location,
        voltage=voltage, current=round(random.uniform(100.0, 400.0), 2),
        temperature=round(random.uniform(45.0, 68.0), 2), gateway_qr=gateway_qr,
        status="NORMAL", component=component, predictive_failure_hours=180,
        recommendation="Painel recém-comissionado. Operação estável.", esg_waste_kwh=1.0
    )
    db.add(new_panel)
    db.add(PanelHistoryModel(panel_id=panel_id, tenant_id=current_user.tenant_id, timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z", temperature=new_panel.temperature))
    db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="ADICIONAR_PAINEL", details=f"Painel {panel_id} adicionado."))
    db.commit()
    return {"status": "success", "message": f"Painel {panel_id} adicionado com sucesso!"}

@app.post("/api/telemetry", tags=["Industrial Ingestion"])
def ingest_telemetry(data: TelemetryData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import math
    if not data.panel_id or len(data.panel_id) > 100:
        raise HTTPException(status_code=422, detail="ID de painel inválido.")
    if not math.isfinite(data.temperature) or not -50 <= data.temperature <= 250:
        raise HTTPException(status_code=422, detail="Temperatura fora do intervalo permitido (-50 a 250 °C).")
    if not math.isfinite(data.current) or not 0 <= data.current <= 100000:
        raise HTTPException(status_code=422, detail="Corrente fora do intervalo permitido (0 a 100000 A).")
    if data.voltage is not None and len(data.voltage) > 80:
        raise HTTPException(status_code=422, detail="Tensão demasiado longa.")
    if data.gateway_qr is not None and len(data.gateway_qr) > 160:
        raise HTTPException(status_code=422, detail="Identificador do gateway demasiado longo.")
    panel = db.query(PanelModel).filter(PanelModel.id == data.panel_id, PanelModel.tenant_id == current_user.tenant_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail=f"Painel {data.panel_id} não encontrado.")
    
    rule = db.query(TenantRuleModel).filter(TenantRuleModel.tenant_id == current_user.tenant_id).first()
    temp_limit = rule.max_temperature if rule else 85.0
    current_limit = rule.max_current if rule else 500.0
    
    panel.temperature = data.temperature
    panel.current = data.current
    if data.voltage:
        panel.voltage = data.voltage
        
    if data.temperature > temp_limit or data.current > current_limit:
        panel.status = "CRITICO"
        reasons = []
        if data.temperature > temp_limit:
            reasons.append(f"temperatura acima de {temp_limit}°C")
        if data.current > current_limit:
            reasons.append(f"corrente acima de {current_limit} A")
        panel.recommendation = "ALERTA: " + " e ".join(reasons) + "."
    else:
        panel.status = "NORMAL"
        panel.recommendation = "Sistema a operar dentro dos parâmetros configurados."
        
    # Alarm lifecycle: one open alarm per panel/type; repeated events update the same record.
    active_conditions = []
    if data.temperature > temp_limit:
        active_conditions.append(("HIGH_TEMPERATURE", "CRITICAL", f"Temperatura {data.temperature} °C acima do limite {temp_limit} °C."))
    if data.current > current_limit:
        active_conditions.append(("HIGH_CURRENT", "CRITICAL", f"Corrente {data.current} A acima do limite {current_limit} A."))
    open_alarms = db.query(AlarmModel).filter(
        AlarmModel.tenant_id == current_user.tenant_id,
        AlarmModel.panel_id == panel.id,
        AlarmModel.status.in_(["ACTIVE", "ACKNOWLEDGED"]),
    ).all()
    active_types = {condition[0] for condition in active_conditions}
    now = datetime.utcnow()
    for alarm_type, severity, message in active_conditions:
        alarm = next((item for item in open_alarms if item.alarm_type == alarm_type), None)
        if alarm:
            alarm.last_triggered_at = now
            alarm.message = message
            alarm.severity = severity
        else:
            db.add(AlarmModel(tenant_id=current_user.tenant_id, panel_id=panel.id, alarm_type=alarm_type, severity=severity, message=message, status="ACTIVE", first_triggered_at=now, last_triggered_at=now))
    for alarm in open_alarms:
        if alarm.alarm_type in {"HIGH_TEMPERATURE", "HIGH_CURRENT"} and alarm.alarm_type not in active_types:
            alarm.status = "CLEARED"
            alarm.cleared_at = now
    db.add(PanelHistoryModel(panel_id=panel.id, tenant_id=current_user.tenant_id, timestamp=now.isoformat(timespec="seconds") + "Z", temperature=panel.temperature))
    db.commit()
    return {"status": "success", "message": f"Telemetria de {data.panel_id} atualizada com base nos limites configurados.", "active_alarms": len(active_conditions)}

@app.post("/api/demo/force-failure")
async def force_failure(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["CEO", "Gerente"]:
        raise HTTPException(status_code=403, detail="Apenas CEO ou Gerente pode executar simulações.")
    raw_panel_id = data.get("panel_id", "")
    panel_id = raw_panel_id.strip() if isinstance(raw_panel_id, str) else ""
    panel = db.query(PanelModel).filter(PanelModel.id == panel_id, PanelModel.tenant_id == current_user.tenant_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="Painel não encontrado.")
    
    panel.status = "CRITICO"
    panel.temperature = 94.5
    panel.predictive_failure_hours = 2
    panel.recommendation = "ALERTA CRÍTICO: Sobreaquecimento extremo detetado!"
    
    db.add(PanelHistoryModel(panel_id=panel.id, tenant_id=current_user.tenant_id, timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z", temperature=panel.temperature))
    db.add(AuditLogModel(
        tenant_id=current_user.tenant_id,
        user_name=current_user.username,
        role=current_user.role,
        action="FORCAR_FALHA",
        details=f"Falha crítica simulada no painel {panel_id}."
    ))
    db.commit()

    sub = db.query(TenantSubscriptionModel).filter(TenantSubscriptionModel.tenant_id == current_user.tenant_id).first()
    if sub and sub.webhook_url:
        try:
            safe_url = validate_webhook_url(sub.webhook_url)
            async with httpx.AsyncClient(follow_redirects=False, timeout=5.0) as client:
                await client.post(safe_url, json={"event": "CRITICAL_ALERT", "panel_id": panel.id, "temperature": panel.temperature, "tenant_id": current_user.tenant_id})
        except Exception:
            # A falha de webhook não deve impedir a gravação do alarme; em produção, registrar em fila/log.
            pass

    await manager.broadcast({"event": "PANEL_UPDATE", "panel_id": panel.id, "status": "CRITICO"}, current_user.tenant_id)
    return {"status": "success", "message": f"Falha crítica simulada com sucesso no cubículo {panel.id}!"}

@app.get("/api/panels")
def get_panels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        panels = db.query(PanelModel).filter(PanelModel.tenant_id == current_user.tenant_id).all()
        
        panels_data = []
        for p in panels:
            curr = p.current
            temp = p.temperature
            if os.getenv("SIMULATE_TELEMETRY", "0").lower() in {"1", "true", "yes"} and p.status != "CRITICO":
                curr = round(max(0.0, p.current + random.uniform(-1.2, 1.2)), 2)
                temp = round(max(-50.0, p.temperature + random.uniform(-0.3, 0.3)), 2)
            
            panels_data.append({
                "id": p.id, "name": p.name, "location": p.location, "voltage": p.voltage,
                "current": curr, "temperature": temp, "gateway_qr": p.gateway_qr,
                "status": p.status, "component": p.component, "predictive_failure_hours": p.predictive_failure_hours,
                "recommendation": p.recommendation, "esg_waste_kwh": p.esg_waste_kwh, "assigned_to": p.assigned_to
            })

        logs = db.query(AuditLogModel).filter(AuditLogModel.tenant_id == current_user.tenant_id).order_by(AuditLogModel.timestamp.desc()).limit(50).all()
        sub = db.query(TenantSubscriptionModel).filter(TenantSubscriptionModel.tenant_id == current_user.tenant_id).first()
        rule = db.query(TenantRuleModel).filter(TenantRuleModel.tenant_id == current_user.tenant_id).first()
        work_orders = db.query(WorkOrderModel).filter(WorkOrderModel.tenant_id == current_user.tenant_id).all()
        inventory = db.query(InventoryModel).filter(InventoryModel.tenant_id == current_user.tenant_id).all()
        alarms = db.query(AlarmModel).filter(AlarmModel.tenant_id == current_user.tenant_id).order_by(AlarmModel.first_triggered_at.desc()).limit(200).all()
        
        history_data = {}
        for p in panels:
            h_records = db.query(PanelHistoryModel).filter(PanelHistoryModel.panel_id == p.id, PanelHistoryModel.tenant_id == current_user.tenant_id).order_by(PanelHistoryModel.id.asc()).all()
            history_data[p.id] = [{"timestamp": h.timestamp, "temperature": h.temperature} for h in h_records]

        logs_data = [{"timestamp": str(l.timestamp), "user_name": l.user_name, "role": l.role, "action": l.action, "details": l.details} for l in logs]
        wo_data = [{"id": w.id, "panel_id": w.panel_id, "title": w.title, "priority": w.priority, "status": w.status, "assigned_technician": w.assigned_technician, "created_at": str(w.created_at), "description": w.description} for w in work_orders]
        inv_data = [{"id": i.id, "part_name": i.part_name, "category": i.category, "quantity_in_stock": i.quantity_in_stock, "min_threshold": i.min_threshold, "unit_cost": i.unit_cost} for i in inventory]
        
        billing_info = {
            "plan_name": sub.plan_name if sub else "Enterprise",
            "status": sub.status if sub else "ACTIVE",
            "expires_at": str(sub.expires_at) if sub else "2027-10-15",
            "max_panels": sub.max_panels if sub else 25,
            "webhook_url": sub.webhook_url if sub else "",
            "max_temperature": rule.max_temperature if rule else 85.0,
            "max_current": rule.max_current if rule else 500.0
        }

        alarm_data = [{"id": a.id, "panel_id": a.panel_id, "alarm_type": a.alarm_type, "severity": a.severity,
                       "message": a.message, "status": a.status, "first_triggered_at": a.first_triggered_at.isoformat() + "Z",
                       "last_triggered_at": a.last_triggered_at.isoformat() + "Z", "acknowledged_at": a.acknowledged_at.isoformat() + "Z" if a.acknowledged_at else None,
                       "acknowledged_by": a.acknowledged_by, "cleared_at": a.cleared_at.isoformat() + "Z" if a.cleared_at else None} for a in alarms]
        return {
            "panels": panels_data, "audit_logs": logs_data, "work_orders": wo_data,
            "inventory": inv_data, "history": history_data, "alarms": alarm_data, "tenant_id": current_user.tenant_id, "billing": billing_info
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Não foi possível carregar os dados do painel.")

@app.get("/api/alarms")
def list_alarms(status_filter: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(AlarmModel).filter(AlarmModel.tenant_id == current_user.tenant_id)
    if status_filter:
        if status_filter not in {"ACTIVE", "ACKNOWLEDGED", "CLEARED"}:
            raise HTTPException(status_code=422, detail="Filtro de estado de alarme inválido.")
        query = query.filter(AlarmModel.status == status_filter)
    return [{"id": a.id, "panel_id": a.panel_id, "alarm_type": a.alarm_type, "severity": a.severity,
             "message": a.message, "status": a.status, "first_triggered_at": a.first_triggered_at.isoformat() + "Z",
             "last_triggered_at": a.last_triggered_at.isoformat() + "Z", "acknowledged_at": a.acknowledged_at.isoformat() + "Z" if a.acknowledged_at else None,
             "acknowledged_by": a.acknowledged_by, "cleared_at": a.cleared_at.isoformat() + "Z" if a.cleared_at else None}
            for a in query.order_by(AlarmModel.first_triggered_at.desc()).limit(500).all()]


@app.post("/api/alarms/{alarm_id}/acknowledge")
def acknowledge_alarm(alarm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alarm = db.query(AlarmModel).filter(AlarmModel.id == alarm_id, AlarmModel.tenant_id == current_user.tenant_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarme não encontrado nesta organização.")
    if alarm.status == "CLEARED":
        raise HTTPException(status_code=409, detail="Um alarme encerrado não pode ser reconhecido.")
    if alarm.status != "ACKNOWLEDGED":
        alarm.status = "ACKNOWLEDGED"
        alarm.acknowledged_at = datetime.utcnow()
        alarm.acknowledged_by = current_user.username
        db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="RECONHECER_ALARME", details=f"Alarme {alarm_id} reconhecido."))
        db.commit()
    return {"status": "success", "id": alarm.id, "alarm_status": alarm.status}


@app.post("/api/alarms/{alarm_id}/clear")
def clear_alarm(alarm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in {"CEO", "Gerente", "Técnico de Campo"}:
        raise HTTPException(status_code=403, detail="Sem permissão para encerrar alarmes.")
    alarm = db.query(AlarmModel).filter(AlarmModel.id == alarm_id, AlarmModel.tenant_id == current_user.tenant_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarme não encontrado nesta organização.")
    if alarm.status != "CLEARED":
        alarm.status = "CLEARED"
        alarm.cleared_at = datetime.utcnow()
        db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="ENCERRAR_ALARME", details=f"Alarme {alarm_id} encerrado manualmente."))
        db.commit()
    return {"status": "success", "id": alarm.id, "alarm_status": alarm.status}


@app.get("/api/panels/qr/{qr_code}")
def get_panel_by_qr(qr_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    panel = db.query(PanelModel).filter(PanelModel.gateway_qr == qr_code, PanelModel.tenant_id == current_user.tenant_id).first()
    if not panel:
        panel = db.query(PanelModel).filter(PanelModel.id == qr_code, PanelModel.tenant_id == current_user.tenant_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="Nenhum cubículo encontrado para este código QR ou ID.")
    return {
        "id": panel.id, "name": panel.name, "location": panel.location, "voltage": panel.voltage,
        "current": panel.current, "temperature": panel.temperature, "gateway_qr": panel.gateway_qr,
        "status": panel.status, "component": panel.component, "predictive_failure_hours": panel.predictive_failure_hours,
        "recommendation": panel.recommendation, "esg_waste_kwh": panel.esg_waste_kwh, "assigned_to": panel.assigned_to
    }

@app.post("/api/inventory/update")
def update_inventory_item(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["CEO", "Gerente"]:
        raise HTTPException(status_code=403, detail="Acesso restrito.")
    
    part_name = data.get("part_name")
    category = data.get("category", "Elétrica")
    raw_qty = data.get("quantity_change", 0)
    raw_min = data.get("min_threshold", 3)
    try:
        qty_change = int(raw_qty)
        unit_cost = float(data.get("unit_cost", 150.0))
        min_threshold = int(raw_min)
    except (TypeError, ValueError, OverflowError):
        raise HTTPException(status_code=422, detail="Quantidade, custo e estoque mínimo devem ser numéricos.")
    if isinstance(raw_qty, float) and not raw_qty.is_integer():
        raise HTTPException(status_code=422, detail="A quantidade deve ser um número inteiro.")
    if isinstance(raw_min, float) and not raw_min.is_integer():
        raise HTTPException(status_code=422, detail="O estoque mínimo deve ser um número inteiro.")
    import math
    if not isinstance(part_name, str) or not part_name.strip() or len(part_name.strip()) > 160:
        raise HTTPException(status_code=422, detail="Nome da peça inválido.")
    if not isinstance(category, str) or len(category.strip()) > 120:
        raise HTTPException(status_code=422, detail="Categoria inválida.")
    part_name = part_name.strip()
    if not math.isfinite(unit_cost):
        raise HTTPException(status_code=422, detail="Custo unitário inválido.")
    if qty_change < 0 and not db.query(InventoryModel).filter(InventoryModel.part_name == part_name, InventoryModel.tenant_id == current_user.tenant_id).first():
        raise HTTPException(status_code=422, detail="Não é possível criar um item com ajuste negativo.")
    if qty_change < -100000 or qty_change > 100000 or min_threshold < 0 or not (0 <= unit_cost <= 100000000):
        raise HTTPException(status_code=422, detail="Quantidade, estoque mínimo ou custo fora dos limites.")

    item = db.query(InventoryModel).filter(InventoryModel.part_name == part_name, InventoryModel.tenant_id == current_user.tenant_id).first()
    if item:
        new_quantity = item.quantity_in_stock + qty_change
        if new_quantity < 0:
            raise HTTPException(status_code=422, detail="O ajuste não pode deixar o estoque negativo.")
        item.quantity_in_stock = new_quantity
        item.unit_cost = unit_cost
        item.min_threshold = min_threshold
        item.category = category.strip()
    else:
        if qty_change < 0:
            raise HTTPException(status_code=422, detail="Não é possível criar item com estoque inicial negativo.")
        db.add(InventoryModel(tenant_id=current_user.tenant_id, part_name=part_name, category=category.strip(), quantity_in_stock=qty_change, min_threshold=min_threshold, unit_cost=unit_cost))
    
    db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="ATUALIZAR_INVENTARIO", details=f"Item {part_name}; ajuste de quantidade {qty_change}."))
    db.commit()
    return {"status": "success", "message": "Inventário atualizado com sucesso!"}

@app.websocket("/ws/panels")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket não aceita OAuth2PasswordBearer automaticamente; token via query string.
    token = websocket.query_params.get("token", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not payload.get("sub") or not tenant_id:
            raise jwt.InvalidTokenError("claims ausentes")
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return
    await manager.connect(websocket, tenant_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/export/executive-report")
def export_executive_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Exporta um relatório CSV real, limitado ao tenant autenticado."""
    import csv
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Relatório Executivo Operacional - HITECH VoltGuard"])
    writer.writerow(["Organização", current_user.tenant_id])
    writer.writerow(["Gerado em UTC", datetime.utcnow().isoformat(timespec="seconds")])
    writer.writerow([])
    writer.writerow(["ID", "Painel", "Local", "Tensão", "Corrente (A)", "Temperatura (°C)", "Estado", "Componente", "Recomendação"])
    panels = db.query(PanelModel).filter(PanelModel.tenant_id == current_user.tenant_id).order_by(PanelModel.id).all()
    for p in panels:
        writer.writerow([p.id, p.name, p.location, p.voltage, p.current, p.temperature, p.status, p.component, p.recommendation])
    writer.writerow([])
    writer.writerow(["Resumo", "Quantidade"])
    writer.writerow(["Total de painéis", len(panels)])
    writer.writerow(["Painéis críticos", sum(1 for p in panels if p.status == "CRITICO")])
    open_orders = db.query(WorkOrderModel).filter(WorkOrderModel.tenant_id == current_user.tenant_id, WorkOrderModel.status.notin_(["CONCLUIDA", "CANCELADA"])).count()
    writer.writerow(["Ordens de serviço abertas", open_orders])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=relatorio_executivo_voltguard.csv"})

class WorkOrderCreate(BaseModel):
    panel_id: str
    title: str
    priority: str = "ALTA"
    description: Optional[str] = None
    assigned_technician: Optional[str] = None

class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_technician: Optional[str] = None
    description: Optional[str] = None

@app.post("/api/work-orders", status_code=201)
def create_work_order(data: WorkOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["CEO", "Gerente", "Técnico de Campo"]:
        raise HTTPException(status_code=403, detail="Sem permissão para criar ordens de serviço.")
    panel_id, title = data.panel_id.strip(), data.title.strip()
    if not panel_id or len(panel_id) > 100 or not title or len(title) > 200:
        raise HTTPException(status_code=422, detail="ID do painel ou título inválido.")
    if data.priority not in {"BAIXA", "MEDIA", "MÉDIA", "ALTA", "CRITICA", "CRÍTICA"}:
        raise HTTPException(status_code=422, detail="Prioridade inválida.")
    if data.description and len(data.description) > 4000:
        raise HTTPException(status_code=422, detail="Descrição demasiado longa.")
    panel = db.query(PanelModel).filter(PanelModel.id == panel_id, PanelModel.tenant_id == current_user.tenant_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="Painel não encontrado nesta organização.")
    order = WorkOrderModel(tenant_id=current_user.tenant_id, panel_id=panel_id, title=title, priority=data.priority, status="ABERTA", assigned_technician=(data.assigned_technician or "").strip() or None, description=data.description)
    db.add(order)
    db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="CRIAR_ORDEM_SERVICO", details=f"Ordem para painel {panel_id}: {title}"))
    db.commit(); db.refresh(order)
    return {"id": order.id, "panel_id": order.panel_id, "title": order.title, "priority": order.priority, "status": order.status, "assigned_technician": order.assigned_technician, "created_at": order.created_at.isoformat(), "description": order.description}

@app.patch("/api/work-orders/{order_id}")
def update_work_order(order_id: int, data: WorkOrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["CEO", "Gerente", "Técnico de Campo"]:
        raise HTTPException(status_code=403, detail="Sem permissão para atualizar ordens de serviço.")
    order = db.query(WorkOrderModel).filter(WorkOrderModel.id == order_id, WorkOrderModel.tenant_id == current_user.tenant_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada.")
    allowed_status = {"ABERTA", "EM_ANDAMENTO", "AGUARDANDO_PECA", "CONCLUIDA", "CANCELADA"}
    if data.status is not None:
        if data.status not in allowed_status:
            raise HTTPException(status_code=422, detail="Estado inválido.")
        order.status = data.status
    if data.priority is not None:
        if data.priority not in {"BAIXA", "MEDIA", "MÉDIA", "ALTA", "CRITICA", "CRÍTICA"}:
            raise HTTPException(status_code=422, detail="Prioridade inválida.")
        order.priority = data.priority
    if data.assigned_technician is not None:
        if len(data.assigned_technician) > 120:
            raise HTTPException(status_code=422, detail="Nome do técnico demasiado longo.")
        order.assigned_technician = data.assigned_technician.strip() or None
    if data.description is not None:
        if len(data.description) > 4000:
            raise HTTPException(status_code=422, detail="Descrição demasiado longa.")
        order.description = data.description
    db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_name=current_user.username, role=current_user.role, action="ATUALIZAR_ORDEM_SERVICO", details=f"Ordem {order_id} atualizada; estado={order.status}."))
    db.commit()
    return {"status": "success", "id": order.id, "order_status": order.status}

@app.get("/")
def serve_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "index.html")
    if not os.path.exists(index_path):
        index_path = os.path.join(base_dir, "index (3).html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail=f"index.html não encontrado no caminho: {index_path}")
