# Histórico de alterações

## Revisão para Render

- Padronizados os nomes de arquivos e caminhos de implantação.
- Atualizados README, revisão técnica e checklist de implantação.
- Reforçada a validação de senha e entrada de cadastro/login.
- Removidas contas de demonstração com credenciais conhecidas.
- Adicionado `tenant_id` ao histórico e consulta de histórico limitada à organização.
- Timestamps de histórico passam a incluir data e hora completas.
- Corrigida validação de estoque para rejeitar saldo negativo e valores numéricos inválidos.
- Endurecida a validação de URL de webhook.
- Adicionados cabeçalhos HTTP e `Cache-Control: no-store` para API/health.
- Melhorias responsivas na interface e botão de simulação sem interpolar ID em código JavaScript inline.
- Adicionados testes smoke para saúde, cadastro/login, isolamento entre organizações, estoque e relatório autenticado.

## Limitações remanescentes

Consulte `REVISAO_TECNICA.md`. A aplicação permanece candidata a demonstração/homologação, não certificada para uso industrial crítico.

## v0.4.0 — Alarm lifecycle and operator workflow
- Added tenant-scoped persistent alarm records with severity, first/last trigger timestamps, acknowledgement metadata, and clearing timestamp.
- Telemetry threshold evaluation now opens or updates high-temperature/high-current alarms and automatically clears those conditions when subsequent telemetry returns within configured limits.
- Added authenticated alarm list, acknowledge, and clear endpoints with tenant isolation and audit trail entries.
- Added a Central de Alarmes interface with status, severity, timestamps, message, and operator actions.
- Added automated smoke coverage for alarm lifecycle and cross-tenant access denial.
- This release does not add physical PLC integration, production notification delivery, billing collection, or industrial certification.
