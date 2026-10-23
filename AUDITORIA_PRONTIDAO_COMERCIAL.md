# Auditoria de prontidão — HITECH VoltGuard

**Atualização:** 23/10/2026
**Escopo:** código da branch de prontidão, deploy do piloto no Render e observações do banco registradas na auditoria inicial de 22/10.
**Resultado:** o piloto está acessível, mas ainda não está pronto para produção comercial nem para receber dados operacionais reais.

## Bloqueios prioritários

### P0 — Confirmar e corrigir o banco usado pelo serviço

- O PostgreSQL `voltguard-db` (`dpg-db9as5gn74is73f2felg-a`) está disponível, mas a consulta somente leitura a `pg_tables` não encontrou tabela alguma.
- Os logs da aplicação no mesmo ambiente registram cadastro de organização e autenticação com HTTP 200. O app cria as tabelas na inicialização, portanto esses fatos não combinam com o app gravando nesse PostgreSQL vazio.
- A auditoria inicial não conseguiu confirmar a variável `DATABASE_URL` no serviço nem localizar tabelas no PostgreSQL consultado.
- O código da branch agora encerra a inicialização no Render se `DATABASE_URL` estiver ausente ou apontar para SQLite. O deploy atual do piloto iniciou, o que indica que a proteção de banco passou, mas não confirma qual banco contém os dados anteriores nem a persistência/expiração do destino.
- O banco PostgreSQL atual está no plano Free, com expiração informada para **15/11/2026**. O serviço web também está no plano Free. O Render documenta que o sistema de arquivos de serviços Free é efêmero, inclusive para SQLite, e que bancos PostgreSQL Free expiram após 30 dias. Esses planos são destinados a teste, não à produção ([limitações do plano Free do Render](https://render.com/docs/free)).
- Existem dois serviços Render para este repositório: `Hitech-VoltGuard` em `main` e `voltguard-pilot-free` na branch de revisão. O primeiro continua servindo o endereço histórico, com deploy por commit e sem health check; o segundo contém a revisão e está configurado para aguardar CI. Ainda não houve promoção para `main`.

**Ação para liberar:** no Dashboard, confirmar a origem efetiva de `DATABASE_URL` sem copiar o segredo para o chat; vincular o serviço ao PostgreSQL correto; migrar para plano persistente antes de 15/11; fazer backup/exportação e validar uma restauração; só então reiniciar/deployar. Antes de decidir qual banco usar, preservar qualquer dado existente no serviço.

### P0 — Tornar o health check HTTP efetivo

- A configuração inicial do serviço estava sem `healthCheckPath`; `/health` foi definido no Render em 23/10 e o deploy da configuração concluiu como `live`.
- A rota implementa `SELECT 1` e responde erro se o banco não responder. A URL pública `/health` retornou HTTP 200 com `{"status":"ok","service":"voltguard","mode":"stored-data"}` após a configuração e novamente depois do deploy do código `a13252d`. A página pública de login também foi conferida.
- O modo automático de deploy do Render foi alterado de `On Commit` para `After CI Checks Pass`; a próxima revisão só será publicada após os checks configurados no GitHub passarem.

**Ação para liberar:** validar novamente `/health` depois do deploy do código revisado e confirmar que `DATABASE_URL` aponta para o PostgreSQL persistente correto; `SELECT 1` confirma conexão, mas não identidade nem histórico do banco.

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
- O cadastro de ativos não cria medições aleatórias nem histórico fictício; leituras parciais ficam identificadas e não são exibidas como estado normal.
- Login de contas com MFA habilitado exige segundo fator. Cadastro público fecha por padrão e só abre com `ALLOW_SELF_SERVICE_REGISTRATION=1` configurado explicitamente.
- Health check HTTP `/health` configurado e respondendo no serviço piloto Render, além da configuração declarada no Blueprint.
- Deploy do serviço configurado para aguardar CI do GitHub. O commit `a13252d` passou no workflow (incluindo `pip-audit` e 20 testes de integração) e está `live` no Render.

## Ordem sugerida de liberação

1. Identificar sem ambiguidade o banco que contém os dados atuais e corrigir o vínculo antes de qualquer reinício.
2. Migrar o banco e o serviço para recursos persistentes e configurar backup/restauração.
3. Manter o health check HTTP `/health` e validar a próxima revisão em homologação.
4. Fechar onboarding, recuperação de conta, privacidade, suporte e cobrança.
5. Validar hardware/protocolo e isolamento industrial com piloto pago e métricas de sucesso acordadas.
6. Só então habilitar clientes de produção e anunciar métricas/benefícios que tenham evidência.

## Limites desta auditoria

Esta revisão não substitui revisão independente de segurança, validação em medidor físico, assessoria jurídica/tributária ou confirmação do vínculo e da persistência de `DATABASE_URL` no painel do Render. Não foram alterados recursos pagos, segredos ou banco de dados. O Render foi configurado para verificar `/health` e aguardar o CI do GitHub antes de publicar.
