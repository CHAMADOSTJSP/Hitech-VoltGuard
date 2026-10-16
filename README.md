# HITECH VoltGuard SCADA Enterprise — revisão funcional

Esta pasta contém uma revisão de trabalho do protótipo original. O objetivo é facilitar execução local e testes controlados, não declarar conformidade regulatória ou aptidão para operar equipamentos elétricos críticos.

## Requisitos
- Python 3.10+ (recomendado 3.12)
- Navegador moderno
- Para execução local, SQLite é usado por padrão

## Executar no Windows (PowerShell)
```powershell
cd voltguard_revisado
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:DATABASE_URL = "sqlite:///./voltguard.db"
uvicorn main:app --host 127.0.0.1 --port 8000
```
Abra `http://127.0.0.1:8000`. Documentação da API: `http://127.0.0.1:8000/docs`; verificação de saúde: `/health`.

## Executar no Linux/macOS
```bash
cd voltguard_revisado
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DATABASE_URL="sqlite:///./voltguard.db"
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Importante:** use uma `SECRET_KEY` persistente e gerenciada com segurança no ambiente que você pretende manter. Se a chave for gerada novamente, os tokens anteriores deixam de funcionar. Não publique a aplicação diretamente na internet sem proxy HTTPS, limitação de tentativas de login/cadastro, monitoramento e revisão de segurança.

## Primeiro acesso
1. Abra a página inicial.
2. Use a opção de cadastro para criar uma organização e um usuário administrador.
3. A senha deve ter pelo menos 10 caracteres.
4. Entre com a conta criada. O banco SQLite será criado automaticamente.

As contas de demonstração com senha conhecida não são criadas por padrão. Para habilitá-las apenas num ambiente local descartável, defina `ENABLE_DEMO_USERS=1`; as contas usam senha `123456` e nunca devem ser usadas em produção.

## Simulação e telemetria
- `SIMULATE_TELEMETRY=0` por padrão: a API não inventa flutuações a cada leitura; apresenta os valores armazenados.
- `SIMULATE_TELEMETRY=1`: habilita pequenas variações demonstrativas para painéis não críticos.
- `POST /api/telemetry` aceita telemetria autenticada por usuário nesta versão. Isso **não é uma identidade adequada para dispositivos industriais em produção**. Antes de conectar equipamentos reais, implemente credenciais por dispositivo, timestamps, proteção contra repetição, limites de taxa e validação de protocolo.
- A função de simular falha é uma ferramenta de demonstração e só está disponível para CEO/Gerente.

## Funcionalidades revisadas
- Hash de senha com scrypt e migração de hashes SHA-256 antigos após login bem-sucedido.
- Chave JWT sem segredo fixo no código.
- Validação de cadastro, regras de alarme, IDs e entradas de telemetria.
- Alarmes por temperatura e corrente.
- WebSocket autenticado com envio limitado ao tenant da conexão.
- Validação inicial de URL de webhook (HTTPS, host público, sem redirect automático); ainda exige revisão de segurança dedicada antes de exposição pública.
- Gestão de ordens de serviço: criação e atualização de estado, com registro de auditoria.
- Relatório executivo CSV com dados do tenant autenticado.
- Validações no inventário e registro de auditoria.
- Cabeçalhos HTTP básicos de segurança e endpoint `/health`.
- Interface escapa diversos valores dinâmicos antes de inserir HTML.

## Testes executados nesta revisão
```bash
python -m py_compile main.py
python -m unittest discover -s tests -v
```
Também foi feito um teste de integração local com SQLite temporário para cadastro, login, leitura de painéis, criação de painel, ingestão de telemetria, criação de ordem de serviço e exportação CSV. Esses testes não substituem teste de navegador, carga, pentest ou validação industrial.

## Limitações conhecidas — não apresentar como pronto para indústria
1. A chave primária de painel continua global (`PanelModel.id`); duas organizações não podem reutilizar o mesmo ID. A migração para chave composta ou ID interno é necessária.
2. A tabela de histórico não tem `tenant_id`; o isolamento atual depende de IDs de painéis globalmente únicos. Migração de esquema e testes de isolamento completos continuam necessários.
3. A validação de webhook reduz risco de SSRF, mas não elimina todos os cenários de DNS rebinding/TOCTOU. Recomenda-se saída de rede restrita, worker dedicado e revisão de segurança antes de habilitar em produção.
4. Não há migrações Alembic; `create_all` não atualiza automaticamente esquemas existentes. Faça backup antes de mudanças e planeje migrações formais.
5. Rate limiting de login/cadastro, recuperação de senha, MFA, gestão de sessão e política formal de retenção não estão implementados.
6. O sistema não tem integração real com PLC/medidores, protocolos industriais, identidade de dispositivo, fila durável de eventos ou monitoramento de perda de comunicação.
7. Previsão de falhas e indicadores ESG ainda são dados estáticos/demonstrativos; não são modelos preditivos ou medições certificadas.
8. Faturamento/assinaturas são metadados; não há gateway de pagamento ou processo de cobrança real.
9. Inventário não tem trilha detalhada de movimentações por item e ainda precisa de controles transacionais mais rigorosos.
10. Esta revisão não comprova conformidade com NR-10, IEC 62443, LGPD ou qualquer certificação. A conformidade depende de escopo, implantação, processos, avaliação profissional e evidências.

## Aviso operacional
Use apenas em desenvolvimento ou laboratório/simulador. Não use este protótipo para comando, intertravamento, proteção elétrica ou decisões críticas de segurança. Antes de piloto com cliente, faça revisão independente de segurança, avaliação de riscos, backups/restauração, testes de falha e validação com profissional habilitado.
