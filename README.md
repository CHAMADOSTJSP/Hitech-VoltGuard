# HITECH VoltGuard SCADA Enterprise — pacote para Render

## v0.38.1 — Tradução completa do leitor QR

A tradução dos controles do leitor agora alcança também textos inseridos em nós de texto da biblioteca, incluindo a opção para ler um QR a partir de imagem.

## v0.38.0 — Leitor QR em português

Os controles do leitor QR passam a ser exibidos em português. A orientação da aba esclarece que a câmera é opcional e que também é possível consultar o painel por imagem, código ou ID.

## v0.37.0 — Teste independente de webhook

A aba Webhooks permite enviar um evento de teste ao endpoint salvo sem simular uma falha nem criar alarmes. A interface informa o resultado HTTP e cada tentativa é registrada na auditoria da organização.

## v0.36.2 — Painel mais amplo no Excel Online

O resumo foi reorganizado em três cartões por linha, ocupando mais largura da tela sem depender do zoom do aplicativo. Inclui contagens de painéis normais e alarmes encerrados.

## v0.36.1 — Zoom e cores de alerta condicionais

A aba Resumo abre com zoom de 140% para aproveitar melhor a tela. Cartões de painéis críticos, alarmes ativos/reconhecidos e estoque abaixo do mínimo usam cores de alerta apenas quando a contagem é maior que zero.

## v0.36.0 — Resumo executivo em cartões

A aba inicial do relatório apresenta os indicadores em cartões coloridos organizados em duas colunas, com maior destaque para itens críticos. O layout ocupa melhor a página, centraliza a impressão em uma folha horizontal e mantém as abas seguintes para consulta detalhada.

## v0.35.2 — Mais espaço no título do resumo

Ampliadas as colunas da aba Resumo para dar margem visual ao título e às notas no Excel.

## v0.35.1 — Ajuste visual do resumo do relatório

A aba Resumo usa colunas mais largas para exibir o título e as notas sem cortes ao abrir no Excel.

## v0.35.0 — Relatório executivo formatado em Excel

O relatório executivo agora é exportado como `.xlsx`, com abas separadas para resumo, painéis, alarmes, ordens de serviço, ativos, manutenção e estoque. O arquivo inclui cabeçalhos destacados, filtros, linhas congeladas, colunas ajustadas e configuração para impressão. Mantém a rastreabilidade de alarmes e OS e o progresso dos checklists.

## v0.34.0 — Rastreabilidade no relatório executivo

O CSV executivo inclui datas de ocorrência, reconhecimento e encerramento dos alarmes e mostra a OS vinculada. As OS exportadas incluem o alarme de origem e o progresso do checklist; o resumo também conta alarmes ativos/reconhecidos e OS originadas de alarmes.

## v0.33.0 — Rastreamento da origem das ordens

A aba Ordens de Serviço identifica ordens criadas a partir de alarmes, permite filtrar por origem e localizar uma ordem pelo número do alarme. O resumo inclui a quantidade de ordens vinculadas a alarmes.

## v0.32.0 — Duração e resumo da Central de Alarmes

A Central de Alarmes apresenta contagens por estado e mostra a primeira e a última ocorrência, a duração total e os horários de reconhecimento e encerramento quando disponíveis. A duração dos alarmes ainda abertos acompanha as atualizações periódicas da tela.

## v0.31.0 — Prévia do comportamento dos alarmes

Na aba Regras de Alarme, a configuração por painel mostra os valores que abrem os alarmes de temperatura e corrente e os valores de normalização após histerese. A prévia atualiza durante a edição e indica que os parâmetros editados só entram em vigor após salvar.

## v0.30.0 — Guia de integração de telemetria

A aba Dispositivos inclui um guia rápido expansível para enviar leituras ao endpoint de telemetria, com exemplo HTTP copiável e payload ajustado ao painel selecionado. O exemplo usa um marcador de token: o segredo continua guardado no gateway e nunca é inserido nem exibido novamente pela interface.

## v0.29.0 — Tarefas avulsas de manutenção

A aba Manutenção permite agendar tarefas avulsas além dos planos recorrentes. Checklist e observações ficam visíveis nos detalhes da tarefa, a data de conclusão aparece na lista e tarefas concluídas ou canceladas têm o estado final bloqueado na interface.

## v0.28.0 — Resumo da gestão de ativos

A aba Ativos mostra totais cadastrados, em operação, em manutenção e vinculados a painéis. A tabela aplica cores ao estado e informa claramente quando não há ativos ou quando os filtros não encontram resultados.

## v0.27.0 — Movimentação de estoque pela interface

A aba Almoxarifado permite registrar itens e movimentações de entrada/saída pela API existente, mostra os itens abaixo do mínimo e calcula o valor estimado em estoque. Ao informar o nome exato de um item existente, categoria, mínimo e custo são preenchidos com os valores atuais antes do ajuste.

## v0.26.0 — Resumo ESG transparente

A aba ESG consolida as estimativas informadas por painel e indica quantas estão disponíveis. A tela esclarece que os números são demonstrativos, não medições, cálculos de emissões ou indicadores auditados; painéis sem valor permanecem identificados como indisponíveis.

## v0.25.0 — Histórico térmico paginado na interface

A aba Tendência Térmica carrega a primeira página de até 500 amostras por painel e oferece **Carregar registros anteriores** para consultar páginas adicionais. A consulta usa cursor por ID e mantém as amostras já carregadas durante o polling. A API continua limitada ao painel e à organização autenticada.

## v0.24.0 — Leitura de QR mais previsível

A aba Comissionamento evita consultas repetidas do mesmo QR durante a leitura contínua, encerra a câmera ao sair da aba e mostra conectividade e horário da última telemetria no resultado. A consulta manual também pode ser enviada pelo teclado.

## v0.23.0 — Leitura de conectividade em português

A aba Tempo Real localiza valores numéricos e horários, apresenta estados de conectividade em português e calcula o tempo desde a última telemetria. Diferencia painel sem credencial ativa de painel que ainda aguarda a primeira leitura.

## v0.22.0 — Retorno de entrega do webhook

A simulação de falha crítica informa se o endpoint respondeu com sucesso, falhou ou não estava configurado. Respostas HTTP de erro deixam de ser consideradas entrega válida; a gravação dos alarmes é mantida mesmo quando o endpoint externo falha.

## v0.21.0 — Configuração de webhook mais clara

A aba Webhooks informa que o envio atual é acionado pela simulação de falha crítica, valida a URL como HTTPS no navegador e mostra retorno de sucesso ou erro ao salvar. Um campo vazio remove a configuração.

## v0.20.0 — Relatório executivo ampliado

O CSV executivo inclui indicadores e registros da organização para painéis, alarmes, ordens de serviço, ativos, tarefas de manutenção e estoque. A exportação é isolada por organização, inclui marca UTF-8 para compatibilidade com Excel e protege campos textuais contra execução acidental como fórmulas.

## v0.19.0 — Resumo de assinatura e uso

A aba Assinatura & Billing mostra o plano e estado retornados pela organização, a data de expiração quando cadastrada e o uso do limite de painéis. A tela informa quando a data não foi configurada e esclarece que não processa pagamentos nem alterações de plano.

Versão revisada para **demonstração e homologação controlada**. Este pacote não é SCADA industrial certificado e não deve ser conectado a funções de proteção, intertravamento ou comando de equipamentos elétricos.

## v0.18.0 — Regras de alarme

Regras específicas por painel podem ser removidas para voltar aos limites padrão da organização. A alteração é isolada por organização e auditada. A auditoria das regras gerais registra os limites de temperatura e corrente.

## v0.17.0 — Credenciais de dispositivos

A aba Dispositivos resume credenciais ativas, nunca utilizadas e revogadas, com busca e filtros por painel/estado. O log de criação guarda o ID atribuído pelo banco; chamadas repetidas para revogar não alteram o horário original.

## v0.16.0 — Acompanhamento de manutenção

A aba Manutenção apresenta contadores operacionais, destaca e filtra tarefas atrasadas, permite buscar por ativo/tarefa/responsável e ajustar o responsável, prazo e estado da tarefa. Alterações operacionais entram na auditoria.

## v0.15.0 — Gestão de ativos

A aba Ativos agora permite buscar por tag, nome, tipo, localização, fabricante, modelo, série ou painel, filtrar por estado e editar os dados. Mudanças são registradas na auditoria e os ativos podem ser marcados como `ATIVO`, `MANUTENCAO` ou `INATIVO`, preservando seus vínculos com planos e tarefas.

## v0.14.0 — Auditoria pesquisável e paginada

A aba Auditoria permite filtrar por texto, usuário, ação e intervalo de datas. Os registros são carregados em páginas de até 100 itens, com isolamento pela organização autenticada.

## v0.13.0 — Busca e filtros na Central de Alarmes

A lista de alarmes agora pode ser pesquisada por painel, tipo ou mensagem e filtrada por estado e severidade. Alarmes reconhecidos mostram o usuário responsável.

## v0.12.0 — Edição dos dados da OS

Os dados principais de uma ordem existente podem ser editados pela coluna **Título**: título, prioridade, técnico atribuído, prazo e descrição. As alterações são registradas no histórico da ordem.

## v0.11.0 — Relatório individual de ordem de serviço

Cada OS pode abrir um relatório imprimível com seus dados, checklist, resumo de execução e histórico. Use a opção de impressão do navegador e escolha “Salvar como PDF” para exportar o documento.

## v0.10.2 — Preservação dos modelos ao redesenhar a tela

As opções de modelos são repostas no seletor após criar uma OS ou redesenhar a aba, mantendo os modelos disponíveis enquanto o formulário é reconstruído.


## v0.10.1 — Aplicação direta dos modelos

Selecionar um modelo agora preenche automaticamente os itens no formulário da nova OS; a aplicação confirma antes de substituir itens já digitados. O botão **Usar modelo** permanece disponível.

## v0.10.0 — Modelos reutilizáveis de checklist

Modelos de checklist são guardados por organização. CEO e Gerente podem salvar o checklist atual como modelo e remover modelos; qualquer usuário autenticado com acesso às OS pode aplicar um modelo ao formulário. As OS existentes permanecem independentes dos modelos.

## v0.9.0 — Checklist de execução para ordens de serviço

Ao criar uma OS, é possível incluir até 20 itens de checklist. A equipe marca cada item durante a execução; cada alteração registra usuário, horário e ação no histórico. O sistema impede concluir uma ordem enquanto houver itens pendentes. OS antigas sem checklist continuam funcionando.

## v0.8.0 — Busca e prioridade operacional para ordens

A gestão de OS mostra contagens por situação, permite buscar por painel/título/técnico e filtrar por estado ou apenas prazos vencidos. Ordens ativas com prazo expirado recebem destaque visual.

## v0.7.2 — Preservação de rascunhos de ordem de serviço

O polling atualiza os dados em memória sem reconstruir a aba de OS, preservando campos preenchidos e histórico expandido. A lista é redesenhada após criar/atualizar uma OS ou navegar novamente para a aba.

## v0.7.1 — Histórico permanece aberto durante o polling

A seção expansível do histórico mantém seu estado aberto enquanto os dados do painel são atualizados automaticamente.

## v0.7.0 — Histórico de alterações das ordens de serviço

Cada OS registra criação e alterações de estado/campos com usuário, papel, horário e detalhes. O histórico fica disponível em uma seção expansível na lista de ordens. Ordens anteriores à atualização não têm eventos retroativos; alterações passam a ser registradas após a implantação.

## v0.6.0 — Ciclo de vida das ordens de serviço

Ordens de serviço agora registram prazo, início e conclusão. A conclusão exige um resumo da solução executada com pelo menos 10 caracteres; datas e resultado aparecem na gestão de ordens. A inicialização adiciona os novos campos a bancos existentes sem apagar ordens anteriores.

## v0.5.3 — Telemetria confiável e conectividade

- Estado do dispositivo: `NOT_CONFIGURED`, `NEVER_CONNECTED`, `ONLINE` ou `OFFLINE`, com base no último uso de credencial ativa.
- `DEVICE_OFFLINE_AFTER_SECONDS` define o limiar de inatividade (padrão 300 segundos; faixa de 30 a 86400 segundos).
- `GET /api/telemetry/history/{panel_id}` retorna histórico paginado, protegido por autenticação e isolamento de organização. Parâmetros: `limit` (1–1000) e `before_id`.
- O endpoint de dashboard mantém no máximo 500 amostras por painel para reduzir payloads grandes.
- Os cartões de monitoramento exibem conectividade e último contato.
- O estado `ONLINE` significa que uma credencial ativa enviou telemetria recentemente; não comprova por si só que um PLC ou equipamento físico esteja íntegro.

## Conteúdo do pacote

- `main.py`: API FastAPI, autenticação JWT, SQLAlchemy, cadastro de organização, painéis, telemetria via API autenticada, alarmes, inventário, ordens de serviço, auditoria e exportação CSV.
- `index.html`: painel web responsivo em português, login/cadastro, abas de monitoramento, QR Code e gestão.
- `requirements.txt`: dependências de execução, incluindo o driver PostgreSQL.
- `render.yaml`: Blueprint para serviço web e PostgreSQL no Render.
- `Dockerfile`: alternativa de execução por contêiner.
- `tests/test_render_smoke.py`: testes básicos de saúde, autenticação, isolamento entre organizações, relatório e integridade do estoque.
- `.env.example`: exemplo de configuração local sem segredos reais.
- `REVISAO_TECNICA.md`: limitações conhecidas e checklist antes de produção.

## v0.5.1 — Histórico completo de telemetria

O histórico agora registra temperatura, corrente e tensão por amostra, além do timestamp UTC. As colunas novas são adicionadas de forma compatível com registros antigos; medições históricas que não foram armazenadas anteriormente permanecem sem corrente/tensão (`null`), sem inventar valores.

### Teste de telemetria autenticada

1. Na aba **Dispositivos**, crie uma credencial para um painel de teste e copie o token apenas no momento em que ele for exibido.
2. Envie uma leitura para `POST /api/device/telemetry` com `Authorization: Bearer <TOKEN>` e JSON semelhante ao exemplo abaixo. Substitua `PANEL_ID` e `TOKEN`; não os coloque em repositórios públicos.

```bash
curl -X POST "https://SEU-SERVICO.onrender.com/api/device/telemetry" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"panel_id":"PANEL_ID","temperature":42.5,"current":118.4,"voltage":"380V AC"}'
```

3. A resposta deve conter `status: success`. Consulte o painel e o histórico para confirmar temperatura, corrente e tensão. Uma leitura acima dos limites configurados deve gerar/atualizar o alarme correspondente; uma leitura normal deve limpar automaticamente a condição ativa.
4. Em **Dispositivos**, confirme que “Último uso” foi atualizado. Revogue a credencial e repita a chamada: a API deve responder `401`.

Validações locais nesta versão: 11 testes automatizados aprovados. O teste foi executado com um stub de `slowapi` porque essa dependência não estava disponível no ambiente local; portanto, o rate limiting deve ser confirmado com as dependências completas no Render. A atualização não foi publicada automaticamente no serviço do usuário.

## Publicação recomendada no Render

1. Extraia o ZIP e confirme que `main.py`, `index.html`, `requirements.txt`, `Dockerfile` e `render.yaml` estão na raiz do repositório.
2. Crie um repositório **privado** no GitHub e envie o conteúdo da pasta do projeto. Não envie `.env`, bancos locais ou segredos.
3. No Render, escolha **New + → Blueprint** e conecte o repositório.
4. Revise os recursos e variáveis definidos pelo `render.yaml` antes de aplicar.
5. Aguarde o deploy e verifique `https://SEU-SERVICO.onrender.com/health`. A resposta esperada contém `"status":"ok"`.
6. Abra a página inicial, selecione **Registar Nova Empresa**, crie uma organização, um usuário e uma senha com pelo menos 12 caracteres; depois faça login.
7. Confira que os três painéis criados para a organização estão identificados como demonstração. Não são leituras de medidores físicos.
8. Teste o acesso às abas, a criação de ordens de serviço, a exportação CSV, as regras e o inventário.

## Configuração do serviço

O Blueprint configura:

- `SECRET_KEY`: gerada pelo Render; mantenha-a secreta e estável entre reinicializações.
- `DATABASE_URL`: conexão fornecida pelo banco PostgreSQL do Blueprint.
- `SIMULATE_TELEMETRY=0`: não simula variações contínuas das leituras.
- `PYTHON_VERSION=3.12.8`.

Se configurar o serviço manualmente, use:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Configure `SECRET_KEY` com pelo menos 32 caracteres aleatórios e `DATABASE_URL` com a URL interna do PostgreSQL. Não existe usuário/senha predefinido; cadastre a primeira organização pela interface.

Não comite valores reais de `SECRET_KEY` nem URLs de banco com credenciais.

## Testes locais

Requer Python 3.12 ou superior compatível com as dependências listadas.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
uvicorn main:app --host 127.0.0.1 --port 8000
```

Abra `http://127.0.0.1:8000`. Para ambiente local, o padrão é SQLite. Para Render, use PostgreSQL.

## Persistência e custo

O Blueprint está configurado para avaliação econômica. Serviços e bancos gratuitos podem ter limites de uso, suspensão por inatividade e políticas de expiração que mudam com o tempo. Antes de guardar dados reais, confirme no painel e na documentação atual do Render o plano, a persistência, os backups e a política de expiração do PostgreSQL. Faça upgrade quando necessário e teste restauração antes de um piloto comercial.

## Limites funcionais importantes

- A telemetria da API é autenticada com token de usuário; **ainda não existe uma identidade/credencial dedicada por dispositivo industrial**.
- Não há driver pronto de PLC/medidor (Modbus/OPC UA), gateway de aquisição ou garantia de tempo real industrial.
- O WebSocket autentica o token via query string, o que pode expor tokens em logs; reavaliar antes de produção.
- Alguns KPIs, previsão de falhas e valores ESG são demonstrativos/estimativas e não constituem predição validada ou medição real.
- A assinatura representa metadados; não há integração de cobrança, pagamentos, inadimplência ou cancelamento.
- IDs de painéis permanecem globalmente únicos no modelo atual. A coluna `tenant_id` e os filtros de acesso protegem as consultas, mas permitir IDs iguais entre organizações requer migração de chave e revisão dos relacionamentos.
- O limitador de requisições usa armazenamento em memória por processo; não é proteção distribuída para uma implantação escalada.

Leia `REVISAO_TECNICA.md` antes de usar dados reais.

## Novos módulos (v0.5.0)

### Gestão de ativos
A aba **Ativos** permite cadastrar tag patrimonial, nome, tipo, localização, fabricante, modelo, número de série, painel associado e observações. A tag é validada como única por organização na aplicação.

Endpoints autenticados: `GET /api/assets`, `POST /api/assets` e `PATCH /api/assets/{id}` (edição permitida a CEO e Gerente).

### Manutenção preventiva
A aba **Manutenção** permite criar planos com periodicidade em dias e checklist, gera a primeira tarefa e agenda a próxima execução quando uma tarefa recorrente é concluída. Estados: `PENDENTE`, `EM_ANDAMENTO`, `CONCLUIDA`, `CANCELADA`. A recorrência é acionada na conclusão da tarefa, não por um scheduler externo.

Endpoints autenticados: `GET/POST /api/maintenance/plans`, `GET/POST /api/maintenance/tasks`, `PATCH /api/maintenance/tasks/{id}` (atualiza estado, responsável e prazo).

### Credenciais dedicadas de dispositivo
A aba **Dispositivos** permite emitir um token exclusivo vinculado a um painel. A API guarda somente o hash SHA-256 do token; o valor bruto aparece uma única vez na criação. Credenciais podem ser revogadas. Use HTTPS, armazene o token em cofre de segredos no gateway e nunca no JavaScript do navegador.

Envie telemetria com `POST /api/device/telemetry`, cabeçalho `Authorization: Bearer <device-token>` e JSON contendo `panel_id`, `temperature`, `current` e opcionalmente `voltage`. Cada token só pode enviar dados ao painel ao qual foi vinculado. Isso implementa o endpoint de ingestão autenticada, mas não instala driver Modbus/OPC UA nem conecta automaticamente equipamento físico.

## Central de Alarmes (v0.4.1)
Acesse a aba **Central de Alarmes** depois de entrar. Os alarmes de temperatura/corrente são criados quando a telemetria autenticada excede os limites da organização. O ciclo de vida inclui `ACTIVE`, `ACKNOWLEDGED` e `CLEARED`. Para gerar um alarme de teste, use um painel da própria organização e envie telemetria pelo endpoint autenticado `POST /api/telemetry` com valores acima dos limites configurados. Dados de teste não devem ser enviados a equipamentos de campo.

Endpoints autenticados:
- `GET /api/alarms` (opcional `?status_filter=ACTIVE|ACKNOWLEDGED|CLEARED`)
- `POST /api/alarms/{id}/acknowledge`
- `POST /api/alarms/{id}/clear`

O estado dos alarmes é específico por organização. Esta versão ainda não configura notificações de produção ou integrações com PLCs.

### Testar a Central de Alarmes com telemetria simulada
1. Entre com uma conta que tenha papel CEO ou Gerente.
2. Na aba **Tempo Real**, clique em **Disparar Alarme Crítico** em um painel de demonstração.
3. Confirme a mensagem de sucesso; a interface abre a **Central de Alarmes** automaticamente.
4. Devem aparecer alarmes `HIGH_TEMPERATURE` e `HIGH_CURRENT`. Você pode reconhecer o alarme ou encerrar manualmente conforme suas permissões.
5. Para encerrar automaticamente por retorno à faixa normal, envie telemetria dentro dos limites configurados via endpoint autenticado `/api/telemetry`.

Este botão altera apenas dados simulados da aplicação. Não envia comandos a equipamentos físicos nem deve ser usado como teste de proteção industrial.


### v0.5.2 — copiar token de dispositivo
Ao criar uma credencial em **Dispositivos**, abre uma janela com o token e botão **Copiar token**. O token é mostrado somente nessa criação; se fechar a janela sem guardá-lo, revogue a credencial e gere outra.


## v0.5.4 — Histórico gráfico
A aba **Tendência Térmica** mostra gráficos de temperatura e corrente a partir das amostras armazenadas. O filtro de período atua sobre até 500 amostras por painel carregadas no painel principal: última hora, 24 horas, 7 dias ou todo o histórico carregado. Para consultas mais extensas, use o endpoint autenticado `GET /api/telemetry/history/{panel_id}`, que suporta paginação. A tensão permanece exibida como última leitura textual porque o modelo atual não guarda uma tensão numérica normalizada. Se não houver amostras no período, a interface informa isso sem inventar dados.


### Regras de alarme por painel (v0.5.6)
A aba **Regras de Alarme** permite configurar limites e histerese por painel. Endpoints: `GET`, `PUT` e `DELETE /api/panels/{panel_id}/alarm-rules`. Ao remover uma regra personalizada, o painel volta a usar os limites da organização. A tabela `panel_alarm_rules` é criada por `create_all`; não exige apagar ou recriar o banco existente.


## v0.5.8

A aba Regras de Alarme não é mais reconstruída pelo polling periódico, preservando o painel selecionado e evitando que o formulário volte automaticamente ao primeiro painel.
