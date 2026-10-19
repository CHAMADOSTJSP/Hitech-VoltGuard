# Checklist de implantação — Render

## Antes do deploy

- [ ] Repositório GitHub privado criado.
- [ ] Arquivos do pacote extraídos diretamente na raiz do repositório.
- [ ] Pasta `vendor/` enviada com `chart.umd.min.js`, `html5-qrcode.min.js` e as duas licenças.
- [ ] `.env`, banco local e segredos reais não foram enviados ao Git.
- [ ] `render.yaml` revisado; planos/região/recursos confirmados no painel do Render.
- [ ] Dependências e testes locais executados em ambiente com as dependências de `requirements.txt` instaladas.

## Durante o deploy

- [ ] Blueprint criou serviço web e banco PostgreSQL.
- [ ] `SECRET_KEY` foi gerada pelo Render e está definida como variável secreta.
- [ ] `DATABASE_URL` aponta para o banco correto.
- [ ] Build e start terminaram sem erros.
- [ ] `/health` responde HTTP 200.
- [ ] `/vendor/chart.umd.min.js` e `/vendor/html5-qrcode.min.js` respondem HTTP 200; a aba Network não mostra chamadas aos CDNs.
- [ ] CSP permanece Report-Only; observar o Console durante os fluxos comuns e QR antes de considerar bloqueio.

## Testes pós-deploy

- [ ] Criar organização de teste com senha de pelo menos 12 caracteres.
- [ ] Fazer login e sair.
- [ ] Confirmar que os painéis iniciais estão marcados como dados de demonstração.
- [ ] Testar leitura QR manual; testar câmera somente em navegador/ambiente com permissão.
- [ ] Criar ordem de serviço e alterar estado.
- [ ] Testar exportação CSV autenticada.
- [ ] Testar regra de alarme e validar os limites com dados simulados.
- [ ] Criar item de estoque, aumentar saldo e confirmar que ajuste negativo indevido é rejeitado.
- [ ] Criar duas organizações de teste e verificar que uma não consegue consultar o painel da outra.
- [ ] Confirmar que nenhum equipamento real ou função de comando/proteção está conectado.

## Antes de qualquer piloto com dados reais

- [ ] Plano PostgreSQL persistente escolhido e política de expiração confirmada.
- [ ] Backup e restauração testados.
- [ ] Revisão independente de segurança e testes de isolamento concluídos.
- [ ] Migrações de banco revisadas com backup.
- [ ] Política de privacidade, retenção, suporte e resposta a incidentes definida.
- [ ] Telemetria real validada em laboratório, com identidade por dispositivo e rede de aquisição isolada.
