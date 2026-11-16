# FundWatch

**Pipeline backend para ingestão, validação, versionamento e armazenamento de informes diários de fundos de investimento da CVM.**

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-94%20testes%20aprovados-0A9EDC?logo=pytest&logoColor=white)
![Status](https://img.shields.io/badge/Status-v0.1%20em%20valida%C3%A7%C3%A3o-orange)

> **Status:** v0.1 — pipeline de importação funcional e validado com arquivo real da CVM. API REST ainda não implementada.
>
> **Idioma:** Português brasileiro. Documentação em inglês planejada.

---

## Sobre o projeto

O **FundWatch** é um projeto Python Backend desenvolvido para transformar arquivos públicos da Comissão de Valores Mobiliários (CVM) em dados financeiros estruturados, persistentes e rastreáveis.

A aplicação realiza a leitura de arquivos CSV, valida os registros, identifica fundos, controla importações, armazena informes diários no PostgreSQL e preserva o histórico de alterações financeiras.

O objetivo é construir uma solução reproduzível para processamento de dados financeiros, aplicando princípios de integridade, rastreabilidade, testes automatizados e separação de responsabilidades.

## O problema

O processamento recorrente de arquivos públicos de fundos de investimento apresenta desafios como:

- Grandes volumes de dados.
- Validação de tipos e formatos.
- Risco de duplicação durante reimportações.
- Correções e reapresentações de informações.
- Necessidade de histórico e auditoria.
- Recuperação consistente após falhas.

O FundWatch centraliza essas responsabilidades em um pipeline backend.

Consulte a [Definição do Problema](docs/product/problem-statement.md).

## Funcionalidades implementadas

| Funcionalidade           | Descrição                                                    |
| ------------------------ | ------------------------------------------------------------ |
| Leitura CSV              | Processamento dos informes diários da CVM                    |
| Validação                | Verificação de datas, valores decimais, inteiros e registros |
| Persistência             | Armazenamento relacional no PostgreSQL                       |
| Identificação de fundos  | Cadastro e reutilização de fundos por CNPJ                   |
| Controle de duplicidades | Detecção de chaves repetidas no arquivo                      |
| Idempotência de arquivo  | Controle de reimportação por hash SHA-256                    |
| Versionamento            | Preservação de alterações financeiras por revisões           |
| Auditoria                | Registro de execuções e tentativas de importação             |
| Transações               | Commit em caso de sucesso e rollback em caso de falha        |
| Progresso                | Acompanhamento a cada 10.000 registros                       |
| Testes                   | Testes automatizados com pytest                              |

O pipeline é executado por linha de comando. A API REST permanece no planejamento.

## Fonte de dados

O FundWatch utiliza o conjunto público **Informe Diário de Fundos de Investimento**, disponibilizado pela CVM.

**Fonte oficial:** https://dados.cvm.gov.br/dataset/fi-doc-inf_diario

Entre os campos processados estão:

- CNPJ do fundo/classe.
- Identificação da subclasse, quando disponível.
- Data de competência.
- Valor total da carteira.
- Valor da cota.
- Patrimônio líquido.
- Captações e resgates.
- Número de cotistas.

O projeto é independente e não possui vínculo institucional ou endosso da CVM.

## Tecnologias utilizadas

| Tecnologia    | Finalidade                            |
| ------------- | ------------------------------------- |
| Python 3.14   | Implementação do backend              |
| PostgreSQL 18 | Persistência e integridade relacional |
| Psycopg 3     | Comunicação entre Python e PostgreSQL |
| pytest        | Testes automatizados                  |
| Git e GitHub  | Versionamento e documentação          |

**Planejadas:** FastAPI, Docker Compose e integração contínua.

## Arquitetura

O pipeline segue o fluxo:

```text
Arquivo CSV da CVM
        |
        v
Leitura e validação
        |
        v
Verificação de duplicidades
        |
        v
Identificação dos fundos
        |
        v
Comparação com informes existentes
        |
        +---- Novo registro ------> Inserção
        |
        +---- Sem alteração ------> Preservação
        |
        +---- Alterado -----------> Revisão histórica
        |
        v
PostgreSQL
        |
        v
Commit ou rollback
        |
        v
Auditoria da importação
```

O processamento utiliza transações e bloqueio consultivo do PostgreSQL para coordenar execuções concorrentes.

## Execução do projeto

### Pré-requisitos

- Python 3.14.
- PostgreSQL 18.
- Dependências Python do projeto instaladas.
- Banco de dados e schema configurados.
- Arquivo CSV da CVM disponível localmente.

### Executar os testes

Com o ambiente virtual ativado:

```powershell
python -m pytest -q
```

Resultado registrado na validação de 16/11/2026:

```text
94 passed in 4.55s
```

### Importar um arquivo da CVM

Exemplo de execução no ambiente de integração:

```powershell
python scripts/import_cvm.py data/raw/inf_diario_fi_202610.csv --schema fundwatch_test
```

O schema `fundwatch_test` é utilizado para integração. O schema principal do projeto é `fundwatch`.

O banco e o schema devem estar previamente configurados. A execução do comando não substitui a preparação do ambiente PostgreSQL.

Durante a importação, o terminal apresenta mensagens de progresso a cada 10.000 registros, incluindo contadores e tempo decorrido.

Os contadores intermediários representam registros processados; a persistência somente é confirmada após o commit.

## Resultados da validação com dados reais

Em **16 de novembro de 2026**, o FundWatch processou integralmente o arquivo `inf_diario_fi_202610.csv`.

| Indicador               |         Resultado |
| ----------------------- | ----------------: |
| Registros processados   |           537.880 |
| Registros inseridos     |           537.880 |
| Fundos únicos           |            25.507 |
| Registros inalterados   |                 0 |
| Registros revisados     |                 0 |
| Duplicidades detectadas |                 0 |
| Registros sem subclasse |           516.310 |
| Tempo total             |    203,0 segundos |
| Vazão média aproximada  | 2.650 registros/s |

**Verificações realizadas no PostgreSQL:**

- 25.507 fundos persistidos.
- 537.880 informes diários persistidos.
- 537.880 informes marcados como atuais.
- Nenhuma revisão na primeira importação.
- Nenhuma duplicidade encontrada entre informes atuais pela combinação de fundo, subclasse e data.

Esses resultados correspondem a uma execução local, com o arquivo e ambiente descritos. Não representam garantia de desempenho em outros ambientes.

## Regras de integridade

O FundWatch adota as seguintes regras:

1. Uma importação já concluída com sucesso não deve ser repetida para o mesmo arquivo.
2. Registros duplicados dentro do CSV são rejeitados.
3. A ausência de subclasse é permitida.
4. Informes atuais são identificados pela combinação de fundo, subclasse e data de referência.
5. Informações financeiras alteradas devem gerar histórico de revisão.
6. Falhas durante o processamento devem provocar rollback da transação.
7. Tentativas e execuções devem ser registradas para auditoria.

## Documentação

| Documento                                                  | Conteúdo                             |
| ---------------------------------------------------------- | ------------------------------------ |
| [Definição do Problema](docs/product/problem-statement.md) | Problema, contexto e objetivos       |
| [Requisitos do Sistema](docs/product/requirements.md)      | Requisitos e regras de negócio       |
| [Análise do Domínio](docs/domain/analysis.md)              | Entidades e comportamento do domínio |
| [Modelo de Dados](docs/domain/data-model.md)               | Estrutura relacional e integridade   |

## Próximas etapas

- [x] Análise do problema e definição de requisitos.
- [x] Inspeção de arquivo real da CVM.
- [x] Modelagem inicial do domínio e banco de dados.
- [x] Leitura e validação dos registros.
- [x] Persistência transacional.
- [x] Controle de duplicidades e reimportações.
- [x] Implementação do versionamento de informes.
- [x] Auditoria de importações.
- [x] Indicador de progresso e medição de desempenho.
- [x] Primeira importação integral validada no PostgreSQL.
- [ ] Ampliar testes de reimportação, revisão histórica e recuperação após interrupção.
- [ ] Implementar API REST com FastAPI.
- [ ] Preparar execução reproduzível com Docker Compose.
- [ ] Configurar integração contínua.
- [ ] Publicar documentação de instalação completa.

## Limitações

A v0.1 concentra-se no pipeline de ingestão e persistência. Ainda não oferece API REST, interface gráfica ou implantação automatizada.

O FundWatch não executa operações financeiras, não fornece recomendações de investimento e não constitui uma plataforma de negociação.

A validação local não representa homologação regulatória ou utilização em ambiente de produção.

## Licença

A licença do código-fonte será definida antes da publicação pública do repositório.

Os dados da CVM estão sujeitos às condições de utilização estabelecidas pela fonte oficial.

---

**FundWatch — Dados financeiros públicos com integridade, histórico e rastreabilidade.**
