# Relatório técnico — HITECH VoltGuard SCADA Enterprise

## Resumo
A versão atual é uma base de demonstração melhorada para desenvolvimento local. Não é uma solução certificada, não foi submetida a pentest independente e não deve ser ligada a funções de proteção/comando industrial. Não há uma única definição universal de “conformidade”: é necessário definir país, setor, escopo de segurança, infraestrutura e requisitos contratuais antes de declarar conformidade normativa.

## Melhorias incluídas nesta revisão
- Senhas novas com hash scrypt; suporte temporário a SHA-256 legado com migração no login.
- Segredo JWT sem valor fixo no código; configuração via `SECRET_KEY`.
- Validação de organização/usuário, IDs de painel, limites de alarmes e faixas da telemetria.
- Alarme por temperatura e corrente.
- Limite configurado de painéis aplicado ao adicionar novos painéis.
- WebSocket valida JWT e envia eventos apenas a conexões do mesmo tenant.
- Validação de webhook HTTPS/host público e desativação por campo vazio; redirects automáticos desativados no envio.
- Simulação de falha restrita a CEO/Gerente.
- Gestão de ordens de serviço via API e interface (criar e alterar estado), com auditoria.
- Relatório executivo CSV com dados reais consultados dentro do tenant autenticado.
- Cabeçalhos HTTP básicos e endpoint de saúde.
- Interface escapa a maioria dos campos dinâmicos que são inseridos em HTML.
- Instruções de execução, exemplo de ambiente, Dockerfile e testes de helpers.

## Verificações realizadas
- `python -m py_compile main.py`: passou.
- `python -m unittest discover -s tests -v`: 3 testes passaram.
- JavaScript inline extraído e verificado com `node --check`: passou.
- Teste de integração local com SQLite temporário: cadastro de organização, login, consulta de painéis, criação de painel, ingestão de telemetria, criação de ordem e exportação CSV responderam com códigos esperados.

## Pendências críticas para uma versão de produção
### Segurança e privacidade
1. Implementar rate limiting e proteção contra abuso em login/cadastro, MFA, recuperação de senha, revogação de sessão e política de retenção.
2. Fazer revisão independente de XSS/CSP e garantir que todo dado não confiável seja inserido via `textContent` ou escape contextual apropriado. A revisão de templates não substitui pentest.
3. O webhook tem validação inicial de DNS/IP público, mas ainda pode haver riscos de DNS rebinding/TOCTOU. Idealmente usar worker isolado, política de saída de rede, lista de destinos permitidos e logs/retries controlados.
4. Implementar gestão segura de segredos, HTTPS/proxy, logs estruturados, alertas de segurança e política de backup/restore.
5. Rever LGPD: finalidade, minimização, acesso, retenção, exportação e exclusão de dados conforme o contexto real.

### Dados e multi-tenancy
1. `PanelModel.id` continua sendo chave primária global, portanto IDs iguais não podem ser reutilizados por organizações diferentes.
2. `PanelHistoryModel` ainda não possui `tenant_id`; o isolamento depende dos IDs globais de painéis. Migrar para chave composta ou ID interno e adicionar testes negativos de isolamento.
3. Usar Alembic ou mecanismo formal de migração. `Base.metadata.create_all()` não altera automaticamente tabelas existentes. Faça backup e migração explícita antes de atualizar bases persistentes.
4. Completar auditoria de todas as operações, movimentações de inventário e alterações administrativas; avaliar imutabilidade/armazenamento externo se houver requisito de auditoria forte.

### Funcionalidade e operação
1. Telemetria ainda é ingerida com token de usuário. Criar identidade e credenciais por dispositivo, timestamp UTC, idempotência, qualidade da leitura, unidade, limites de taxa e monitoramento de comunicação.
2. Integração real com PLCs/medidores/protocolos não está implementada. Validar no laboratório e selecionar protocolos conforme os equipamentos (por exemplo, Modbus TCP/RTU ou OPC UA) após análise de risco.
3. Previsão de falhas, ESG e alguns KPIs permanecem demonstrativos/estáticos; não apresentar como resultado medido ou predição validada.
4. Cobrança é apenas metadado de assinatura; não há integração de pagamentos, renovação, inadimplência ou ciclo de cancelamento.
5. Estoque precisa de tabela de movimentações, proteção contra saldo negativo e testes transacionais/concorrrência.
6. Testes de integração automatizados completos, teste de carga, recuperação de backup, navegador cross-platform e observabilidade ainda faltam.

## Conformidade
Não declarar conformidade com NR-10, IEC 62443, LGPD ou certificação industrial com base nesta entrega. Isso exige definir requisitos, arquitetura de implantação, controles organizacionais, avaliação de risco, evidências e validação por profissionais habilitados. A aplicação deve ficar em ambiente de desenvolvimento/laboratório até essa etapa.
