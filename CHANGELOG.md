## v0.5.3 — Telemetria confiável e conectividade
- Status de conectividade baseado em atividade real de credenciais de dispositivo ativas.
- Endpoint autenticado de histórico de telemetria com paginação e isolamento multiempresa.
- Payload do dashboard limita o histórico aos 500 pontos mais recentes por painel.
- UI de monitoramento exibe conectividade e último contato.
- Configuração `DEVICE_OFFLINE_AFTER_SECONDS` documentada.

# Histórico de alterações

## v0.5.1 — Histórico completo de telemetria
- O histórico persistido passa a armazenar corrente e tensão, além da temperatura e timestamp.
- Migração compatível adiciona colunas nullable para preservar registros anteriores sem fabricar dados ausentes.
- A resposta de `/api/panels` expõe as medições novas no histórico.
- Testes da ingestão autenticada agora verificam persistência de temperatura/corrente/tensão, atualização de último uso, token ausente e faixa inválida.
- Incluído roteiro curl para teste de ponta a ponta no Render.


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

## 0.4.1 — Alarmes simulados funcionais
- O endpoint de simulação de falha agora cria/atualiza alarmes persistentes de temperatura e corrente para o tenant autenticado.
- O botão “Disparar Alarme Crítico” atualiza os dados, exibe erros de forma explícita e abre a Central de Alarmes após a simulação.
- Teste automatizado garante que a simulação cria alarmes consultáveis e persistentes sem equipamento físico.


## 0.5.0 — Ativos, manutenção preventiva e credenciais de dispositivos
- Adicionado cadastro de ativos com identificação patrimonial, fabricante/modelo/série, localização e vínculo opcional a painel.
- Adicionados planos de manutenção com checklist, periodicidade e tarefas persistentes. A conclusão de uma tarefa recorrente agenda a próxima execução; a mesma tarefa não agenda duplicatas ao ser atualizada novamente.
- Adicionadas credenciais dedicadas por dispositivo, token aleatório mostrado apenas uma vez e persistido somente como hash.
- Adicionado endpoint `/api/device/telemetry`, limitado ao painel vinculado à credencial e com atualização de histórico e alarmes.
- Adicionadas abas Ativos, Manutenção e Dispositivos e testes de isolamento, recorrência, ingestão e revogação.
- Limites: integração Modbus/OPC UA, scheduler externo, notificações, cobrança real e validação industrial continuam fora desta entrega.


## v0.5.2 — 2026-10-17
- Substituído o alerta nativo ao criar credencial por uma janela acessível com token selecionável e botão **Copiar token**.
- Incluído fallback de cópia e instrução para usar Ctrl+C se o navegador bloquear a cópia automática.
- O token continua sendo exibido somente na criação e não é gravado no armazenamento do navegador.
