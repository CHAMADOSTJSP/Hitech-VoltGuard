# Auditoria de prontidão — HITECH VoltGuard

**Data:** 22/10/2026  
**Escopo:** código disponível no workspace, configuração do serviço `Hitech-VoltGuard` no Render, estado do PostgreSQL associado e logs recentes.  
**Resultado:** o aplicativo está acessível, mas não está pronto para produção comercial nem para receber dados operacionais reais.

## Bloqueios prioritários

### P0 — Confirmar e corrigir o banco usado pelo serviço

- O PostgreSQL `voltguard-db` (`dpg-db9as5gn74is73f2felg-a`) está disponível, mas a consulta somente leitura a `pg_tables` não encontrou tabela alguma.
- Os logs da aplicação no mesmo ambiente registram cadastro de organização e autenticação com HTTP 200. O app cria as tabelas na inicialização, portanto esses fatos não combinam com o app gravando nesse PostgreSQL vazio.
- `main.py` escolhe `sqlite:///./voltguard.db` quando `DATABASE_URL` não está definida. A configuração atual do serviço não mostrou a variável no resultado de `get_service`; não foi possível confirmar qual banco o processo usa.
- Nesta revisão, foi adicionada à branch uma verificação de inicialização que recusa ausência de `DATABASE_URL` e SQLite no Render. A alteração precisa ser aplicada somente depois de confirmar PostgreSQL persistente, caso contrário o novo deploy falhará com segurança.
- O banco PostgreSQL atual está no plano Free, com expiração informada para **15/11/2026**. O serviço web também está no plano Free. O Render documenta que o sistema de arquivos de serviços Free é efêmero, inclusive para SQLite, e que bancos PostgreSQL Free expiram após 30 dias. Esses planos são destinados a teste, não à produção ([limitações do plano Free do Render](https://render.com/docs/free)).

**Ação para liberar:** no Dashboard, confirmar a origem efetiva de `DATABASE_URL` sem copiar o segredo para o chat; vincular o serviço ao PostgreSQL correto; migrar para plano persistente antes de 15/11; fazer backup/exportação e validar uma restauração; só então reiniciar/deployar. Antes de decidir qual banco usar, preservar qualquer dado existente no serviço.

### P0 — Tornar o health check HTTP efetivo

- O serviço Render retornou `healthCheckPath` vazio, embora `render.yaml` defina `/health` e `main.py` implemente a rota.
- Sem esse caminho, o Render não verifica se o app consegue atender uma rota HTTP nem se o banco está acessível; a configuração observada usa apenas a checagem TCP padrão. O Render permite configurar uma checagem HTTP para validar disponibilidade da aplicação ([Health Checks](https://render.com/docs/health-checks)).

**Ação para liberar:** aplicar `/health` no serviço atual e confirmar que a rota falha quando o banco de aplicação não estiver acessível. A rota atual faz `SELECT 1`, mas não identifica se o banco correto é o usado pelo app.

## Lacunas de produto e operação

### P1 — Cobrança e ciclo comercial

- A tela de assinatura declara que pagamentos, alteração de plano e cancelamento não são processados.
- A assinatura é apenas metadado no banco; não há provedor de pagamento, webhook de cobrança, renovação, inadimplência, cancelamento ou bloqueio de recursos por plano.
- Planos e preço ainda dependem de pilotos e cálculo de custo de implantação, gateway, conectividade, cloud e suporte.

**Ação:** definir mercado inicial e modelo de cobrança com pilotos pagos; então escolher provedor, regras de plano, emissão fiscal, cancelamento e tratamento de falhas antes de implementar o fluxo de pagamento.

### P1 — Identidade e atendimento ao cliente

- O cadastro de organização é público e cria contas CEO sem confirmação de e-mail; há limite de taxa, mas não há verificação de domínio/identidade, convites ou aprovação comercial.
- Não há recuperação de senha por e-mail. A recuperação administrativa depende de suporte fora do fluxo do produto.
- Não há política implementada de retenção, exportação e exclusão de dados da organização, termos, aviso de privacidade, SLA nem processo de resposta a incidentes.

**Ação:** definir o processo de onboarding e recuperação; incluir os fluxos de e-mail verificado/convite e suporte; formalizar privacidade, retenção e atendimento antes de clientes reais.

### P1 — Dados e integração industrial

- Novas organizações recebem painéis fictícios de demonstração. Alguns indicadores antigos do dashboard eram números fixos e sem origem operacional; foram substituídos nesta revisão por contagens baseadas na API.
- `gateway.py` implementa um coletor Modbus configurável, mas o mapa de registradores depende do equipamento e firmware. Não há homologação física do PM5320 nem validação laboratorial documentada.
- A conectividade significa atividade recente da credencial/API, não disponibilidade garantida do medidor ou do circuito. Os indicadores preditivos e ESG ainda não devem ser vendidos como previsões ou medições validadas.
- O produto é monitoramento e apoio à manutenção. Não é sistema certificado de proteção, comando, intertravamento ou conformidade normativa.

**Ação:** separar claramente demonstração de produção; escolher medidores e gateway do piloto; validar leituras, qualidade, stale data, reconexão e alarmes em laboratório e depois em piloto controlado, sem conectar o VoltGuard a funções de proteção/comando.

### P1 — Confiabilidade e segurança de produção

- `init_db()` usa `create_all()` e ajustes de compatibilidade específicos; ainda não há migrações versionadas com rollback.
- Não há evidência registrada de restauração de backup testada, monitoramento/alertas operacionais, teste de carga, revisão independente de segurança ou testes de isolamento completos de todos os endpoints.
- O rate limit é local por processo sem Redis. A arquitetura atual do serviço tem uma instância, mas limites globais serão necessários ao escalar.
- Webhooks são síncronos, sem fila durável, política de repetição ou monitoramento de entrega.

**Ação:** adicionar migrações formais, backup e restauração ensaiados, alertas, testes de segurança/isolamento e observabilidade; mover entregas externas para fila durável quando a operação exigir garantias.

## Melhorias feitas nesta revisão local

- Removidos KPIs fixos de risco, downtime, confiabilidade, ESG, MTTR e disponibilidade que não eram calculados a partir de dados reais.
- O cabeçalho agora mostra painéis cadastrados, painéis online, alarmes ativos/reconhecidos e ordens em aberto, atualizados com o polling do painel.
- Adicionada proteção para impedir que uma configuração do Render sem `DATABASE_URL` use o SQLite descartável como se fosse persistente.

## Ordem sugerida de liberação

1. Identificar sem ambiguidade o banco que contém os dados atuais e corrigir o vínculo antes de qualquer reinício.
2. Migrar o banco e o serviço para recursos persistentes e configurar backup/restauração.
3. Configurar o health check HTTP e validar o conjunto completo em homologação.
4. Fechar onboarding, recuperação de conta, privacidade, suporte e cobrança.
5. Validar hardware/protocolo e isolamento industrial com piloto pago e métricas de sucesso acordadas.
6. Só então habilitar clientes de produção e anunciar métricas/benefícios que tenham evidência.

## Limites desta auditoria

Esta revisão não substitui revisão independente de segurança, validação em medidor físico, assessoria jurídica/tributária ou confirmação do vínculo de `DATABASE_URL` no painel do Render. Não foram alterados recursos pagos, segredos, banco de dados ou configuração do serviço ao vivo. Não foram executados testes automatizados.
