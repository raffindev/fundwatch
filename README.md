# FundWatch

**Plataforma de ingestão, validação e consulta de dados históricos de fundos de investimento.**

![Python](https://img.shields.io/badge/Python-Backend-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Planejado-009688?logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-orange)

> **Status:** Em desenvolvimento — fase de análise e especificação.
>
> **Idioma:** Português brasileiro. Uma versão em inglês da documentação será disponibilizada futuramente.

---

## Sobre o projeto

O **FundWatch** é um projeto backend desenvolvido em Python, voltado ao processamento e à disponibilização de dados públicos de fundos de investimento brasileiros.

A plataforma utilizará informações oficiais da Comissão de Valores Mobiliários (CVM), transformando arquivos periódicos em dados históricos estruturados, persistentes e consultáveis por meio de uma API REST.

O objetivo é construir uma solução funcional, testável e reproduzível, aplicando práticas de engenharia de software ao tratamento de dados financeiros.

## O problema

A utilização recorrente de dados públicos de fundos de investimento pode exigir processos manuais de obtenção, leitura, validação e consolidação de arquivos.

Esses processos apresentam desafios como:

- Repetição de atividades de importação e preparação dos dados.
- Dificuldade de consulta em grandes volumes de registros.
- Risco de inconsistências e registros incompletos.
- Duplicação de informações durante reprocessamentos.
- Necessidade de tratar correções e reapresentações da fonte.
- Dificuldade de rastrear falhas e resultados das importações.

O FundWatch propõe centralizar essas responsabilidades em um serviço backend, reduzindo a dependência de manipulações manuais e estabelecendo mecanismos verificáveis de integridade e rastreabilidade.

Para uma análise detalhada, consulte a [Definição do Problema](docs/product/problem-statement.md).

## Funcionalidades previstas

A primeira versão (V1) terá como objetivo implementar:

| Funcionalidade          | Descrição                                            |
| ----------------------- | ---------------------------------------------------- |
| Ingestão de dados       | Processamento de arquivos oficiais da CVM            |
| Validação               | Verificação de estrutura, tipos e consistência       |
| Tratamento de rejeições | Identificação de registros inválidos e seus motivos  |
| Persistência histórica  | Armazenamento normalizado em PostgreSQL              |
| Idempotência            | Reprocessamento sem duplicação de registros          |
| Atualizações            | Tratamento de registros corrigidos ou reapresentados |
| Consultas históricas    | Pesquisa por fundo e intervalo de datas              |
| Rastreabilidade         | Histórico de execuções e resultados de importação    |
| API REST                | Disponibilização de consultas documentadas           |

**Importante:** as funcionalidades acima representam o escopo planejado da V1 e ainda não estão disponíveis para utilização.

A especificação detalhada encontra-se em [Requisitos do Sistema](docs/product/requirements.md).

## Fonte de dados

O FundWatch utilizará como fonte primária o conjunto de dados públicos **Informe Diário de Fundos de Investimento**, disponibilizado pela CVM.

**Fonte oficial:**  
https://dados.cvm.gov.br/dataset/fi-doc-inf_diario

Os arquivos contêm informações como:

- Identificação de fundo/classe e subclasse.
- Data de competência.
- Patrimônio líquido.
- Valor da cota.
- Valor total da carteira.
- Captações e resgates.
- Número de cotistas.

A estrutura, a cobertura, as atualizações e as condições de utilização dos dados serão consideradas durante a implementação.

O FundWatch é um projeto independente, sem vínculo institucional ou endosso da CVM.

## Tecnologias

A arquitetura prevista utilizará:

| Tecnologia     | Finalidade                         |
| -------------- | ---------------------------------- |
| Python         | Linguagem principal                |
| PostgreSQL     | Persistência de dados              |
| FastAPI        | Desenvolvimento da API REST        |
| pytest         | Testes automatizados               |
| Docker Compose | Execução reproduzível dos serviços |
| GitHub Actions | Integração contínua                |

A seleção de bibliotecas complementares será realizada conforme as necessidades concretas da implementação.

## Arquitetura prevista

O fluxo principal de processamento será:

```text
       Fonte oficial CVM
               |
               v
        Leitura de arquivos
               |
               v
       Validação de dados
               |
               v
     Normalização e regras
            de negócio
               |
               v
           PostgreSQL
               |
               v
           API REST
               |
               v
      Aplicações consumidoras
```

O processamento também deverá produzir informações sobre registros rejeitados, atualizados e eventuais falhas de execução.

A arquitetura definitiva e as decisões técnicas serão documentadas conforme o desenvolvimento avançar.

## Estrutura do repositório

A estrutura atual da documentação é:

```text
fundwatch/
├── docs/
│   └── product/
│       ├── problem-statement.md
│       └── requirements.md
├── .gitignore
└── README.md
```

A estrutura será expandida progressivamente para incluir código-fonte, testes, documentação de domínio e decisões arquiteturais.

Não serão criados módulos ou diretórios sem responsabilidades definidas.

## Documentação

| Documento                                                   | Conteúdo                                            |
| ----------------------------------------------------------- | --------------------------------------------------- |
| [Definição do Problema](docs/product/problem-statement.md)  | Contexto, público-alvo, problema e solução proposta |
| [Especificação de Requisitos](docs/product/requirements.md) | Requisitos, regras de negócio e critérios de aceite |

Novos documentos serão adicionados conforme a modelagem, a arquitetura e a implementação evoluírem.

## Desenvolvimento e execução

O FundWatch encontra-se na fase inicial de análise e especificação.

A aplicação ainda não possui uma versão executável.

As instruções de instalação, configuração do ambiente, execução da API, importação de dados e utilização do Docker Compose serão incluídas quando essas funcionalidades estiverem implementadas e verificadas.

## Estratégia de qualidade

O desenvolvimento será orientado por:

- Separação de responsabilidades.
- Integridade e precisão dos dados.
- Tratamento explícito de erros.
- Testes unitários e de integração.
- Reprocessamento idempotente.
- Documentação de decisões técnicas.
- Versionamento organizado em branches.
- Integração contínua.

Os requisitos deverão possuir critérios de aceite verificáveis, permitindo relacionar funcionalidades implementadas aos testes correspondentes.

## Roadmap

- [x] Definição inicial do problema e público-alvo.
- [x] Especificação inicial de requisitos e regras de negócio.
- [x] Identificação do dicionário de dados da CVM.
- [ ] Análise reproduzível de um arquivo real.
- [ ] Modelagem do domínio e do banco de dados.
- [ ] Implementação do pipeline de ingestão e validação.
- [ ] Persistência e reprocessamento idempotente.
- [ ] Implementação da API REST.
- [ ] Testes automatizados e integração contínua.
- [ ] Containerização com Docker Compose.
- [ ] Documentação de instalação e demonstração da V1.

## Limitações

A V1 não incluirá autenticação, integração com contas de corretoras, execução de ordens financeiras, recomendações de investimento ou previsões de rentabilidade.

O FundWatch não constitui uma plataforma de negociação ou aconselhamento financeiro.

A conclusão técnica do projeto não será apresentada como evidência de homologação regulatória, validação em produção ou utilização por instituições financeiras.

## Licença

A licença do código-fonte será definida antes da publicação pública do repositório.

Os dados utilizados pertencem às respectivas fontes e estão sujeitos às condições de utilização estabelecidas pelos seus responsáveis.

---

**FundWatch — Transformando dados públicos financeiros em informações estruturadas, rastreáveis e consultáveis.**
