# Gateway Modbus TCP do VoltGuard

Coletor local de leitura somente. Lê registradores Modbus TCP e envia as medições por HTTPS para `POST /api/device/telemetry`. Não envia comandos ao medidor, não abre porta de entrada na rede do cliente e não substitui PLC, proteção ou supervisório.

## Configuração

1. Instale Python 3.10 ou superior e crie o ambiente no computador gateway.
2. Instale as dependências: `python -m pip install -r requirements.txt`.
3. Copie `config.example.json` para `gateway-config.json` fora do controle de versão.
4. Preencha painel, URL do VoltGuard e IP/Unit ID do medidor. Configure os registradores somente a partir do mapa oficial do modelo e firmware instalados. Os endereços no arquivo de exemplo estão vazios de propósito.
5. Crie uma credencial na aba **Dispositivos**, vinculada ao painel correto. Guarde o token apenas como variável de ambiente `VOLTGUARD_DEVICE_TOKEN` no gateway.
6. Antes do equipamento, valide o arquivo e o acesso ao painel com `python gateway.py gateway-config.json --preflight`. Essa opção não conecta ao Modbus nem envia telemetria.
7. Com o mapa e o equipamento disponíveis, inicie com `python gateway.py gateway-config.json`.

O pré-check confirma que o JSON é válido, mostra quantas grandezas ainda precisam de endereço, verifica se o segredo está configurado sem revelá-lo e consulta `GET /health`. É possível executá-lo antes de preencher o mapa Modbus; os endereços podem continuar vazios até a documentação correta estar disponível.

O processo valida os principais parâmetros antes de abrir a conexão: endereço e tipo de registrador, unidade, intervalo, escala, HTTPS e limites de cada grandeza aceitos pela API. Consulta cada grandeza habilitada, normaliza o valor usando `scale` e publica somente as medições obtidas. Se uma leitura Modbus falhar ou ficar fora do intervalo, o ciclo não envia um conjunto parcial potencialmente enganoso; registra um aviso sem imprimir o token e tenta novamente no próximo intervalo. O certificado HTTPS é validado.

## Formato de cada grandeza

- `address`: endereço Modbus base zero conforme o mapa validado.
- `register_type`: `input` (código 04) ou `holding` (código 03).
- `data_type`: `uint16`, `int16`, `uint32`, `int32` ou `float32`.
- `scale`: multiplicador para converter o valor bruto à unidade esperada pela API.
- `word_order`: `big` ou `little` para ordem dos dois registradores de valores de 32 bits.

Confirme representação, sinal, escala, offset e ordem de palavras contra o mapa do fabricante e compare as leituras com o visor do equipamento. O coletor ainda não tem um perfil PM5320 homologado, buffer local quando a Internet cai, serviço de instalação ou validação em hardware; esses itens dependem do equipamento e do piloto.

## Rede e segurança

Restrinja Modbus TCP à rede local do equipamento e permita a saída HTTPS do gateway ao VoltGuard. Não exponha a porta 502 à Internet. Proteja o arquivo `gateway-config.json` e o segredo de ambiente com permissões do sistema operacional; não os envie ao GitHub. Revogue a credencial pela interface em caso de perda do gateway.
