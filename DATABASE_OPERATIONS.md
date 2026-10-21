# Operação do banco de dados — HITECH VoltGuard

Este procedimento cobre os dados armazenados no PostgreSQL do Render. Faça o backup antes de qualquer alteração de esquema, atualização importante ou atividade de manutenção. Use somente dados de demonstração enquanto a restauração não tiver sido validada.

## Estado atual do aplicativo

- O endereço `DATABASE_URL` seleciona o PostgreSQL no Render; em desenvolvimento local, o padrão é SQLite.
- Na inicialização, `init_db()` executa algumas alterações de compatibilidade específicas e `Base.metadata.create_all()`. Isso não é um sistema de migração versionado e não oferece rollback automático.
- Não há comando de migração separado nesta versão. Não edite tabelas manualmente nem introduza uma nova migração de esquema sem cópia do banco, plano de retorno e validação em uma instância separada.
- O banco contém contas, hashes de senha, segredos TOTP criptografados, códigos de recuperação em hash, auditoria, credenciais de dispositivos em hash, telemetria e dados por organização. Trate qualquer exportação como informação sensível.

## Criar uma exportação no painel do Render

1. Abra o Dashboard do Render e selecione o recurso **PostgreSQL** conectado ao serviço VoltGuard.
2. Confirme que o nome do banco e o serviço correspondem ao ambiente pretendido.
3. Abra **Recovery** e escolha **Create export**.
4. Aguarde a exportação terminar e baixe o arquivo `.dir.tar.gz` para um local privado com acesso restrito.
5. Registre a data, o banco de origem e a versão do aplicativo em um registro de operação. Nunca inclua URLs de conexão, senhas ou segredos nesse registro.
6. Armazene uma cópia fora do Render se precisar de retenção maior. O Render informa retenção de sete dias para exportações lógicas criadas no painel.

O Render informa que exportações lógicas pelo painel e recuperação PITR não estão disponíveis para bancos no plano de computação Free. Confira o plano atual na página do banco. Para Free, use `pg_dump` a partir de uma máquina com ferramentas PostgreSQL instaladas e acesso à URL externa do banco; mantenha a URL fora do histórico de comandos, logs e mensagens. A URL externa contém credenciais.

## Recuperação após perda ou corrupção de dados

### Banco pago com recuperação PITR disponível

1. Em **Recovery**, use **Restore Database** para criar uma instância de recuperação em um horário anterior ao incidente.
2. Aguarde a nova instância ficar disponível e valide os dados nela, sem apontar o serviço ativo para ela ainda.
3. Se os dados estiverem corretos, atualize `DATABASE_URL` no ambiente do serviço (ou no Environment Group correspondente) para a URL da instância recuperada.
4. Faça um deploy/restart controlado e confirme `/health`, login de uma conta de teste e leitura de dados esperados.
5. Preserve a instância original até confirmar o funcionamento. Só então decida se ela deve ser suspensa ou removida.

O PITR cria uma nova instância; ele não substitui o banco em uso automaticamente. Janela e disponibilidade dependem do plano vigente. Consulte [Render Postgres Recovery and Backups](https://render.com/docs/postgresql-backups).

### Restaurar uma exportação lógica

Restaure apenas em um banco novo e vazio. O comando `pg_restore --clean` remove objetos existentes no esquema de destino. Não o execute contra o banco ativo nem contra um banco que contenha outros dados importantes.

1. Crie um banco de destino separado no Render e obtenha a URL externa dele.
2. Baixe e extraia o arquivo `.dir.tar.gz` em uma pasta privada.
3. Use `pg_restore` da versão principal compatível com o banco de destino, apontando para a URL externa do destino.
4. Valide as tabelas e os dados no destino antes de alterar `DATABASE_URL` do serviço.

Siga os comandos e requisitos atuais da documentação oficial do Render, pois os nomes das opções e as ferramentas PostgreSQL compatíveis podem mudar: [Render Postgres Recovery and Backups](https://render.com/docs/postgresql-backups).

## Voltar atrás após uma atualização de aplicativo

1. Se o deploy falhar antes de alterar o esquema, restaure a versão anterior do aplicativo pelo fluxo de deploy do Render.
2. Se a inicialização da nova versão já tiver alterado o esquema, não presuma que voltar o código reverte o banco. Pare novas alterações, preserve logs e use a cópia/PITR para preparar uma instância separada.
3. Valide a instância recuperada com a versão de aplicativo compatível antes de trocar a conexão do serviço.
4. Não apague a instância original ou a cópia de recuperação até confirmar que a aplicação está lendo e gravando os dados esperados.

## Segredos e configuração

O backup do banco não substitui o backup seguro de configuração. Preserve `SECRET_KEY` em um cofre de segredos com acesso restrito e mantenha-a estável: os segredos TOTP são criptografados com uma chave derivada dela. Uma cópia do banco sem a `SECRET_KEY` original não permite descriptografar os segredos MFA existentes. Nunca coloque `SECRET_KEY`, `DATABASE_URL`, códigos de recuperação ou exportações no GitHub, em capturas de tela ou neste repositório.

## Registro mínimo de cada operação

- Data e responsável.
- Banco/ambiente de origem e destino (nomes, sem URLs).
- Versão do aplicativo e motivo da operação.
- Tipo e horário do backup ou ponto de recuperação.
- Resultado da validação e decisão de manter/remover instâncias temporárias.
