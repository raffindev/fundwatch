# FundWatch — Modelo Relacional de Dados

**Versão:** 0.1  
**Status:** Implementado; validação com dados reais em andamento  
**SGBD:** PostgreSQL 18  
**Schema da aplicação:** `fundwatch`  
**Schema de integração:** `fundwatch_test`

## 1. Objetivo

Documentar a estrutura relacional utilizada pelo FundWatch para armazenar informes diários de fundos de investimento publicados pela CVM.

O modelo foi desenvolvido para atender aos seguintes requisitos:

- Preservar a identidade dos fundos e das subclasses.
- Armazenar indicadores financeiros com precisão decimal.
- Impedir duplicidades dentro de uma importação.
- Manter apenas uma versão vigente por identidade de informe.
- Preservar versões históricas quando os dados forem alterados.
- Registrar tentativas, execuções e falhas de importação.
- Garantir integridade referencial e transacional.

Este documento descreve a estrutura da v0.1. O arquivo `sql/schema.sql` permanece como referência para a definição física do banco de dados.

## 2. Evidências da análise dos dados

Arquivo de referência: `inf_diario_fi_202610.csv`.

| Indicador                    | Resultado |
| ---------------------------- | --------: |
| Registros analisados         |   537.880 |
| CNPJs distintos              |    25.507 |
| Chaves de negócio duplicadas |         0 |
| Registros sem subclasse      |   516.310 |

A análise identificou a seguinte chave de negócio:

`(CNPJ_FUNDO_CLASSE, ID_SUBCLASSE, DT_COMPTC)`

O campo `ID_SUBCLASSE` pode estar vazio e deve ser tratado como opcional.

As classificações informadas pela CVM também podem conter descrições textuais maiores que um caractere.

Essas observações fundamentaram as decisões de modelagem, mas não garantem que arquivos de outros períodos apresentem as mesmas características.

## 3. Estrutura geral

O FundWatch utiliza cinco tabelas principais:

| Tabela            | Responsabilidade                          |
| ----------------- | ----------------------------------------- |
| `funds`           | Identificação de fundos ou classes        |
| `daily_reports`   | Informes financeiros e versões históricas |
| `revisions`       | Rastreabilidade das revisões              |
| `import_runs`     | Controle das execuções de importação      |
| `import_attempts` | Auditoria das tentativas de importação    |

A implementação não utiliza as tabelas `daily_report_versions`, `import_executions` ou `import_rejections` previstas na modelagem inicial.

## 4. Tabela `funds`

### Responsabilidade

Representar a identidade de um fundo ou classe conforme o CNPJ fornecido pela CVM.

### Estrutura

| Coluna       | Tipo PostgreSQL | Restrições             |
| ------------ | --------------- | ---------------------- |
| `id`         | `BIGINT`        | PK, identidade gerada  |
| `cnpj`       | `VARCHAR(18)`   | NOT NULL, UNIQUE       |
| `class_type` | `VARCHAR(30)`   | NOT NULL               |
| `created_at` | `TIMESTAMPTZ`   | NOT NULL, valor padrão |

### Regras

- Cada CNPJ deve identificar um único registro em `funds`.
- O CNPJ é armazenado como texto.
- A classificação deve preservar as descrições recebidas da CVM.
- Um fundo pode possuir múltiplos informes diários.

**Decisão de modelagem:** `class_type` utiliza `VARCHAR(30)` após a identificação de classificações incompatíveis com o tipo inicial `CHAR(1)`.

## 5. Tabela `import_runs`

### Responsabilidade

Registrar a execução de uma importação, incluindo o arquivo de origem, o estado do processamento e informações operacionais.

### Estrutura

| Coluna             | Tipo PostgreSQL | Restrições                     |
| ------------------ | --------------- | ------------------------------ |
| `id`               | `BIGINT`        | PK, identidade gerada          |
| `filename`         | `VARCHAR(255)`  | NOT NULL                       |
| `file_hash`        | `CHAR(64)`      | Opcional no esquema            |
| `started_at`       | `TIMESTAMPTZ`   | NOT NULL, valor padrão         |
| `finished_at`      | `TIMESTAMPTZ`   | Opcional                       |
| `status`           | `VARCHAR(20)`   | NOT NULL, CHECK                |
| `error_message`    | `TEXT`          | Opcional                       |
| `total_records`    | `INTEGER`       | Não negativo, quando informado |
| `duplicates`       | `INTEGER`       | Não negativo, quando informado |
| `missing_subclass` | `INTEGER`       | Não negativo, quando informado |

### Estados permitidos

- `PROCESSING`: execução iniciada.
- `SUCCESS`: execução concluída com sucesso.
- `FAILED`: execução encerrada com falha.
- `REJECTED`: estado de rejeição previsto no esquema.

A aplicação utiliza principalmente `PROCESSING`, `SUCCESS` e `FAILED` no fluxo de execução.

### Controle de arquivos repetidos

O sistema identifica o conteúdo do arquivo por meio de um hash SHA-256.

O índice parcial `uq_import_runs_active_file_hash` impede que dois registros com o mesmo hash permaneçam simultaneamente nos estados `PROCESSING` ou `SUCCESS`.

Essa restrição protege a consistência das importações.

### Falhas

Uma execução com falha pode permanecer registrada mesmo quando a transação de persistência financeira é revertida.

O histórico operacional não deve ser confundido com o conjunto de dados financeiros efetivamente confirmado.

## 6. Tabela `import_attempts`

### Responsabilidade

Registrar as tentativas de iniciar importações, inclusive aquelas recusadas antes do processamento.

### Estrutura

| Coluna          | Tipo PostgreSQL | Restrições             |
| --------------- | --------------- | ---------------------- |
| `id`            | `BIGINT`        | PK, identidade gerada  |
| `filename`      | `VARCHAR(255)`  | NOT NULL               |
| `file_hash`     | `CHAR(64)`      | NOT NULL               |
| `requested_by`  | `VARCHAR(100)`  | Opcional               |
| `target_table`  | `VARCHAR(100)`  | NOT NULL               |
| `attempted_at`  | `TIMESTAMPTZ`   | NOT NULL, valor padrão |
| `outcome`       | `VARCHAR(30)`   | NOT NULL, CHECK        |
| `import_run_id` | `BIGINT`        | FK opcional            |
| `reason`        | `TEXT`          | Opcional               |

### Resultados permitidos

- `ACCEPTED`: tentativa aceita.
- `ALREADY_IMPORTED`: arquivo anteriormente importado.
- `REJECTED`: tentativa recusada.

### Integridade

Uma tentativa com resultado `ACCEPTED` deve possuir referência a uma execução em `import_runs`.

Tentativas recusadas não devem possuir associação com uma nova execução.

Essa separação permite auditar solicitações sem criar execuções desnecessárias.

## 7. Tabela `revisions`

### Responsabilidade

Registrar informações de rastreabilidade associadas a revisões de informes financeiros.

### Estrutura

| Coluna           | Tipo PostgreSQL | Restrições             |
| ---------------- | --------------- | ---------------------- |
| `id`             | `BIGINT`        | PK, identidade gerada  |
| `run_id`         | `BIGINT`        | NOT NULL, FK           |
| `reference_date` | `DATE`          | NOT NULL               |
| `note`           | `TEXT`          | Opcional               |
| `created_at`     | `TIMESTAMPTZ`   | NOT NULL, valor padrão |

### Relacionamento

Cada revisão pertence a uma execução de importação.

Uma execução pode originar múltiplas revisões.

A tabela registra a referência operacional da revisão. Os valores financeiros históricos são armazenados em `daily_reports`.

## 8. Tabela `daily_reports`

### Responsabilidade

Armazenar os indicadores financeiros publicados pela CVM, preservando versões históricas e identificando a versão vigente de cada informe.

### Estrutura

| Coluna           | Tipo PostgreSQL  | Restrições             |
| ---------------- | ---------------- | ---------------------- |
| `id`             | `BIGINT`         | PK, identidade gerada  |
| `fund_id`        | `BIGINT`         | NOT NULL, FK           |
| `subclass_id`    | `VARCHAR(15)`    | Opcional               |
| `reference_date` | `DATE`           | NOT NULL               |
| `total_value`    | `NUMERIC(17,2)`  | Opcional               |
| `quota_value`    | `NUMERIC(27,12)` | Opcional               |
| `net_equity`     | `NUMERIC(17,2)`  | Opcional               |
| `inflow`         | `NUMERIC(17,2)`  | Opcional               |
| `outflow`        | `NUMERIC(17,2)`  | Opcional               |
| `shareholders`   | `INTEGER`        | Opcional               |
| `revision_id`    | `BIGINT`         | FK opcional            |
| `created_at`     | `TIMESTAMPTZ`    | NOT NULL, valor padrão |
| `import_run_id`  | `BIGINT`         | NOT NULL, FK           |
| `is_current`     | `BOOLEAN`        | NOT NULL, padrão TRUE  |

### 8.1. Identidade de negócio

A identidade de um informe é determinada por:

`(fund_id, reference_date, subclass_id)`

O campo `subclass_id` pode ser `NULL`.

O modelo utiliza `NULLS NOT DISTINCT` para considerar subclasses ausentes equivalentes nas restrições de unicidade.

### 8.2. Unicidade dentro da importação

O índice `uq_daily_reports_import_record` utiliza:

`(import_run_id, fund_id, reference_date, subclass_id)`

Sua finalidade é impedir que uma execução armazene mais de uma ocorrência da mesma identidade de negócio.

### 8.3. Unicidade da versão vigente

O índice parcial `uq_daily_reports_current` utiliza:

`(fund_id, reference_date, subclass_id)`

com a condição:

`is_current = TRUE`

Essa restrição garante que exista no máximo uma versão vigente para cada identidade de informe.

### 8.4. Versionamento

O histórico é mantido na própria tabela `daily_reports`.

Quando um informe existente apresenta valores diferentes, o fluxo de revisão deve:

1. Identificar o informe vigente.
2. Comparar os indicadores financeiros.
3. Registrar a revisão associada à execução.
4. Marcar a versão anterior como não vigente.
5. Persistir a nova versão vigente.

A operação deve preservar a integridade transacional.

Quando os valores não apresentam alterações, não deve ser criada uma revisão desnecessária.

### 8.5. Precisão financeira

Os indicadores financeiros utilizam tipos `NUMERIC` para preservar precisão decimal.

A aplicação utiliza `Decimal` na interpretação dos valores.

O valor da cota possui escala de 12 casas decimais, enquanto os demais indicadores financeiros definidos no esquema utilizam escala de 2 casas decimais.

## 9. Integridade referencial

O esquema estabelece as seguintes referências:

| Origem            | Destino       | Chave           |
| ----------------- | ------------- | --------------- |
| `daily_reports`   | `funds`       | `fund_id`       |
| `daily_reports`   | `import_runs` | `import_run_id` |
| `daily_reports`   | `revisions`   | `revision_id`   |
| `revisions`       | `import_runs` | `run_id`        |
| `import_attempts` | `import_runs` | `import_run_id` |

Essas relações permitem identificar a origem dos informes, suas revisões e as execuções responsáveis.

## 10. Transações e consistência

O fluxo de importação separa a auditoria inicial da persistência financeira.

### Auditoria inicial

A execução é registrada com estado `PROCESSING`.

### Persistência

Os registros financeiros são processados em uma transação.

Quando ocorre uma falha antes do commit, as alterações não confirmadas são revertidas.

### Finalização

Uma execução concluída deve registrar `SUCCESS`.

Falhas controladas devem registrar `FAILED` e preservar informações úteis para diagnóstico.

### Limitação identificada

Uma interrupção abrupta do processo pode deixar uma execução com status `PROCESSING` mesmo depois do rollback da transação financeira.

A recuperação automática desse estado permanece pendente.

## 11. Ambientes de banco de dados

O projeto utiliza schemas separados para aplicação e testes de integração.

| Ambiente             | Schema           |
| -------------------- | ---------------- |
| Aplicação            | `fundwatch`      |
| Testes de integração | `fundwatch_test` |

A conexão utiliza o `search_path` correspondente ao schema selecionado.

Essa separação reduz o risco de testes modificarem os dados da aplicação.

A configuração local atual utiliza o banco `sql_lab`. O nome do banco é uma configuração de ambiente, não uma exigência permanente do domínio.

## 12. Decisões implementadas e pendências

| Código | Decisão                                         | Situação               |
| ------ | ----------------------------------------------- | ---------------------- |
| DM-01  | Separação de fundos e informes                  | Implementada           |
| DM-02  | Chave de negócio com subclasse opcional         | Implementada           |
| DM-03  | Unicidade com `NULLS NOT DISTINCT`              | Implementada no SQL    |
| DM-04  | Histórico na própria tabela `daily_reports`     | Implementado no modelo |
| DM-05  | Uma única versão vigente por informe            | Implementada no SQL    |
| DM-06  | Auditoria separada de tentativas e execuções    | Implementada           |
| DM-07  | Identificação de arquivos por SHA-256           | Implementada           |
| DM-08  | Atomicidade da persistência financeira          | Implementada           |
| DM-09  | Recuperação automática de execuções abandonadas | Pendente               |
| DM-10  | Avaliação de desempenho com arquivo completo    | Em andamento           |
| DM-11  | Validação de instalação e execução reproduzível | Em andamento           |

## 13. Limitações e próximos passos

Antes da conclusão da v0.1, o projeto deverá:

1. Confirmar a importação completa de um arquivo real.
2. Verificar a quantidade de registros persistidos.
3. Validar os resultados da auditoria.
4. Confirmar a recusa de reimportação do mesmo arquivo.
5. Testar o comportamento de revisões com dados modificados.
6. Implementar recuperação segura de importações interrompidas.
7. Medir o desempenho e avaliar otimizações.

A documentação deverá ser atualizada sempre que houver alterações relevantes na estrutura física do banco.

## 14. Referências

- [Análise do Domínio](analysis.md)
- [Requisitos do Sistema](../product/requirements.md)
- [CVM — Informes Diários de Fundos de Investimento](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)
- `sql/schema.sql` — definição física das tabelas e restrições.

---

**Nota:** a estrutura documentada corresponde ao esquema da v0.1, considerando a correção local de `class_type` para `VARCHAR(30)`. A importação integral do arquivo real permanece em validação.
