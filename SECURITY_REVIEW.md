# Revisão de segurança — VoltGuard

Revisão do código e das dependências do branch `codex/commercial-readiness-audit`, em 23/10/2026. O resultado descreve o que foi verificado nesta cópia; não é certificação, pentest independente nem garantia de ausência de vulnerabilidades.

## Corrigido nesta revisão

- A suíte usava o mesmo IP simulado em todos os casos e consumia o limite real de cadastro/login compartilhado. Agora cada teste usa um endereço reservado próprio, sem desativar o limitador do aplicativo.
- A validade padrão da assinatura era calculada no carregamento do módulo. Todas as organizações criadas pelo mesmo processo podiam receber a mesma data de expiração. O prazo agora é calculado no momento de cada inserção.
- Os timestamps UTC usavam `datetime.utcnow()`, descontinuado na versão atual do Python. A função `utcnow()` preserva o formato UTC sem fuso usado pelas colunas existentes.
- Corpos da API agora têm limite em fluxo: 1 MiB para rotas `/api/*` e 16 KiB para ingestão de telemetria. O limite vale também quando o cliente envia o corpo em blocos sem `Content-Length`.
- O manifesto passou a exigir versões com correções de segurança conhecidas: FastAPI 0.161+, Starlette 1.3.1+, PyJWT 2.15+, python-multipart 0.0.31+ e cryptography 49+. As faixas também mantêm limites de versão major.
- O rate limit no Render usa o `CF-Connecting-IP` validado como endereço IP; ignora `X-Forwarded-For` fornecido pelo cliente. Localmente continua usando o IP da conexão.
- O Docker desativa a interpretação genérica de cabeçalhos proxy pelo Uvicorn. O `Host` é verificado contra `RENDER_EXTERNAL_HOSTNAME` e a lista opcional `ALLOWED_HOSTS`; HSTS reconhece HTTPS encaminhado apenas em Render.
- Painéis recém-cadastrados não recebem leituras aleatórias nem uma amostra inicial fictícia. A API marca `SEM_DADOS` até receber telemetria; a interface separa tensão de referência das leituras medidas.
- Amostras sem temperatura ou corrente não são apresentadas como operação normal: o painel fica `PARCIAL` até ser possível avaliar os dois limites de alarme. A API diferencia medições atuais de valores preservados de amostras anteriores.
- GitHub Actions executa testes e `pip-audit` em push/PR e semanalmente; Dependabot abre atualizações semanais para pacotes Python e Actions.

## Controles verificados no código

- Senhas novas usam scrypt; JWT fixa o algoritmo HS256; sessões têm identificador aleatório, expiração e revogação consultada no banco.
- As operações sensíveis verificam papel e organização no servidor. Os testes agora cobrem a matriz básica CEO/Gerente/Técnico de Campo para administração de usuários, auditoria, credenciais de dispositivo e relatório executivo, além de isolamento entre organizações nos fluxos principais; ainda não cobrem cada combinação de rota/papel.
- Tokens de dispositivo são aleatórios, armazenados como hash, limitados a um painel e revogáveis.
- Quando MFA TOTP está habilitado, o login agora exige o código TOTP ou um código de recuperação de uso único; senha correta sem segundo fator não cria sessão.
- Cadastro público é desativado por padrão em todos os ambientes; precisa de `ALLOW_SELF_SERVICE_REGISTRATION=1` explícito. O Blueprint do Render o mantém desativado até haver verificação de e-mail e onboarding.
- Webhooks exigem HTTPS, rejeitam destinos não globais, fixam o IP resolvido, não seguem redirects e não herdam proxies do ambiente.
- Cabeçalhos de segurança e CSP estão ativos; os testes confirmam ao menos `X-Content-Type-Options`.
- A revisão dos arquivos de configuração do branch não encontrou `.env` nem credenciais reais versionadas; `.env.example` contém valores vazios/de exemplo. Isso não inspeciona todo o histórico Git nem os segredos configurados no GitHub/Render.

## Pendências antes de dados reais ou venda

- O piloto sem custo usa rate limit em memória por processo. Sem Redis, várias instâncias ou reinícios não compartilham contadores; o fallback continua permissivo para disponibilidade. Configure armazenamento compartilhado antes de escalar.
- Não há confirmação de e-mail, convite ou onboarding comercial. O cadastro público agora fica fechado por padrão; não habilite a variável de self-service em produção antes de implementar verificação de e-mail, prevenção contra abuso e fluxo de suporte.
- Ainda não foram executados pentest, teste de carga, scanner de segredos de todo o histórico Git ou revisão independente. A validação local desta revisão executou 23 testes; `compileall`, `node --check`, `pip check` e `git diff --check` passaram. No commit `f0c8a59`, a CI passou em `pip-audit`, integração, sintaxe e build Docker; o serviço `voltguard-pilot-free` está ativo e `/health` retorna `ok`. A disponibilidade pública não substitui teste de carga ou homologação.
- Em Render, adicione cada domínio personalizado ao `ALLOWED_HOSTS` separado por vírgulas; sem isso, apenas o hostname padrão do serviço é autorizado.
- Backup/restauração do PostgreSQL, migrações formais com rollback, alertas, rotação de credenciais, recuperação de conta, retenção/exclusão de dados e resposta a incidentes ainda precisam de processo e validação operacional.
- A telemetria Modbus ainda precisa ser validada com o modelo/firmware do medidor em laboratório. Não conecte esta aplicação a funções de comando, proteção ou intertravamento e não declare conformidade NR-10, IEC 62443 ou LGPD com base nesta revisão.
- Os testes cobrem os fluxos principais e o cadastro do painel sem telemetria fictícia; ainda não formam uma matriz negativa completa de autorização multiempresa para todos os endpoints.

## Referências de advisories consultados

- [PyJWT — correções de segurança até 2.15.0](https://github.com/jpadilla/pyjwt/security/advisories)
- [Starlette — limites de parser de formulário e validação de Host/path](https://github.com/Kludex/starlette/security/advisories)
- [python-multipart — limites de cabeçalho multipart e parsing](https://github.com/Kludex/python-multipart/security/advisories)
- [cryptography — OpenSSL incluído nas wheels e validação de certificados](https://github.com/pyca/cryptography/security/advisories)
