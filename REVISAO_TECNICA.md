# Revisão técnica — HITECH VoltGuard SCADA Enterprise

## Escopo e conclusão

Esta entrega organiza e endurece o MVP para **demonstração/homologação controlada** no Render. Não representa certificação, pentest independente, conformidade normativa nem prontidão para uso industrial crítico.

## Melhorias aplicadas nesta revisão

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
6. Rever WebSocket: token na query string pode aparecer em logs; preferir mecanismo de autenticação que não exponha bearer token na URL e limitar conexões.
7. O webhook ainda pode estar sujeito a DNS rebinding/TOCTOU entre validação e conexão. Para produção, usar worker isolado, política de saída de rede, destinos permitidos e logs/retries controlados.
8. Rever a política de CORS, cookies/sessões (se forem introduzidos), CSP e configuração de proxy/HTTPS de acordo com o ambiente.

### Banco e multiempresa

1. `PanelModel.id` ainda é chave primária global. A aplicação não permite reutilizar o mesmo ID em duas organizações. Alterar para chave composta exige migração estrutural e testes de regressão.
2. A coluna `tenant_id` foi adicionada ao histórico e as consultas filtram por organização. Validar a migração com cópia de banco e backup antes de atualizar bases persistentes antigas.
3. A migração de compatibilidade em `init_db()` cobre apenas a coluna `panel_history.tenant_id`; não substitui Alembic para futuras mudanças estruturais.
4. Adicionar testes negativos para cada endpoint que lê ou altera painéis, inventário, regras, auditoria, ordens, webhooks e relatórios.
5. Criar histórico de movimentação de estoque, constraints/índices apropriados, transações robustas e testes de concorrência. A validação de saldo negativo já foi adicionada, mas concorrência precisa ser testada em PostgreSQL.
6. Completar trilha de auditoria para todas as operações administrativas e definir retenção, exportação e exclusão.

### Telemetria e operação

1. A ingestão ainda usa token de usuário. Criar identidade e credenciais individuais por dispositivo, rotação/revogação de chaves, timestamps de origem confiáveis, idempotência, limites de taxa e métricas de qualidade.
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
