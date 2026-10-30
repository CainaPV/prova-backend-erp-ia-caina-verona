





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
├── .env.example
├── Dockerfile
└── docker-compose.yml


- routers/: serve para organizar as rotas/endpoints da API. Evita misturar URL, requisição e regra de negócio no mesmo arquivo.
- schemas/: serve para validar os dados que chegam e saem da API. Por exemplo, verificar se um valor está no formato correto.
- models/: mantém a estrutura das tabelas do banco de dados organizada, como Pedido, Cliente e Produto.
- repositories/: fica responsável por fazer as consultas, cadastros, alterações e exclusões no banco de dados. Assim, o restante do sistema não precisa acessar o banco diretamente.
- services/: onde ficam as regras de negócio. Por exemplo: antes de criar um pedido, verificar o estoque, validar o cliente e calcular o valor total.
- core/: teria as configurações principais e que podem ser usadas por todo o projeto. Por exemplo: conexão com banco de dados, configurações do .env e autenticação.
- cache/: teria o redis.py, que serviria para evitar consultas desnecessárias no banco. Por exemplo, guardar temporariamente um produto muito acessado. Também poderia ser usado para fila ou comunicação assíncrona.
- workers/: teria arquivos para executar tarefas em segundo plano, como enviar e-mail, gerar relatório ou processar fila, sem travar a API.
- tests/: garante que novas alterações não quebrem funcionalidades que já existiam. Poderia separar testes das regras de negócio e testes das rotas da API.
- .env.example: mostra quais variáveis de ambiente o projeto precisa, sem expor senhas, tokens ou URLs reais.
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

### Parte 4: Docker, Orquestração e Entrega
### Questão 7.

Documente no README como subir tudo com um único comando (docker compose up) e como rodar as migrações/seed inicial, se houver;


### Parte 5: Desafio de IA (LLM / Agentes / MCP)
Como não integramos com APIs de LLM de terceiros em produção, o objetivo aqui é avaliar
seu entendimento de arquitetura e padrões de IA aplicada, não o uso de uma API
específica.
### Questão 9 (teórica/design — obrigatória mesmo que não implemente tudo). Descreva
como você desenharia isso de forma plugável para um LLM real no futuro, cobrindo:

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



