# Prova Prática — Back-end e IA

Este repositório contém as respostas teóricas desta prova e as implementações
práticas nas pastas `parte2-q4`, `parte3-q6`, `parte4-q7` e `parte5-q8`.

## Como executar as partes práticas

1. Entre na pasta da orquestração:

   ```bash
   cd parte4-q7
   ```

2. Na primeira execução, crie as imagens e inicie todos os serviços com um
   único comando:

   ```bash
   docker compose up --build
   ```

   Nas próximas execuções, basta usar:

   ```bash
   docker compose up
   ```

O Compose inicia a API de Produtos e Estoque na porta `8000`, a API assíncrona
da Parte 2 na porta `8001`, PostgreSQL, Redis e o worker RQ. Para encerrar, use
`docker compose down`.

Não há migrations ou seed nesta atividade. Ao iniciar, a API cria a tabela
`produtos` automaticamente com `Base.metadata.create_all()`. Portanto, não é
necessário executar nenhum comando adicional de migração ou carga inicial.

## Uso de IA

Utilizei IA como apoio para estudo, organização, revisão e validação das
respostas e do código. Todas as sugestões geradas foram revisadas ponto a ponto
antes de serem usadas. Ao final de cada questão, conferi manualmente o conteúdo,
adaptei o que fosse necessário e validei se a solução atendia ao enunciado.

### Parte 1: Arquitetura e Organização

**Questão 1:** usei IA para tornar a resposta mais clara e técnica. Também pedi
sugestões e exemplos sobre comunicação síncrona e assíncrona entre
microsserviços, além de validação e aprofundamento sobre API Gateway, logs e
tracing.

**Questão 2:** a IA ajudou a estruturar uma proposta de arquitetura de pastas a
partir do exemplo do enunciado. Também auxiliou na explicação da organização e
na revisão da resposta para deixá-la mais resumida e técnica.

### Parte 2: Assíncrono e Concorrência

**Questão 3:** consultei a IA sobre `threading` e `multiprocessing`, pedi
exemplos práticos e apoio para organizar a resposta de forma mais técnica.

**Questão 4:** pedi uma explicação do requisito com exemplos. A IA auxiliou na
montagem da função `async def consultar_servico(nome, service)`, incluindo a
lógica de timeout, tratamento de erros e retry. Depois adaptei a implementação
no arquivo da questão.

### Parte 3: API RESTful

**Questão 6:** pedi exemplos e revisão da configuração do banco de dados,
autenticação JWT e Redis. Também recebi apoio para estruturar de forma básica a
paginação, os filtros e o processo em fila para alerta de estoque baixo.

### Parte 4: Docker, Orquestração e Entrega

**Questão 7:** usei a IA para revisar a estrutura do Dockerfile. Para o
`docker-compose.yml`, recebi exemplos que foram combinados e adaptados à
estrutura do projeto. Também pedi apoio para documentar como iniciar os
serviços.

### Parte 5: Desafio de IA

**Questão 8:** pedi exemplos e apoio para criar o módulo de interpretação de
perguntas sobre o ERP. A implementação foi criada com esse auxílio e revisada
antes da finalização.

**Questão 9:** pedi revisão para tornar a resposta mais técnica e correta, com
sugestões de complementos quando necessário.

### Respostas das Questões Teóricas

### Parte 1: Arquitetura e Organização
#### QUESTÃO 1
Você foi contratado para desenhar a arquitetura de um novo módulo de um ERP (ex: módulo de Pedidos e Estoque), que precisa se comunicar com outros módulos já existentes (Financeiro, Clientes) via microsserviços.

● Como você organizaria os serviços (quais responsabilidades cada microsserviçoteri a e por quê);

### Resp.: 
Eu organizaria o módulo de ERP por domínios de negócio, separando as responsabilidades principais em microsserviços independentes. Dessa forma, cada serviço possui regras claras, pode evoluir sem impactar diretamente os demais e mantém seus próprios dados.

-Serviço de Clientes: responsável pelo cadastro e informações de cada cliente(POST /clientes), seja nome, CPF/CNPJ, endereço e situação cadastral, por exemplo.
  Consulta de clientes(GET /clientes/{client_id}).
  Esse serviço é separado porque essas informações podem ser utilizadas por diferentes módulos, como Pedidos e Financeiro.

-Serviço de Produtos e Estoque: responsável pelo cadastro de produtos(POST /produtos), consulta de disponibilidade(GET /produtos/{produto_id}/estoque), reserva(GET /produtos/{produto_id}/reserva) e baixa de estoque(POST /produtos/{produto_id}/baixas). 
  Ele concentra as regras relacionadas à quantidade disponível e movimentações, evitando que outros serviços alterem estoque diretamente.

-Serviço de Pedidos: responsável por criar(POST) e acompanhar pedidos(GET). Ele recebe os itens desejados pelo cliente(POST /pedidos), consulta os serviços necessários(GET  /clientes/3;POST /credito/validar;POST /estoque/reservas) e controla o status do pedido, como pendente, confirmado, pago ou cancelado(POST /pedidos/{pedido_id}/checkout). Esse serviço não deve calcular crédito nem controlar estoque internamente; ele apenas coordena o fluxo.

-Serviço Financeiro: responsável por validar limite de crédito(POST /financeiro/limite), gerar cobranças, registrar pagamentos e controlar informações financeiras. 
O serviço financeiro ficaria isolado porque possui regras mais sensíveis, como valores, faturas e pagamentos.

● Como seria a comunicação entre eles (síncrona via REST, assíncrona via fila, ambos?) e em que casos usaria cada uma;

### Resp.:
Eu utilizaria ambas(síncrona e assícrona). Via REST seria utilizado quando o serviço de Pedidos precisaria de uma resposta imediata para continuar o fluxo, como validar se o cliente está ativo ou consultar a disponibilidade de estoque. Pois ao meu ver, alguns serviços precisariam ter respostas imediatas antes de prosseguir para o outro fluxo por exemplo.
Na comunicação assíncrona, utilizaria filas para tarefas que não precisam bloquear a criação ou confirmação de um pedido. Por exemplo, após um pedido ser criado, o sistema pode enviar uma tarefa para um worker gerar uma notificação ao cliente, atualizar relatórios de vendas ou verificar se o estoque ficou abaixo do limite mínimo. Dessa forma, caso o serviço de notificações esteja indisponível, o pedido ainda poderá ser criado normalmente.
Para chamadas REST independentes que precisam de resposta imediata, utilizaria async/`await` e asyncio.gather no FastAPI. Isso permitiria consultar múltiplos serviços ao mesmo tempo.

● Onde entrariam PostgreSQL e Redis nessa arquitetura (cache, filas, pub/sub, locks distribuídos etc.);

### Resp.:
O PostgreSQL seria utilizado como banco de dados principal e persistente, armazenando entidades do domínio como clientes, produtos, pedidos, pagamentos e movimentações de estoque. Cada microsserviço seria responsável pelos próprios dados, evitando que um serviço altere diretamente as tabelas de outro.
O Redis seria utilizado como tecnologia complementar. Para cache, armazenaria temporariamente dados muito consultados, como informações de produtos e disponibilidade de estoque, reduzindo leituras repetidas no PostgreSQL. Também poderia ser usado como broker de filas para tarefas assíncronas, como envio de notificações, geração de relatórios e alertas de estoque baixo.

● O papel de um API Gateway (ex: Kong) nesse cenário;

### Resp.:
API Gateway seria utilizado como ponto único de entrada para clientes externos, frontend e integrações. Ele encaminharia as requisições ao microsserviço responsável, evitando que o consumidor precise conhecer os endereços internos de Clientes, Pedidos, Estoque e Financeiro. 

● Como você pensaria em observabilidade (logs, métricas, tracing) e cite ferramentas (ex: Prometheus/Grafana) e o que monitoraria como prioridade em um ERP;

### Resp.:
Para garantir a observabilidade do sistema, utilizaria logs estruturados para registrar eventos e erros importantes, como criação de pedidos, falhas na reserva de estoque e indisponibilidade do serviço Financeiro. 
Também utilizaria métricas para acompanhar números como tempo de resposta, quantidade de requisições e taxa de erros. 
Para identificar em qual serviço ocorreu uma lentidão ou falha, utilizaria tracing distribuído.
Ferramentas como Grafana já serviria para criar dashboards e alertas. 
Na minha opnião, como prioridade, eu monitoraria três fluxos críticos do ERP: criação de pedidos, estoque e financeiro. 
Esses serviços impactam diretamente a operação de venda; por isso, falhas ou lentidão neles podem impedir a conclusão de pedidos.
1. Criação de pedidos: taxa de sucesso, quantidade de falhas e tempo de resposta;
2. Estoque: tentativas de reserva com falha, tentativas de estoque negativo e alertas de estoque baixo;
3. Financeiro: falhas de pagamento, tempo de resposta e indisponibilidade do serviço.

### QUESTÃO 2
Descreva a estrutura de pastas/camadas que você usaria em um serviço FastAPI de médio/grande porte (ex: separação entre routers, services, repositories, schemas, models, core, tests). 
Explique o motivo de cada camada existir e como isso ajuda em testabilidade e manutenção. 
Cite quais princípios (SOLID,Clean Architecture, DDD leve, etc.) inspiraram sua escolha, se algum.

### Resp.:
Em um serviço FASTAPI de método/grande porte, eu organizaria e estruturaria dessa forma:

servico-fastapi/
├── app/
│   ├── main.py
│   ├── routers/
│   │   ├── pedidos.py
│   │   ├── estoque.py
│   │   └── clientes.py
│   ├── services/
│   │   ├── pedidos_service.py
│   │   ├── estoque_service.py
│   │   └── clientes_service.py
│   ├── repositories/
│   │   ├── pedidos_repository.py
│   │   ├── estoque_repository.py
│   │   └── clientes_repository.py
│   ├── schemas/
│   │   ├── pedido.py
│   │   ├── estoque.py
│   │   └── cliente.py
│   ├── models/
│   │   ├── pedido.py
│   │   ├── estoque.py
│   │   └── cliente.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── cache/
│   │   └── redis.py
│   └── workers/
│       ├── worker.py
│       └── tasks.py
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
└── docker-compose.yml


- routers/: serve para organizar as rotas/endpoints da API. Evita misturar URL, requisição e regra de negócio no mesmo arquivo.
- schemas/: serve para validar os dados que chegam e saem da API. Por exemplo, verificar se um valor está no formato correto.
- models/: mantém a estrutura das tabelas do banco de dados organizada, como Pedido, Cliente e Produto.
- repositories/: fica responsável por fazer as consultas, cadastros, alterações e exclusões no banco de dados. Assim, o restante do sistema não precisa acessar o banco diretamente.
- services/: onde ficam as regras de negócio. Por exemplo: antes de criar um pedido, verificar o estoque, validar o cliente e calcular o valor total.
- core/: teria as configurações principais e que podem ser usadas por todo o projeto. Por exemplo: conexão com banco de dados, variáveis de ambiente e autenticação.
- cache/: teria o redis.py, que serviria para evitar consultas desnecessárias no banco. Por exemplo, guardar temporariamente um produto muito acessado. Também poderia ser usado para fila ou comunicação assíncrona.
- workers/: teria arquivos para executar tarefas em segundo plano, como enviar e-mail, gerar relatório ou processar fila, sem travar a API.
- tests/: garante que novas alterações não quebrem funcionalidades que já existiam. Poderia separar testes das regras de negócio e testes das rotas da API.
- Dockerfile: padroniza o ambiente para a aplicação funcionar da mesma forma em qualquer computador ou servidor.
- docker-compose.yml: facilita iniciar a API junto com outros serviços, como PostgreSQL, Redis e worker.

Essa separação facilita a manutenção e os testes, pois cada pasta possui uma responsabilidade específica.

Sobre os princípios, conforme a estrutura apresentada acima eu seguiria a organização com base no SOLID(cada camada tem sua responsabilidade) e Clean Architecture(separar a regra de negócio das partes externas, como FastAPI, banco de dados, Redis e APIs externas) .


### Parte 2: Assíncrono e Concorrência
### QUESTÃO 3
Explique com suas palavras a diferença entre asyncio, threading e multiprocessing em Python, e quando usar cada um. Dê um exemplo real de cenário de ERP para cada abordagem (ex: chamar 3 APIs externas, processar um arquivo CSV grande, gerar um relatório pesado em PDF)

### Resp.:
As três servem para executar tarefas de forma simultânea, porém cada uma possui uma finalidade diferente.

Asyncio: permite que uma função espere uma operação de rede sem travar o restante da aplicação.
Ou seja, enquanto uma API está aguardando resposta do serviço Financeiro, por exemplo, ela pode continuar processando outras tarefas.Exemplo: asyncio.gather
Serviço de Pedidos
→ consulta Cliente
→ consulta Estoque
→ consulta Financeiro

Threading: ele é útil principalmente quando você precisa usar uma biblioteca bloqueante, ou seja, uma biblioteca que não possui suporte para async e await. Integração com impressoras e SDK legados.Exemplo:
Pedido confirmado
→ sistema precisa usar uma biblioteca antiga para imprimir etiqueta
→ essa biblioteca demora e bloqueia a execução
→ tarefa é enviada para uma thread


Multiprocessing:cada processo possui memória própria e pode usar mais de um núcleo do processador. Por isso, é adequado para tarefas que exigem bastante CPU. Ou seja, serve para processar CSV grandes, gerar relatórios PDF pesados e processamento de imagem e gráficos.
Exemplo:
Usuário solicita um relatório anual
→ sistema precisa ler um CSV com milhões de linhas
→ calcular vendas, impostos, produtos e gráficos
→ gerar PDF

### Parte 2: Assíncrono e Concorrência
### QUESTÃO 4 (prática)

Implementação: `parte2-q4/main.py`.

O endpoint `GET /consulta/{cliente_id}` consulta simultaneamente os serviços
simulados de estoque, financeiro e cliente. Ele usa `asyncio.gather`, timeout
individual com `asyncio.wait_for` e uma tentativa simples de retry. Caso uma
consulta falhe, a resposta dos outros serviços ainda é retornada junto com o
erro parcial.

Com o Docker Compose em execução, acesse:

```text
http://localhost:8001/consulta/1
```

### Parte 3: API RESTful — QUESTÃO 6 (prática)

Implementação: `parte3-q6/`.

A API de Produtos e Estoque usa FastAPI, Pydantic, PostgreSQL, SQLAlchemy
assíncrono e `asyncpg`. A escolha do SQLAlchemy facilita mapear a tabela
`produtos` para Python, enquanto o `asyncpg` evita bloquear as rotas assíncronas
durante o acesso ao PostgreSQL.

Ela possui CRUD completo, autenticação JWT, validação de nome, preço e estoque,
paginação e filtros por nome, faixa de preço e estoque baixo. Primeiro, faça
`POST /auth/login` com as credenciais configuradas no ambiente; depois envie o token no cabeçalho
`Authorization: Bearer <token>` para as rotas abaixo:

```text
POST   /produtos
GET    /produtos
GET    /produtos/{id}
PUT    /produtos/{id}
DELETE /produtos/{id}
```

A listagem de produtos fica em cache no Redis por 60 segundos. Quando um produto
é criado, alterado ou excluído, as chaves de listagem são removidas; assim, a
próxima leitura consulta o PostgreSQL e preenche o cache novamente. Produtos com
10 unidades ou menos geram uma tarefa na fila Redis `estoque`; o worker RQ
processa essa tarefa e registra o alerta de estoque baixo.

Documentação interativa da API: `http://localhost:8000/docs`.

### Parte 4: Docker, Orquestração e Entrega — QUESTÃO 7 (prática)

Implementação: `parte4-q7/Dockerfile` e `parte4-q7/docker-compose.yml`.

O Dockerfile tem um comando padrão para iniciar a API da Parte 3. No Compose,
esse comando é substituído quando necessário para iniciar o worker RQ e a API da
Parte 2. Os serviços de API, PostgreSQL, Redis e worker possuem healthchecks.
As variáveis sensíveis são fornecidas em tempo de execução e não são versionadas.

### Parte 5: Desafio de IA — QUESTÃO 8 (prática)

Implementação: `parte5-q8/app.py`.

O módulo não chama OpenAI, Anthropic ou outro provedor externo. Ele recebe uma
pergunta em `POST /perguntas`, aplica regras simples e gera uma ação estruturada.
Por exemplo, a pergunta `Quais produtos estão com estoque abaixo de 10 unidades?`
é convertida para `{"tipo": "estoque_abaixo_de", "limite": 10}`. Em seguida,
consulta a mesma tabela `produtos` da Parte 3 e devolve o resultado em JSON.

Para executar esse módulo separadamente, com o banco da Parte 3 disponível:

```bash
cd parte5-q8
pip install -r requirements.txt
uvicorn app:app --reload --port 8002
```

### Parte 5: Desafio de IA (LLM / Agentes / MCP)
Como não integramos com APIs de LLM de terceiros em produção, o objetivo aqui é avaliar
seu entendimento de arquitetura e padrões de IA aplicada, não o uso de uma API
específica.
### Questão 9 (teórica/design — obrigatória mesmo que não implemente tudo). 
Descreva como você desenharia isso de forma plugável para um LLM real no futuro, cobrindo:

● Como seria o tool/function calling (schema das ferramentas expostas ao agente: ex.
consultar_estoque, criar_pedido);

### Resp.:
Eu transformaria funções específicas do ERP em ferramentas MCP utilizando FastMCP. Por exemplo, poderia existir uma ferramenta chamada consultar_estoque, que receberia o produto_id como número inteiro e retornaria a quantidade disponível.
Cada ferramenta teria nome, descrição, parâmetros, tipo dos dados e campos obrigatórios. O FastMCP pode utilizar os tipos definidos na função para gerar esse schema automaticamente.
Exemplo: consultar_estoque(produto_id: int) ou criar_pedido(cliente_id: int, produtos: list).
Dessa forma, o agente entende quais ferramentas estão disponíveis, quais dados precisa enviar e qual serviço deve ser consultado.

● Se você usaria o padrão MCP (Model Context Protocol) para expor as ferramentas
do ERP a um agente e explique como um servidor MCP se encaixaria na arquitetura
de microsserviços que você desenhou na Parte 1;

### Resp.:
Eu utilizaria MCP para criar uma camada entre o agente e os microsserviços do ERP. 
Poderia existir um servidor MCP principal, com ferramentas separadas por domínio, como tools/clientes.py, tools/produtos.py, tools/estoque.py e tools/pedidos.py.
Cada ferramenta MCP chamaria a API ou service do microsserviço correto. Por exemplo, a ferramenta consultar_estoque chamaria o microsserviço de estoque.

● Guardrails: como evitar que o agente execute ações destrutivas (ex: deletar pedidos)
sem confirmação, e como lidar com alucinação/erro de interpretação;

### Resp.:
Eu não deixaria funções destrutivas, como deletar_pedido, disponíveis para o agente de forma automática.
Caso fosse necessário cancelar, atualizar ou excluir algum pedido, a ferramenta exigiria uma confirmação explícita do usuário antes da execução. 
Também utilizaria permissões por usuários e logs de todas as ações realizadas.
Eu poderia criar um arquivo system_prompt.md com regras para orientar o agente sobre quando usar cada ferramenta. Porém, as regras principais também precisariam ser validadas no próprio servidor MCP, pois o agente pode interpretar algo de forma errada.

● Considerações de custo, latência e observabilidade específicas de sistemas com
LLM (ex: logging de prompts/respostas, cache de respostas, fallback quando o
provedor de IA está fora do ar).

### Resp.:
Eu utilizaria Redis para criar caches temporários de consultas que acontecem com frequência, como consulta de produto ou estoque. Dessa forma, evita consultas desnecessárias ao banco de dados e reduz o tempo de resposta.
Dependendo da regra de negócio, também poderia utilizar uma arquitetura RAG para o agente consultar fontes internas, como documentos, manuais, políticas ou informações do ERP. Os dados poderiam ser armazenados em um banco vetorial, como o ChromaDB.
Dessa forma, em vez de enviar todos os dados internos para o LLM a cada pergunta, o sistema buscaria apenas as informações mais relevantes antes de gerar a resposta. Isso ajuda a reduzir tokens, custo e também diminui a chance de o agente responder algo incorreto.
Caso seja necessário responder perguntas muito parecidas com frequência, também poderia existir um cache de respostas, desde que os dados não sejam sensíveis ou mudem constantemente.
Para reduzir custos, eu evitaria enviar todo o histórico da conversa para o LLM e limitaria a quantidade de informações enviadas em cada requisição.
Eu registraria logs das chamadas do agente, ferramentas utilizadas, erros, tempo de resposta e quantidade de tokens utilizados. Em produção, esses logs poderiam ser enviados para uma ferramenta de monitoramento, além de aparecerem no terminal.


### Parte 6: Pergunta de Perfil
### Questão 10. 
Imagine a seguinte situação real: nosso stack principal é Python, mas identificamos que uma frente específica do produto (ex: um serviço de alta performance
para ingestão/processamento de grandes volumes de eventos do ERP, com baixa latência e alto throughput) se beneficiaria de ser escrita em Go.
Você seria alocado(a) para desenvolver essa frente em Go.
● Como você reagiria a essa decisão?

### Resp.:
Atualmente eu ainda não utilizei Go em projetos, porém encararia a decisão de forma positiva. No começo eu precisaria de um período de adaptação, pois já programo há mais tempo em Python.
Mesmo assim, por já possuir base em lógica, funções, classes, APIs, arquitetura e banco de dados, acredito que conseguiria aprender a linguagem e contribuir com o projeto. Eu entenderia que a escolha de Go seria para uma necessidade específica de performance, e não para substituir Python em todo o sistema.

● Você acha Go uma escolha razoável para esse cenário específico (alta concorrência, baixo overhead, binário único para deploy)? Por quê ou por que não?

### Resp.:
Sim, considero Go uma escolha razoável para esse cenário. Go é uma linguagem que possui baixo consumo de recursos e facilita trabalhar com várias tarefas ao mesmo tempo.
Para um serviço que recebe e processa muitos eventos, com baixa latência e alto volume de requisições, Go pode trazer ganhos de desempenho.
Python também poderia ser utilizado, principalmente com asyncio, filas e múltiplos workers. Porém, se a necessidade de concorrência e performance for realmente alta, Go pode ser uma escolha mais adequada para esse serviço específico.

● Se você discordasse da escolha, como argumentaria tecnicamente a favor de outra linguagem/abordagem?

### Resp.:
Caso eu discordasse, eu não discordaria apenas por não conhecer a linguagem. Eu analisaria o volume real de eventos, a latência esperada, os custos e os gargalos atuais do sistema.
Se Python com asyncio, filas, Redis ou Kafka e mais de um worker já atendesse aos requisitos, eu argumentaria que talvez não fosse necessário adicionar outra linguagem ao projeto, pois isso também aumenta a complexidade de manutenção.
Para tomar essa decisão com mais segurança, eu criaria uma pequena pauta de conceito com ajuda da IA e faria testes de carga no início do projeto. 
Assim, seria possível comparar o desempenho das abordagens e escolher a melhor linguagem que atende aos requisitos dentro do prazo definido.

● Se concordasse, mas não tivesse experiência prévia com Go, como se organizaria para aprender e entregar com qualidade?

### Resp.:
Primeiramente, eu estudaria os fundamentos de Go, como, interfaces, tratamento de erros, goroutines, channels e context. 
Também assistiria a videoaulas para reforçar o aprendizado.
Pesquisaria a documentação oficial, exemplos parecidos com o projeto e tiraria dúvidas com pessoas mais experientes e com IA. 

### Parte 7: Portfólio
### Questão 11. 
Envie link(s) do seu GitHub/GitLab com projetos anteriores ou pessoais relevantes (se houver). 
Escolha um projeto que considere mais representativo do seu nível técnico e explique brevemente:
Links: 
https://github.com/CainaPV/Cars.git
https://github.com/CainaPV/ChatBot_AI.git
https://github.com/CainaPV/Auto_Process.git
https://github.com/CainaPV/MCP_Server_Tavily_Search.git
https://github.com/CainaPV/ChatBot-WhatsApp.git

Projeto escolhido: ChatBot-WhatsApp

● Qual problema ele resolve;
### Resp.:
O ChatBot-WhatsApp, ainda em desenvolvimento, tem como objetivo atender clientes
pelo WhatsApp, identificar o assunto da mensagem e direcioná-lo ao setor
responsável. Ele também pode responder dúvidas iniciais e orientar o cliente.

● Principais decisões técnicas e por quê;
### Resp.:
A principal decisão técnica foi criar uma API assíncrona com FastAPI para organizar
a comunicação do chatbot e facilitar futuras integrações. Inicialmente, utilizei
uma integração não oficial com o WhatsApp para desenvolver e testar o protótipo.
Porém, reconheço que esse tipo de integração pode exigir renovação de sessão e
trazer riscos de manutenção. Em uma versão de produção, eu avaliaria utilizar a
API oficial do WhatsApp para obter mais estabilidade.
Também estou ajustando os fluxos de atendimento para que as mensagens sejam mais
naturais e adequadas ao contexto de cada setor.

● O que você faria diferente hoje, com o que aprendeu desde então.
### Resp.:
Com o que aprendi desde o início do projeto, eu criaria ferramentas MCP para o
agente consultar informações específicas, como status de pedido, dados do cliente
ou disponibilidade de produtos. Isso daria ao agente mais recursos, mantendo as
ações organizadas, validadas e limitadas pelas permissões do sistema.
