# HITECH VoltGuard SCADA Enterprise — pacote Render

Este pacote prepara o protótipo existente para **demonstração/homologação na nuvem**. Ainda não deve ser tratado como SCADA industrial validado ou como plataforma pronta para receber dados críticos de clientes.

## O que foi preparado

- `render.yaml`: Blueprint do Render para criar o serviço web e um PostgreSQL.
- `main.py`: FastAPI, suporte a PostgreSQL/psycopg, verificação de saúde com banco e criação de dados demonstrativos por organização.
- `index.html`: remove usuário/senha predefinidos e usa autenticação no download do CSV.
- `requirements.txt`: dependências, incluindo driver PostgreSQL.
- `Dockerfile`: alternativa de execução em contêiner.
- `tests/test_render_smoke.py`: testes básicos de saúde, cadastro/login, separação dos dados de duas organizações e autenticação do relatório.

## Implantação pelo GitHub + Render

1. Extraia o ZIP.
2. Crie um repositório **privado** no GitHub e envie todos os arquivos e pastas do pacote para a raiz do repositório.
3. No Render, escolha **New + → Blueprint** e conecte o repositório.
4. Confira os recursos que o `render.yaml` vai criar e aplique o Blueprint.
5. Aguarde o deploy. O Render gera `SECRET_KEY` e conecta o serviço ao PostgreSQL declarado no Blueprint.
6. Abra o domínio `onrender.com` gerado pelo Render e confirme que `/health` retorna `{"status":"ok", ...}`.
7. Na tela inicial, use **Registar Nova Empresa**. Cadastre um ID de organização, um usuário e uma senha com pelo menos 10 caracteres; depois faça login.
8. Os três painéis iniciais são explicitamente demonstrativos. Não são leituras de medidores reais.

## Atenção ao plano gratuito

O `render.yaml` usa o plano gratuito para reduzir custo de avaliação. Conforme a documentação atual do Render, o PostgreSQL gratuito expira após 30 dias e tem limite de 1 GB. **Não armazene dados reais nem aceite clientes pagantes com esse banco.** Antes de piloto comercial, altere o banco para um plano persistente pago no painel Render e confirme backups/restauração. O serviço web gratuito também pode entrar em suspensão após inatividade.

Se não quiser usar o Blueprint, crie um Web Service Python manualmente:

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`
- `SECRET_KEY`: chave aleatória com pelo menos 32 caracteres, salva como secret no Render.
- `DATABASE_URL`: URL interna do PostgreSQL Render; nunca a publique no repositório.
- `ENABLE_DEMO_USERS=0`
- `SIMULATE_TELEMETRY=0`

## Testar localmente antes de publicar

Requer Python 3.12.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
uvicorn main:app --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000`.

## Limitações importantes antes de uso comercial

Este pacote é um **candidato a demonstração**, não uma aprovação de produção. Antes de colocar dados de clientes reais:

- Faça revisão de segurança independente e teste de penetração.
- Adicione migrações de banco formais (Alembic); `create_all()` não migra automaticamente tabelas antigas. Use banco novo para esta primeira implantação.
- Valide a autorização multiempresa em todas as rotas e teste de regressão após cada mudança.
- Planeje recuperação de senha, MFA para administradores, gestão de sessões, auditoria e retenção de dados.
- Teste backup e restauração do PostgreSQL e configure monitoramento/alertas.
- O limitador de tentativas de login/cadastro deste pacote usa armazenamento em memória por processo; não substitui limitação distribuída/WAF em escala.
- A telemetria ainda não é uma integração industrial real. Antes de conectar medidores, implemente identidade individual por dispositivo, autenticação, proteção contra repetição, fila/reconexão, mapeamento de registradores documentado e rede de aquisição isolada.
- Não conecte o sistema a funções de comando, proteção ou intertravamento elétrico. O escopo atual é demonstração/monitoramento.
- Valores de tendência preditiva, ESG e outros campos demonstrativos não devem ser anunciados como análises validadas.

## Referência

A configuração segue a documentação do Render para Blueprints, serviços web e variáveis de ambiente: https://render.com/docs/blueprint-spec, https://render.com/docs/web-services e https://render.com/docs/configure-environment-variables.
