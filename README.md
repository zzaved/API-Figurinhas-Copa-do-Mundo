# API de Figurinhas da Copa do Mundo 2026

## Introdução

Este repositório contém uma API REST desenvolvida como parte da Atividade Ponderada 3 da disciplina ministrada pelo professor Murilo Zanini. O objetivo era construir uma API para gerenciar figurinhas da Copa do Mundo 2026 aplicando os princípios de Clean Code, separação de responsabilidades em camadas, interfaces para desacoplamento, injeção de dependência e erros de domínio nomeados.

O projeto foi desenvolvido em dupla por **Cecília Galvão** e **Pablo Azevedo**. A divisão foi a seguinte: Cecília ficou responsável pelo Domain, pelo Service e pelos testes; Pablo ficou responsável pelo Repository, pelo Handler e pela composição final no `main.py`. Essa divisão não foi aleatória, cada um ficou com as camadas que se complementam conceitualmente: Cecília trabalhou com o núcleo do sistema, as regras e a verificação delas; Pablo trabalhou com as bordas, a infraestrutura e a cola que une tudo.

Esta documentação tem duas funções. A primeira é técnica: explicar como rodar o projeto, qual é o contrato da API e como a arquitetura foi organizada. A segunda é narrativa, conforme solicitado: registrar, fase a fase, o que planejamos, quais problemas encontramos, como resolvemos e o que ficou de fora por falta de tempo.

---

## Sumário

- [API de Figurinhas da Copa do Mundo 2026](#api-de-figurinhas-da-copa-do-mundo-2026)
  - [Introdução](#introdução)
  - [Sumário](#sumário)
  - [Stack](#stack)
  - [Como rodar localmente](#como-rodar-localmente)
  - [Como rodar os testes](#como-rodar-os-testes)
  - [Contrato da API](#contrato-da-api)
    - [Exemplos com `curl`](#exemplos-com-curl)
  - [A entidade Figurinha](#a-entidade-figurinha)
  - [Regras de negócio](#regras-de-negócio)
  - [Arquitetura em camadas](#arquitetura-em-camadas)
  - [Estrutura de pastas](#estrutura-de-pastas)
  - [A jornada de construção](#a-jornada-de-construção)
    - [Fase 0 — O plano antes do código](#fase-0--o-plano-antes-do-código)
    - [Fase 1 — A fundação](#fase-1--a-fundação)
    - [Fase 2 — O Domain](#fase-2--o-domain)
    - [Fase 3 — O Repository](#fase-3--o-repository)
    - [Fase 4 — O Service](#fase-4--o-service)
    - [Fase 5 — O Handler](#fase-5--o-handler)
    - [Fase 6 — A composição e os problemas que só aparecem ao rodar](#fase-6--a-composição-e-os-problemas-que-só-aparecem-ao-rodar)
    - [Fase 7 — Os testes](#fase-7--os-testes)
  - [O que ficou de fora](#o-que-ficou-de-fora)
  - [Conclusão](#conclusão)

---

## Stack

| Camada do Clean Code | Ferramenta |
|---|---|
| Apresentação (Handler) | FastAPI |
| Contratos de entrada/saída (DTOs) | Pydantic |
| Negócio (Service) | Python puro |
| Dados (Repository) | SQLAlchemy + SQLite |
| Interfaces / desacoplamento | `abc.ABC` |
| Testes | pytest |

Requer **Python 3.10 ou superior**. O motivo está documentado na Fase 6.

---

## Como rodar localmente

```bash
git clone https://github.com/zzaved/API-Figurinhas-Copa-do-Mundo.git
cd API-Figurinhas-Copa-do-Mundo

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

O servidor sobe em `http://127.0.0.1:8000`.

A documentação interativa (Swagger) fica em `http://127.0.0.1:8000/docs`, onde é possível testar todos os endpoints pelo navegador.

O banco SQLite (`figurinhas.db`) é criado automaticamente na primeira execução.

---

## Como rodar os testes

Com o ambiente virtual ativado:

```bash
python -m pytest
```

A suíte testa as regras de negócio do Service usando um repositório falso em memória (`FakeFigureRepository`), sem subir banco nem servidor. É a prova prática de que as camadas estão desacopladas pelas interfaces.

---

## Contrato da API

| Método | Rota | Corpo / Query | Respostas |
|---|---|---|---|
| POST | `/figurinha` | `CreateFigureRequest` (JSON) | 201 · 400 |
| GET | `/figurinha` | filtro opcional `?posicao=` ou `?tipo=` | 200 · 400 |
| GET | `/figurinha/{id}` | — | 200 · 404 |
| PUT | `/figurinha/{id}` | `UpdateFigureRequest` (JSON) | 200 · 400 · 404 |
| DELETE | `/figurinha/{id}` | — | 204 · 404 |

### Exemplos com `curl`

```bash
curl -X POST http://127.0.0.1:8000/figurinha \
  -H "Content-Type: application/json" \
  -d '{"numero": "BRA 15", "tipo": "comum", "posicao": "Atacante"}'

curl http://127.0.0.1:8000/figurinha

curl "http://127.0.0.1:8000/figurinha?posicao=Atacante"

curl http://127.0.0.1:8000/figurinha/1

curl -X PUT http://127.0.0.1:8000/figurinha/1 \
  -H "Content-Type: application/json" \
  -d '{"numero": "BRA 16", "tipo": "legends_ouro", "posicao": "Zagueiro"}'

curl -X DELETE http://127.0.0.1:8000/figurinha/1
```

Erros de negócio retornam sempre no formato `{"error": "mensagem"}`. Por exemplo, ao buscar um id inexistente:

```json
{"error": "figurinha não encontrado"}
```

---

## A entidade Figurinha

| Campo | Tipo | Observação |
|---|---|---|
| `id` | inteiro | gerado pelo banco |
| `numero` | string | código no álbum (ex: `"BRA 15"`, `"FWC 02"`) |
| `tipo` | enum | `comum`, `brilhante`, `legends_ouro`, `legends_bronze` |
| `posicao` | enum | `Goleiro`, `Zagueiro`, `Meio-campista`, `Atacante` |
| `created_at` | datetime | preenchido automaticamente na criação |
| `updated_at` | datetime | atualizado a cada alteração |

---

## Regras de negócio

Todas vivem na camada **Service**, nunca no Handler:

- Todos os campos (`numero`, `tipo`, `posicao`) são obrigatórios na criação e na atualização.
- `tipo` precisa ser um dos quatro valores válidos, validado na criação, na atualização e no filtro da listagem.
- `posicao` precisa ser uma das quatro posições válidas, mesma validação.
- `created_at` é preenchido com `datetime.now()` na criação. O cliente não pode definir nem alterar esse campo. Na atualização ele é preservado e somente o `updated_at` muda.
- Buscar, atualizar ou deletar um id inexistente retorna **404** com o corpo `{"error": "figurinha não encontrado"}`.

---

## Arquitetura em camadas

A comunicação segue uma direção única: de cima para baixo. Cada camada conhece apenas a camada imediatamente abaixo dela.

```
Cliente HTTP
     │  JSON
     ▼
┌─────────────────────────────────────────────┐
│  HANDLER  (FastAPI)                          │
│  Recebe a requisição, repassa ao Service e   │
│  traduz o resultado/erro em resposta HTTP.   │
└───────────────────┬──────────────────────────┘
                    │  DTO
                    ▼
┌─────────────────────────────────────────────┐
│  SERVICE                                     │
│  Aplica as regras de negócio e orquestra a   │
│  operação. Não conhece HTTP nem SQL.         │
└───────────────────┬──────────────────────────┘
                    │  Entidade Figurinha
                    ▼
┌─────────────────────────────────────────────┐
│  REPOSITORY  (SQLAlchemy)                    │
│  Persiste e recupera. Traduz o modelo do     │
│  banco para a entidade de domínio.           │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
              [ SQLite ]
```

O **Domain** é a camada transversal: define a entidade, os enums, os DTOs e os erros. Todas as camadas o conhecem, mas ele não conhece ninguém.

Os erros sobem na direção contrária: o Service lança erros de domínio (`FigurinhaNaoEncontrada`, `CampoObrigatorio`, `TipoInvalido`, `PosicaoInvalida`) e um tratador centralizado no Handler os mapeia para o status HTTP correto.

---

## Estrutura de pastas

```
app/
├── main.py                     ← composição: monta as peças e sobe o servidor
├── domain/
│   ├── enums.py                ← TipoFigurinha, PosicaoFigurinha
│   ├── figurinha.py            ← entidade Figurinha (dataclass pura)
│   ├── dto.py                  ← CreateFigureRequest, UpdateFigureRequest, FigureResponse
│   └── errors.py               ← erros de domínio nomeados
├── repository/
│   ├── database.py             ← engine, sessão e criação de tabelas
│   ├── models.py               ← FigurinhaModel (mapeamento SQLAlchemy)
│   └── figure_repository.py    ← interface + implementação SQLite
├── service/
│   └── figure_service.py       ← interface + regras de negócio
└── handler/
    └── figure_handler.py       ← rotas HTTP + tradução de erros
tests/
├── fake_repository.py          ← repositório falso em memória
└── test_figure_service.py      ← testes das regras de negócio
```

---

## A jornada de construção

Esta seção é a memória do projeto. A intenção desde o início era nunca cair na armadilha do arquivo único onde tudo se mistura, aquele tipo de código que funciona no dia em que é escrito e vira um problema em todas as vezes seguintes. Cada fase abaixo registra o que queríamos fazer, o problema que apareceu, como decidimos resolvê-lo e o raciocínio por trás de cada escolha.

### Fase 0 — O plano antes do código

Antes de escrever qualquer linha, nós dois paramos para definir o que queríamos de fato construir. A tentação em qualquer projeto com prazo é abrir o editor e começar, e foi exatamente essa tentação que resistimos.

A primeira decisão foi a linguagem. Python não foi uma escolha óbvia desde o início: cogitamos Go, porque o material de referência do enunciado usava Go com Gin e GORM, e Java, porque ambos temos alguma familiaridade com Spring. Descartamos Go pela curva de aprendizado num prazo curto e Java pela verbosidade que tornaria difícil enxergar a arquitetura por trás do código. Python foi escolhido porque permite escrever as camadas de forma limpa e legível, e porque FastAPI, Pydantic e SQLAlchemy formam um conjunto que mapeia naturalmente as mesmas intenções que Gin, structs e GORM expressam em Go.

A segunda decisão foi a ordem de construção: do núcleo para fora. Primeiro o Domain, depois Repository, Service e Handler, e por fim o `main.py` costurando tudo. Cada camada só poderia começar depois que a anterior estivesse estável. Isso nos forçou a pensar nas interfaces antes das implementações, o que é exatamente o ponto.

A terceira decisão foi sobre o `requirements.txt`: preenchê-lo de forma incremental, biblioteca por biblioteca, conforme cada uma fosse de fato importada. Parece detalhe, mas era uma forma de manter o arquivo honesto sobre o que o projeto usa e por quê.

### Fase 1 — A fundação

Antes de qualquer código funcional, criamos a estrutura de pastas e os arquivos base. Cada pasta nasceu representando uma pergunta específica: `domain` — o que existe no sistema? `repository` — como guardamos? `service` — o que pode ser feito? `handler` — como respondemos?

Essa separação física foi intencional. Quando a estrutura de pastas reflete a arquitetura, qualquer pessoa que abra o repositório pela primeira vez consegue entender a intenção do projeto antes mesmo de ler uma linha de código.

### Fase 2 — O Domain

**Responsável: Cecília**

O Domain foi a fase que mais exigiu pensar antes de escrever. Era preciso definir a entidade `Figurinha`, os enums, os DTOs e os erros, tudo isso sem depender de HTTP, banco ou qualquer framework. O Domain precisava ser puro.

**A decisão sobre a entidade.** A pergunta central foi: a entidade e o corpo que a API recebe devem ser a mesma coisa? A resposta imediata seria sim, menos código, menos complexidade. Mas percebemos o problema: se usássemos a entidade diretamente como entrada, o cliente poderia enviar um `id` ou um `created_at` arbitrário e sobrescrever campos que o servidor deveria controlar. Isso é um problema clássico de mistura de camadas, a borda externa contamina o núcleo.

A solução foi separar. A `Figurinha` virou uma `dataclass` pura, sem conhecimento de HTTP ou banco. Os DTOs (`CreateFigureRequest`, `UpdateFigureRequest`) passaram a ser a fronteira de entrada, definindo exatamente o que o cliente tem permissão de informar.

**A decisão sobre os erros.** A primeira ideia foi lançar exceções genéricas com strings descritivas, como `raise Exception("campo obrigatório")`. O problema é que strings são frágeis — qualquer refatoração no texto quebraria o código que depende delas. Optamos por criar classes nomeadas para cada erro de domínio: `FigurinhaNaoEncontrada`, `CampoObrigatorio`, `TipoInvalido`, `PosicaoInvalida`. Com isso, o Handler poderia mapear erros por identidade de tipo, não por conteúdo de texto, o que é muito mais robusto.

**Um detalhe do enunciado.** O enunciado continha resíduos de uma versão anterior de outra API, mencionava `UpdateExpenseRequest`, `category`, `date` e "cinco valores válidos" para o tipo, embora a tabela listasse quatro. Adaptamos tudo para o domínio de figurinhas e seguimos os quatro tipos efetivamente especificados, registrando essa decisão aqui de forma explícita para não deixar dúvida sobre a interpretação que fizemos.

### Fase 3 — O Repository

**Responsável: Pablo**

O objetivo era isolar completamente o acesso ao banco atrás de uma interface, de forma que nenhuma camada acima precisasse saber que o SQLAlchemy existe.

**A decisão sobre a interface.** Antes de escrever qualquer código de banco, definimos a interface `FigureRepository` com `abc.ABC`. Essa ordem foi deliberada: primeiro o contrato, depois a implementação. Isso garantiu que o Service, quando fosse escrito, dependesse da abstração e não do SQLAlchemy, o que é exatamente o que torna os testes possíveis sem banco real.

**O problema da conexão global.** O caminho mais curto seria abrir uma conexão global com o banco e acessá-la de qualquer ponto do código. Identificamos isso como um dos piores padrões possíveis: uma variável global mutável cria dependências invisíveis entre partes do sistema que deveriam ser independentes, e torna impossível testar qualquer coisa de forma isolada. A solução foi fazer a `SqlAlchemyFigureRepository` receber a fábrica de sessão pelo construtor — injeção de dependência simples e explícita.

**A decisão sobre o comportamento com registros não encontrados.** Discutimos se o repositório deveria lançar uma exceção quando não encontrasse um registro, ou devolver `None`. Optamos por `None`. O raciocínio foi que o repositório é infraestrutura, ele não tem como saber se "não encontrado" é um erro de negócio ou um comportamento esperado. Quem toma essa decisão é o Service.

**O mapeamento entre modelo e entidade.** Criamos um mapeamento explícito entre o `FigurinhaModel` (o modelo interno do SQLAlchemy) e a entidade `Figurinha`. Sem isso, o modelo do banco vazaria para as camadas superiores, criando um acoplamento que tornaria impossível trocar o banco no futuro sem mexer em todo o sistema.

### Fase 4 — O Service

**Responsável: Cecília**

O Service foi a fase que gerou mais discussão entre nós dois, porque foi aqui que a principal tensão arquitetural do projeto apareceu.

**O problema do Pydantic.** O Pydantic é poderoso o suficiente para validar tudo automaticamente: bastaria tipar os campos dos DTOs diretamente como enums e ele rejeitaria entradas inválidas durante o parsing, antes mesmo de chegar ao Service. A questão é que essa rejeição aconteceria dentro do Handler, com status 422, e o enunciado era explícito, as validações precisam estar na camada Service.

Discutimos se isso não seria simplesmente uma exigência formal sem consequência prática. Chegamos à conclusão de que tem consequência sim: se a regra de negócio vive no Handler, ela some quando a lógica é reaproveitada em outro contexto, uma CLI, um worker assíncrono, um script de importação. Nesses casos, não há Handler. A validação precisava estar onde a lógica está, não onde o HTTP está.

**A solução.** Deixamos os DTOs propositalmente permissivos (`str | None`) e colocamos o Service como o único responsável pelas validações. É ele quem verifica campos obrigatórios, valida `tipo` e `posicao` contra os enums e lança os erros de domínio com mensagens claras, resultando em **400**.

**A decisão sobre o PUT.** Como o método é PUT, tratamos a atualização como substituição completa, todos os campos são exigidos, sem exceção. O `created_at` é preservado do registro original e o `updated_at` é renovado com `datetime.now()`. O cliente nunca controla os timestamps, isso é regra de negócio, não decisão do consumidor da API.

### Fase 5 — O Handler

**Responsável: Pablo**

O Handler é a camada que mais parece simples e que mais esconde armadilhas.

**O problema da repetição.** A primeira versão mental de cada rota tinha seu próprio bloco `try/except` para capturar erros e transformá-los em respostas HTTP. Com cinco rotas, isso seria cinco lugares para lembrar de atualizar quando surgisse um novo tipo de erro. Era o princípio "não se repita" sendo violado antes mesmo de escrever o código.

**Como resolvemos.** Centralizamos o mapeamento de erros em um único tratador registrado na aplicação. Os métodos do Handler ficaram enxutos: chamam o Service e devolvem o resultado. Quando um erro de domínio sobe, um único lugar decide o status HTTP (404 para `FigurinhaNaoEncontrada`, 400 para os demais) e formata o corpo no padrão `{"error": ...}` exigido pelo enunciado — e não o `{"detail": ...}` padrão do FastAPI.

**A decisão sobre a serialização.** Para converter a entidade `Figurinha` no DTO de saída `FigureResponse`, habilitamos a leitura por atributos no modelo Pydantic. Sem isso, o Pydantic tentaria tratar a entidade como um dicionário e falharia silenciosamente.

### Fase 6 — A composição e os problemas que só aparecem ao rodar

**Responsável: Pablo**

No `main.py` montamos tudo: criamos o banco, injetamos o repositório no Service e o Service no Handler, registramos o tratador de erros e subimos o servidor. Foi ao rodar pela primeira vez que dois problemas concretos apareceram, nenhum deles visível nas fases anteriores.

**Problema 1 — a sintaxe de tipos quebrou.** Ao subir a aplicação, recebemos um `TypeError: unsupported operand type(s) for |`. O Python padrão da máquina era o 3.9.6, e a sintaxe `str | None` só funciona em tempo de execução a partir do Python 3.10. Tínhamos duas saídas: reverter tudo para `Optional[str]`, compatível com o 3.9, ou exigir um Python mais novo. Como havia um Python 3.13 instalado e a sintaxe moderna deixa o código mais legível, decidimos exigir **Python 3.10+** e documentar esse requisito de forma explícita.

**Problema 2 — o SQLite e as múltiplas threads.** Com o servidor em execução, o SQLite reclamou de conexões sendo usadas entre threads diferentes. O Uvicorn atende requisições síncronas em um pool de threads, e conexões do pool acabam migrando entre elas. A correção foi configurar o engine com `check_same_thread=False`. Não foi uma solução inventada, é um ajuste documentado e padrão para quem usa SQLite com servidores web. Mas levamos um tempo para identificar a origem do erro antes de chegar nessa solução.

**A verificação final.** Com tudo em funcionamento, testamos os endpoints de ponta a ponta: criação válida (201), campo faltando (400 com mensagem clara), tipo inválido (400), listagem com e sem filtro, busca por id, id inexistente (404), atualização preservando o `created_at`, e remoção (204). Verificamos também, lendo a tabela diretamente pelo SQLite, que os dados realmente persistiram em disco. Todos os cenários do contrato passaram.

### Fase 7 — Os testes

**Responsável: Cecília**

Com a API funcionando, o objetivo era provar que a arquitetura realmente entregava a testabilidade prometida desde a Fase 0.

**O problema.** Testar regras de negócio normalmente exige subir banco e servidor. Se o Service dependesse diretamente do SQLAlchemy, não haveria como isolá-lo, qualquer teste seria lento, frágil e dependente de estado externo.

**Como resolvemos.** Como o Service depende da interface `FigureRepository` e não da implementação concreta, criamos um `FakeFigureRepository` que guarda tudo em um dicionário em memória. Com ele, escrevemos uma suíte em pytest que valida todas as regras — campos obrigatórios, tipo e posição inválidos, id inexistente, filtro da listagem e a preservação do `created_at` no update, rodando em milissegundos, sem nenhum banco real.

Foi a confirmação prática de que as camadas estavam de fato desacopladas. O Service não sabia, e não precisava saber, se estava falando com o SQLite ou com um dicionário em memória. A interface garantiu isso.

---

## O que ficou de fora

Nem tudo que planejamos foi implementado. Registramos aqui o que ficou de fora, tanto por honestidade quanto para deixar claro o que o projeto ainda poderia ser.

**Interface visual simples.** Desde o início da Fase 0, cogitamos construir uma tela HTML simples, sem framework, só HTML, CSS e JavaScript puro, que consumisse a API e permitisse visualizar o álbum de figurinhas de forma mais intuitiva do que o Swagger. A ideia era ter uma grade com as figurinhas cadastradas, filtros por posição e tipo, e um formulário para adicionar novas. Chegamos a esboçar a estrutura em rascunho, mas o tempo não permitiu. A integração entre frontend e backend, mesmo que simples, exigiria resolver CORS, tratar os estados de loading e erro na interface, e garantir que a experiência fizesse sentido, e isso, feito com cuidado, levaria mais tempo do que tínhamos disponível. Optamos por entregar a API bem feita a entregar a tela pela metade.

**Testes de integração.** Os testes que escrevemos são unitários, testam o Service isolado, sem banco. Queríamos também escrever testes de integração que subissem a aplicação completa com um banco SQLite em memória e testassem os endpoints de ponta a ponta via HTTP. Isso daria uma cobertura muito mais completa. Não chegamos a implementar por conta do prazo, mas a arquitetura está preparada para isso, bastaria configurar um `TestClient` do FastAPI com um banco de teste injetado.

---

## Conclusão

Este projeto cumpriu o que se propôs: uma API funcional, com camadas bem separadas, regras de negócio no lugar certo e testes que provam o desacoplamento sem depender de banco real.

Ao longo das fases, as decisões mais importantes não foram as técnicas, foram as de resistir ao caminho mais curto. Não usar variável global de banco, não deixar o Pydantic validar no lugar do Service, não repetir o `try/except` em cada rota. Cada uma dessas escolhas custou um pouco mais de tempo na hora e economizou retrabalho nas fases seguintes.

O que ficou de aprendizado prático: arquitetura em camadas não é sobre seguir um diagrama bonito, é sobre conseguir mudar uma parte do sistema sem precisar tocar nas outras. Quando os testes rodaram sem banco e sem servidor, ficou claro que isso tinha funcionado.
