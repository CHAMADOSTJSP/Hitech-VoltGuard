# Revisão técnica — HITECH VoltGuard SCADA Enterprise

## Escopo e conclusão

Esta entrega organiza e endurece o MVP para **demonstração/homologação controlada** no Render. Não representa certificação, pentest independente, conformidade normativa nem prontidão para uso industrial crítico.

## Melhorias aplicadas nesta revisão

- v0.46.0: removidos os eventos inline da tela de autenticação, com delegação no JavaScript externo; as alternâncias entre login e cadastro passaram a botões acessíveis por teclado. Handlers nas telas dinâmicas e estilos inline ainda impedem uma CSP estrita.
- v0.45.0: script principal extraído para `app.js`, servido pelo FastAPI com `Cache-Control: no-store` e incluído na imagem Docker. A CSP restritiva permanece pendente porque ainda existem handlers e estilos inline.
- Nomes de arquivos padronizados para coincidir com os caminhos esperados pelo Render e Dockerfile.
- Cabeçalhos HTTP básicos, política `no-store` para respostas de API/health e política de permissões para recursos do navegador.
- Hash de senhas com scrypt e migração de hashes SHA-256 legados no login.
- `SECRET_KEY` configurável; o Render deve fornecer um segredo estável e aleatório.
- Validação de senha de cadastro com mínimo de 12 caracteres, limites de comprimento e validação de identificadores.
- Rate limiting de login e cadastro por processo, usando SlowAPI; não é rate limiting distribuído.
- Filtros por organização nas consultas de painéis, ordens, auditoria, inventário e histórico.
- Adicionado `tenant_id` ao histórico de painéis, incluindo uma migração de compatibilidade estreita para bancos anteriores.
- Timestamps de novos registros de histórico passam a incluir data/hora completa em formato ISO.
- Validação numérica de telemetria, limites térmicos e de corrente.
- Proteção contra ajuste de estoque abaixo de zero e tratamento de entradas numéricas inválidas.
- Validação HTTPS e bloqueio inicial de destinos locais/privados para webhooks; redirects automáticos desativados no envio.
- Relatório CSV protegido por autenticação e limitado à organização autenticada.
- Interface ajustada para telas menores e identificação explícita de que relatório e painéis demonstrativos não certificam conformidade NR-10.
- Botões de simulação de falha não interpolam o ID do painel em código JavaScript inline.
- Testes básicos adicionados para health check, cabeçalhos, cadastro/login, isolamento entre organizações, inventário e autenticação do relatório.

## Limitações e pendências antes de produção

### Segurança e identidade

1. Realizar revisão de segurança independente e teste de penetração.
2. Remover os demais manipuladores inline e rever todos os pontos de inserção via `innerHTML`; preferir `textContent`, criação de nós DOM e escape contextual.
3. Implementar Content Security Policy (CSP) depois de eliminar scripts e eventos inline.
4. Implementar MFA para administradores, recuperação segura de senha, revogação de sessões/tokens, gestão de usuários e política de bloqueio/alerta.
5. Migrar rate limiting para armazenamento compartilhado/edge ou WAF se houver múltiplas instâncias.
6. Limitar conexões WebSocket, acompanhar falhas de autenticação e considerar um transporte de credencial fora da URL para ambientes de produção.
7. O webhook ainda pode estar sujeito a DNS rebinding/TOCTOU entre validação e conexão. Para produção, usar worker isolado, política de saída de rede, destinos permitidos e logs/retries controlados.
8. Rever a política de CORS, cookies/sessões (se forem introduzidos), CSP e configuração de proxy/HTTPS de acordo com o ambiente.

### Controles implementados na versão 0.41.0

- Tokens de acesso expiram em 8 horas.
- A autorização HTTP usa o usuário atual do banco para obter papel, organização e plano; exclusão e mudança de papel/organização têm efeito imediato sobre tokens já emitidos.
- WebSocket usa ticket opaco de uso único, armazenado como hash e válido por 30 segundos. O ticket é consumido atomicamente e a origem do navegador precisa corresponder à origem do serviço.
- O frontend ainda não usa WebSocket. O ticket curto reduz o impacto de registros de URL, mas não remove completamente o segredo da URL; limitar conexões e monitorar tentativas continua pendente.

### Controles implementados na versão 0.43.0

- Cada login recebe um identificador de sessão aleatório; somente seu hash e validade são persistidos.
- A autorização verifica a sessão ativa em cada requisição autenticada. O endpoint `/api/logout` revoga a sessão atual, e a interface limpa o token e interrompe o polling.
- A atualização invalida tokens emitidos antes da adoção do identificador de sessão; a interface solicita novo login. MFA, encerramento remoto de todas as sessões e alertas de atividade continuam pendentes.

### Controles implementados na versão 0.44.0

- A ingestão de dispositivo limita 600 requisições por minuto por endereço IP usando SlowAPI.
- A rota recusa requisições que declarem `Content-Length` maior que 16 KB antes do processamento do corpo.
- O modelo de telemetria rejeita campos desconhecidos e limita os tamanhos de `panel_id`, `voltage` e `gateway_qr`.
- O rate limiting é em memória por processo e compartilhado por todos os dispositivos que chegam do mesmo IP. Para múltiplas instâncias, adotar armazenamento distribuído e uma política dimensionada por credencial.

### Banco e multiempresa

1. `PanelModel.id` ainda é chave primária global. A aplicação não permite reutilizar o mesmo ID em duas organizações. Alterar para chave composta exige migração estrutural e testes de regressão.
2. A coluna `tenant_id` foi adicionada ao histórico e as consultas filtram por organização. Validar a migração com cópia de banco e backup antes de atualizar bases persistentes antigas.
3. A migração de compatibilidade em `init_db()` cobre apenas a coluna `panel_history.tenant_id`; não substitui Alembic para futuras mudanças estruturais.
4. Adicionar testes negativos para cada endpoint que lê ou altera painéis, inventário, regras, auditoria, ordens, webhooks e relatórios.
5. Criar histórico de movimentação de estoque, constraints/índices apropriados, transações robustas e testes de concorrência. A validação de saldo negativo já foi adicionada, mas concorrência precisa ser testada em PostgreSQL.
6. Completar trilha de auditoria para todas as operações administrativas e definir retenção, exportação e exclusão.

### Telemetria e operação

1. A ingestão já usa credenciais individuais por dispositivo, armazenadas como hash, com vínculo a um único painel e possibilidade de revogação. Permanecem pendentes rotação planejada, timestamps de origem confiáveis, idempotência, rate limiting distribuído por credencial e métricas de qualidade.
2. Não existe integração pronta com PLCs/medidores físicos. Definir equipamentos e protocolos (p. ex. Modbus TCP/RTU ou OPC UA), validar em laboratório e separar a rede de aquisição.
3. Criar detecção de equipamento offline, limites de stale data, reconexão, fila de eventos e observabilidade.
4. Previsão de falhas, ESG e KPIs demonstrativos não devem ser anunciados como medições ou previsões validadas.
5. Cobrança é metadado, sem gateway de pagamento, renovação ou gestão de inadimplência.
6. Configurar backup e restauração do PostgreSQL, logs estruturados, alertas e plano de resposta a incidentes.
7. Executar testes de carga, navegador multiplataforma e testes de recuperação antes de um piloto.

## Conformidade e segurança industrial

Não declarar conformidade com NR-10, IEC 62443, LGPD ou qualquer certificação industrial com base nesta entrega. A LGPD depende do tratamento real de dados pessoais e das operações da organização; requisitos de segurança industrial dependem da arquitetura, análise de risco, controles e validação profissional. Não conectar a aplicação a funções de comando, proteção ou intertravamento elétrico.

## Critérios mínimos de liberação para piloto com dados reais

- [ ] Revisão de segurança e autorização multiempresa concluída.
- [ ] Testes automatizados executados no ambiente equivalente ao de produção.
- [ ] Migração de banco revisada, backup feito e restauração testada.
- [ ] Segredos e acessos administrativos configurados com privilégio mínimo.
- [ ] Política de retenção, privacidade, resposta a incidentes e suporte definida.
- [ ] Fonte e confiabilidade de cada leitura claramente identificadas.
- [ ] Telemetria industrial validada em laboratório e isolada de sistemas de proteção/comando.

## Atualização técnica v0.4.0

### Melhorias implementadas nesta rodada
- Central de Alarmes com persistência no banco, severidade, estado, primeira/última ocorrência, reconhecimento e encerramento.
- Alarmes de temperatura e corrente são gerados a partir da telemetria autenticada e dos limites configurados pela organização.
- Repetições atualizam o alarme aberto existente do mesmo tipo para o painel, evitando criar uma nova linha a cada leitura.
- Quando uma leitura posterior volta aos limites, o alarme correspondente é encerrado automaticamente. O encerramento manual permanece disponível para usuários autorizados.
- Endpoints de listagem, reconhecimento e encerramento filtram por `tenant_id`; ações manuais geram trilha de auditoria.
- A interface ganhou a aba Central de Alarmes.

### Referências de produto usadas como inspiração funcional
A organização de dispositivos/ativos, dashboards, telemetria e alarmes segue padrões públicos encontrados na documentação do ThingsBoard. O código e a interface foram implementados especificamente para este projeto, sem copiar código proprietário.

### Limitações que continuam abertas
- O painel ainda inclui métricas e ativos de demonstração; valores simulados não devem ser interpretados como medições de campo.
- Não foi implementado driver físico Modbus TCP/OPC UA nem provisionamento de credenciais independentes por dispositivo nesta rodada.
- Notificações externas de alarmes exigem configuração e testes próprios; webhook não substitui um sistema de entrega confiável.
- O controle de assinaturas ainda não processa pagamentos reais.
- A versão não é certificada para comando/proteção de instalações industriais e não declara conformidade automática com NR-10, IEC 62443 ou LGPD.
- A migração atual de banco continua limitada; para mudanças de esquema futuras, adotar Alembic e processo de backup/rollback.


## Revisão adicional — versão 0.5.0

Implementados cadastro de ativos, planos/tarefas de manutenção e credenciais próprias de dispositivos. As credenciais são armazenadas como hashes e podem ser revogadas; a ingestão autenticada valida que o token só escreve no painel vinculado. A recorrência é orientada à conclusão da tarefa e não depende de um scheduler.

Antes de produção: usar migrações formais (Alembic), limitar taxa distribuída, testar restauração/backup, revisar WebSocket e CSP/XSS, adicionar notificações com entrega monitorada, realizar testes de carga e revisão independente de segurança. Nenhuma integração Modbus/OPC UA ou certificação de segurança funcional está incluída.


## Atualização v0.5.3

- Adicionado estado derivado de conectividade para credenciais de dispositivo: `NOT_CONFIGURED`, `NEVER_CONNECTED`, `ONLINE`, `OFFLINE`. O cálculo usa `DeviceCredential.last_used_at` e exclui credenciais revogadas.
- `DEVICE_OFFLINE_AFTER_SECONDS` controla o limiar de inatividade (padrão 300 s, limitado a 30–86400 s).
- Adicionado endpoint autenticado `GET /api/telemetry/history/{panel_id}` com paginação por ID e validação de tenant.
- O endpoint agregado `/api/panels` limita histórico a 500 amostras mais recentes por painel.
- Testes cobrem paginação, limites, isolamento entre tenants e estados de conectividade.
- Limitação: isto indica atividade da credencial/API, não confirma disponibilidade física do PLC/rede; um gateway pode enviar telemetria enquanto o equipamento de campo está inacessível.
