# Changelog

## v0.39.0 — Telemetria elétrica ampliada
- A API de dispositivo aceita leituras parciais de tensão, potência, energia, frequência e fator de potência, além de temperatura e corrente.
- Novas grandezas são armazenadas no painel e no histórico; medições ausentes preservam os valores atuais e não limpam alarmes de temperatura/corrente.
- Mantida a compatibilidade com gateways que enviam o payload anterior.
- Iniciada a preparação documentada da integração de referência com PowerLogic PM5320; driver e validação física continuam pendentes.

## v0.38.1 — Tradução completa do leitor QR
- Expandida a localização para traduzir textos renderizados como nós de texto, incluindo a leitura de QR por imagem.

## v0.38.0 — Leitor QR em português
- Traduzidos os controles do leitor de QR para português, inclusive quando a biblioteca os atualiza dinamicamente.
- Esclarecido na aba que a câmera é opcional e que há consulta manual por código/ID e leitura por imagem.

## v0.37.0 — Teste independente de webhook
- Adicionado teste do endpoint salvo, sem criar alarmes nem alterar a telemetria.
- Exibido o resultado HTTP e registrado cada teste na auditoria da organização.
- A interface habilita o teste após salvar um endpoint e o desabilita quando a configuração é removida.

## v0.36.2 — Painel mais amplo no Excel Online
- Reorganizados os indicadores em três cartões por linha para aproveitar melhor a largura da tela.
- Incluídas contagens de painéis normais e alarmes encerrados.

## v0.36.1 — Zoom e cores de alerta condicionais
- Definido zoom inicial de 140% na aba Resumo para reduzir o espaço vazio na tela.
- Alertas críticos e de estoque só recebem vermelho/âmbar quando a contagem é maior que zero.

## v0.36.0 — Resumo executivo em cartões
- Substituído o resumo tabular por cartões de indicadores organizados em duas colunas.
- Destacados em vermelho os indicadores críticos e em âmbar os pontos de atenção.
- Ajustado o resumo para impressão horizontal em uma página, preservando as abas detalhadas.

## v0.35.2 — Mais espaço no título do resumo
- Ampliadas as colunas da aba Resumo para dar margem visual ao título e às notas no Excel.

## v0.35.1 — Ajuste visual do resumo do relatório
- Aumentada a largura das colunas do resumo para exibir o título e as notas por completo no Excel.

## v0.35.0 — Relatório executivo formatado em Excel
- O relatório é exportado como `.xlsx`, com abas separadas para resumo, painéis, alarmes, ordens de serviço, ativos, manutenção e estoque.
- Incluídos cabeçalhos destacados, filtros, linhas congeladas, colunas ajustadas e configuração de impressão.
- Mantidas as referências entre alarmes e OS, contagens executivas e progresso dos checklists.

## v0.34.0 — Rastreabilidade no relatório executivo
- O CSV inclui datas da ocorrência, reconhecimento e encerramento dos alarmes e o ID da OS vinculada.
- Incluídos no resumo os alarmes ativos/reconhecidos e as ordens geradas por alarmes.
- As ordens exportadas identificam o alarme de origem e trazem o progresso do checklist.

## v0.33.0 — Rastreamento da origem das ordens
- Adicionado filtro para separar ordens abertas por alarmes das ordens criadas manualmente.
- Ordens geradas por alarme identificam a origem na linha e podem ser encontradas pela busca usando o número do alarme.
- Incluído contador de ordens originadas de alarmes no resumo.

## v0.32.0 — Duração e resumo da Central de Alarmes
- Incluídos contadores de alarmes ativos, reconhecidos, encerrados e em aberto.
- Exibidas a primeira e a última ocorrência e a duração do alarme.
- Mostrados os horários de reconhecimento e encerramento quando disponíveis.

## v0.31.0 — Prévia do comportamento dos alarmes
- A configuração por painel mostra quando cada alarme abre e o valor de normalização definido pela histerese.
- A prévia acompanha a edição dos limites e deixa claro que os valores só passam a valer após salvar.

## v0.30.0 — Guia de integração de telemetria
- Adicionado guia rápido expansível na aba Dispositivos com endpoint, cabeçalhos e exemplo de payload para o painel selecionado.
- Incluído botão para copiar a requisição de exemplo sem inserir nem revelar o token na interface.
- Documentados os campos opcionais e os intervalos aceitos para temperatura e corrente.

## v0.29.0 — Tarefas avulsas de manutenção
- Adicionado formulário para agendar tarefa avulsa com ativo, prazo, responsável e checklist/observações.
- Exibidos detalhes e data de conclusão das tarefas na listagem.
- Bloqueada na interface a troca de estado para tarefas concluídas ou canceladas, em linha com as transições da API.
- Incluídas mensagens vazias para tarefas e planos sem registros.

## v0.28.0 — Resumo da gestão de ativos
- Adicionados contadores para ativos cadastrados, em operação, em manutenção e vinculados a painéis.
- Destacados estados na listagem e mensagens explícitas para lista vazia ou filtros sem resultados.
- Preservados cadastro, edição e filtros existentes.

## v0.27.0 — Movimentação de estoque pela interface
- Ligado o formulário do Almoxarifado à API autenticada de movimentação de inventário.
- Adicionados movimentos positivos para entrada e negativos para saída, com validação do backend.
- Exibidos itens abaixo do mínimo, busca local e valor estimado do estoque.
- Ao selecionar por nome um item existente, os campos de categoria, estoque mínimo e custo são carregados para evitar sobrescrever os dados por engano.

## v0.26.0 — Resumo ESG transparente
- Adicionado resumo com quantidade de painéis, estimativas disponíveis e soma informativa em kWh/dia.
- Criada tabela por painel com localização, estimativa e indicação de dado indisponível.
- Explicitado que os valores são demonstrativos, não medições nem indicadores auditados.

## v0.25.0 — Histórico térmico paginado na interface
- Ligada a aba Tendência Térmica ao endpoint paginado de histórico por painel.
- Adicionado botão para carregar registros anteriores em páginas de até 500 amostras.
- Preservadas amostras históricas carregadas durante as atualizações automáticas.
- Mostrados estados de carregamento, disponibilidade do histórico e falha na consulta.

## v0.24.0 — Leitura de QR mais previsível
- Evitadas consultas repetidas ao decodificar o mesmo QR em sequência.
- Encerrada a câmera ao sair do Comissionamento e sincronizado o reinício do leitor.
- Incluídos estado de conectividade e horário da última telemetria no resultado da consulta.
- Consulta manual pode ser enviada pelo teclado e mostra estado de carregamento.

## v0.23.0 — Leitura de conectividade em português
- Localizada a exibição de medidas e horário da última telemetria.
- Traduzidos os estados de conectividade e mostrado o tempo desde a última leitura.
- Diferenciados os painéis sem credencial e os que aguardam a primeira telemetria.

## v0.22.0 — Retorno de entrega do webhook
- A simulação mostra se o webhook foi entregue, falhou ou não estava configurado.
- Respostas HTTP de erro são identificadas como falha de entrega.
- A falha de integração não impede que os alarmes simulados sejam gravados.

## v0.21.0 — Configuração de webhook mais clara
- A aba informa o estado configurado/desativado e quando o envio é disparado no comportamento atual.
- Adicionados validação básica de URL no navegador e mensagens de sucesso/erro no salvamento.
- Campo vazio permite remover e desativar o endpoint.

## v0.20.0 — Relatório executivo ampliado
- Ampliado o CSV com resumos de estado e registros de painéis, alarmes, OS, ativos, manutenção e estoque.
- Adicionada marca UTF-8 para melhorar a abertura de acentos no Excel.
- Campos textuais exportados são protegidos contra interpretação como fórmulas por planilhas.
- A aba explica o conteúdo e o caráter demonstrativo do relatório.

## v0.19.0 — Resumo de assinatura e uso
- A aba Assinatura & Billing apresenta os painéis cadastrados, o limite e as vagas disponíveis.
- Removida a data de expiração fictícia quando não há data registrada na assinatura.
- Indicados os limites da tela de demonstração: sem processamento de pagamentos, mudança de plano ou cancelamento.

## v0.18.0 — Regras de alarme
- Adicionada restauração das regras padrão da organização para um painel, removendo sua substituição específica.
- A restauração é restrita ao tenant e registrada na auditoria.
- Corrigida a auditoria das regras da organização para incluir temperatura e corrente.
- Evita que respostas fora de ordem troquem os valores exibidos ao alternar rapidamente entre painéis.

## v0.17.0 — Credenciais de dispositivos
- Corrigido o registro de auditoria na criação para incluir o ID definitivo da credencial.
- Tornada idempotente a revogação repetida, preservando o instante original da revogação.
- Adicionados indicadores, busca e filtros por painel e estado na lista de credenciais.
- Exibidos horários localizados e indicação explícita de credencial nunca utilizada.

## v0.16.0 — Acompanhamento de manutenção
- Adicionados indicadores de tarefas pendentes, em andamento, atrasadas e concluídas.
- Adicionados busca, filtro por estado e filtro de tarefas atrasadas.
- Permite ajustar responsável e prazo da tarefa junto com a transição de estado.
- Alterações de estado, responsável e prazo são registradas na auditoria.
- A data de conclusão é preservada quando uma tarefa concluída é salva novamente.

## v0.15.0 — Gestão de ativos
- Adicionada edição de identificação, dados técnicos, painel associado e estado dos ativos.
- Adicionados busca textual e filtro por estado na lista de ativos.
- Alterações de ativos são registradas na auditoria; a exclusão foi evitada para preservar vínculos com manutenção e histórico.
- Adicionado `PATCH /api/assets/{id}` com validação de organização, tag única e painel associado.

## v0.14.0 — Auditoria pesquisável e paginada
- Adicionado endpoint de auditoria paginado, limitado à organização autenticada e acessível somente ao CEO.
- Adicionados filtros por texto, usuário, ação e intervalo de datas.
- A interface carrega até 100 registros por página e permite carregar os próximos.
- A aba deixa de depender do recorte de 50 registros enviado pelo endpoint geral do painel.

## v0.13.0 — Busca e filtros na Central de Alarmes
- Adicionada busca por painel, tipo, severidade, mensagem e usuário que reconheceu o alarme.
- Adicionados filtros de estado (ativo, reconhecido e encerrado) e severidade.
- Exibido o usuário que reconheceu cada alarme.

## v0.12.0 — Edição dos dados da OS
- Adicionada edição de título, prioridade, técnico, prazo e descrição de uma ordem existente.
- Mudanças dos dados principais são registradas no histórico da OS e na auditoria.
- Permite limpar o prazo e remover o técnico atribuído.

## v0.11.0 — Relatório individual de ordem de serviço
- Adicionado relatório imprimível por OS com dados da ordem, prazo, técnico, descrição, checklist, resumo de execução e histórico.
- A impressão pode ser salva como PDF pelo navegador, sem dependência de serviço externo.
- Conteúdo variável é escapado antes de ser incluído no documento.

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
## v0.40.0 — Protótipo de gateway Modbus TCP

- Criado coletor local configurável e somente leitura, com envio HTTPS autenticado ao endpoint de dispositivo.
- Endereços Modbus permanecem sem preencher até validação do mapa do modelo e firmware reais.
- Sem validação física, buffer offline ou uso operacional; ver `gateway/README.md`.

