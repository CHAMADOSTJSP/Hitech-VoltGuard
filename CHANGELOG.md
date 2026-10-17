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
