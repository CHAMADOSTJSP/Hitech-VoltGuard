# Changelog

## v0.10.2 — Preservação dos modelos ao redesenhar a tela
- Corrigido o seletor que voltava ao estado vazio quando a tela de ordens era redesenhada após criar uma OS.
- As opções existentes são reaplicadas ao formulário usando os modelos carregados da organização.

## v0.10.1 — Aplicação direta dos modelos
- Selecionar um modelo de checklist preenche automaticamente o campo da OS.
- Se já houver itens digitados, a interface pede confirmação antes de substituí-los.
- Mantido o botão explícito **Usar modelo** para reaplicar o modelo selecionado.

## v0.10.0 — Modelos reutilizáveis de checklist
- Adicionado armazenamento de modelos de checklist isolado por organização, com nome exclusivo dentro de cada tenant.
- CEO e Gerente podem salvar modelos a partir dos itens preenchidos e remover os modelos selecionados.
- Usuários com acesso à gestão de OS podem aplicar um modelo; isso preenche o checklist sem criar a ordem automaticamente.
- Criação e remoção de modelos entram no registro de auditoria. Os checklists já copiados para ordens existentes não mudam.

## v0.9.0 — Checklist de execução para ordens de serviço
- Criação de checklist opcional com até 20 itens por ordem.
- Marcação e reabertura de itens autorizadas a papéis operacionais; cada mudança gera histórico e auditoria com usuário e horário.
- A conclusão da OS é bloqueada até que todos os itens estejam concluídos; ordens antigas sem checklist seguem o fluxo atual.
- Checklist de OS encerradas fica bloqueado para edição.

## v0.8.0 — Busca e prioridade operacional para ordens
- Adicionados indicadores de ordens abertas, em andamento, atrasadas e concluídas.
- Busca local por painel, título ou técnico e filtros por estado e prazo vencido.
- Ordens ativas com prazo vencido recebem destaque; ordens concluídas/canceladas não são consideradas atrasadas.
- Estado dos filtros permanece ao redesenhar a tela após ações, e o polling continua sem limpar formulários.

## v0.7.2 — Preservação de rascunhos de ordem de serviço
- O polling deixa de reconstruir a aba de OS e, portanto, não apaga formulários parcialmente preenchidos ao perder o foco.
- A lista atualiza depois de criar ou atualizar uma OS; as consultas periódicas continuam atualizando os dados em memória.

## v0.7.1 — Persistência visual do histórico
- A expansão do histórico por OS é mantida durante a atualização automática do painel e novas renderizações da tela.

## v0.7.0 — Histórico de alterações das ordens de serviço
- Criada trilha dedicada e multiempresa para eventos de OS, persistida na mesma transação que a criação ou atualização.
- Cada evento registra usuário, papel, data/hora, campos alterados e o resumo de execução quando ele muda ou a OS é concluída.
- O histórico de cada OS é exibido em seção expansível na tela de gestão.
- Ordens existentes permanecem intactas; não há reconstrução de eventos anteriores, e a interface informa que o histórico começa nesta versão.

## v0.6.0 — Ciclo de vida das ordens de serviço
- Ordens de serviço aceitam prazo opcional e registram automaticamente a primeira entrada em andamento e a conclusão.
- A conclusão exige um resumo da solução executada com pelo menos 10 caracteres, visível na listagem da OS.
- A API e o dashboard expõem prazo, início, conclusão e resumo de execução.
- Migração compatível acrescenta os campos opcionais em bancos existentes, preservando ordens atuais.
- As datas são exibidas no horário local do navegador.

## v0.5.9 — Fluxo operacional de alarmes e manutenção
- Adicionada ação para criar uma ordem de serviço diretamente de um alarme aberto, preservando o vínculo para consulta posterior.
- Um alarme pode originar no máximo uma ordem vinculada; requisições repetidas retornam a ordem existente.
- A ordem herda o painel, prioridade por severidade e contexto temporal/mensagem do alarme.
- Reconhecimento de alarme e alteração de tarefas exigem papel operacional autorizado.
- Tarefas concluídas ou canceladas não podem ser reabertas por transições inválidas.
- A conclusão de tarefa recorrente, auditoria e agendamento da próxima ocorrência agora são gravados na mesma transação.
- Adicionada migração de compatibilidade para a coluna nullable `work_orders.alarm_id`.

## v0.5.8 — Preservação do painel selecionado nas regras
- Corrigido o polling do dashboard para não reconstruir a aba Regras de Alarme a cada 3 segundos.
- A seleção do painel e os valores editados permanecem na interface enquanto os dados em memória continuam atualizando.
- A navegação para fora e de volta à aba continua recarregando as regras do painel selecionado pela interface.

## v0.5.5 — Correção de atualização dos gráficos
- Corrigida a verificação dos canvases de histórico: o polling agora procura os IDs reais `chart-temp-*` e `chart-current-*`.
- Evita reconstruir toda a aba de tendências a cada ciclo de atualização, impedindo que os gráficos desapareçam intermitentemente.
- Mantém a atualização dos datasets sem inventar amostras.

## v0.5.4 — Histórico gráfico de telemetria
- A aba Tendência Térmica passou a exibir gráficos separados de temperatura e corrente com base em amostras persistidas.
- Adicionado filtro local por última hora, últimas 24 horas, últimos 7 dias ou todo o histórico carregado.
- Exibida mensagem explícita quando não há amostras no período; valores ausentes permanecem vazios, sem interpolação ou dados fictícios.
- A tensão recebida é apresentada como última leitura textual, pois o modelo atual armazena tensão como texto (ex.: `380V AC`), não como série numérica.
- O endpoint histórico existente mantém paginação, limite de consulta e isolamento por organização.
- A validação automatizada local não pôde ser concluída neste ambiente por ausência do pacote `slowapi`; executar `pip install -r requirements.txt` antes de repetir os testes.

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


## v0.5.6
- Regras de alarme configuráveis por painel, com fallback para os limites da organização.
- Histerese configurável para temperatura e corrente, reduzindo oscilação de alarmes.
- Auditoria de alterações de regras e validação de isolamento multi-tenant.
- UI de configuração por painel na aba Regras de Alarme.
