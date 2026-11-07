# FundWatch — Modelo Relacional de Dados

**Status:** Em desenvolvimento
**Versão:** 0.1
**Banco de dados:** PostgreSQL

## 1. Objetivo

Definir o modelo relacional responsável pelo armazenamento dos dados financeiros e operacionais do FundWatch, com foco em:

- Integridade dos dados.
- Precisão financeira.
- Idempotência das importações.
- Preservação do histórico de alterações.
- Rastreabilidade da origem dos registros.
- Consultas por fundo ou classe e data de competência.

O modelo deverá permitir importar dados públicos da CVM, identificar registros existentes, detectar alterações e preservar versões anteriores sem sobrescrever informações financeiras históricas.

Esta documentação representa a proposta inicial do modelo. Restrições e decisões ainda pendentes serão validadas antes ou durante a implementação.

## 2. Evidências da análise exploratória

**Arquivo analisado:** `inf_diario_fi_202610.csv`

| Métrica                                  | Resultado |
| ---------------------------------------- | --------: |
| Registros processados                    |   537.880 |
| CNPJs distintos                          |    25.507 |
| Chaves de negócio duplicadas             |         0 |
| Registros sem identificador de subclasse |   516.310 |

A análise identificou como chave de negócio candidata:

`(CNPJ_FUNDO_CLASSE, ID_SUBCLASSE, DT_COMPTC)`

Os resultados correspondem exclusivamente ao arquivo analisado e não estabelecem garantias sobre outros períodos ou arquivos corrigidos.

A ausência de subclasse foi observada como campo vazio no CSV. Sua representação no banco deverá ser normalizada de forma consistente.

## 3. Visão geral do modelo

### 3.1. Tabelas previstas

| Tabela                  | Responsabilidade                           |
| ----------------------- | ------------------------------------------ |
| `funds`                 | Identidade do fundo ou classe              |
| `daily_reports`         | Identidade do informe diário               |
| `daily_report_versions` | Valores financeiros e histórico de versões |
| `import_executions`     | Histórico das execuções de importação      |
| `import_rejections`     | Registros rejeitados e motivos de rejeição |

### 3.2. Relacionamentos

- `funds` 1:N `daily_reports`
- `daily_reports` 1:N `daily_report_versions`
- `import_executions` 1:N `daily_report_versions`
- `import_executions` 1:N `import_rejections`

### 3.3. Princípio de separação de responsabilidades

O modelo distingue três conceitos:

**Identidade:** determina qual fundo ou informe está sendo representado.

**Conteúdo financeiro:** representa os valores publicados pela CVM para determinado informe.

**Proveniência:** identifica a execução de importação que originou cada versão armazenada.

Essa separação evita duplicação desnecessária dos valores financeiros entre tabelas e facilita a preservação do histórico.

## 4. Tabela `funds`

**Responsabilidade:** representar a identidade de um fundo ou classe identificado pelo CNPJ informado pela CVM.

| Coluna | Tipo PostgreSQL | Restrições                     |
| ------ | --------------- | ------------------------------ |
| `id`   | `BIGINT`        | PRIMARY KEY, identidade gerada |
| `cnpj` | `VARCHAR(18)`   | NOT NULL, UNIQUE               |

### Regras

- Cada CNPJ normalizado deverá corresponder a um único registro.
- O CNPJ deverá ser tratado como identificador textual, não numérico.
- O identificador interno `id` será utilizado nas relações com outras tabelas.
- A normalização do CNPJ deverá ser consistente durante todas as importações.
- O CNPJ informado pela CVM identifica o fundo ou classe conforme o conjunto de dados de origem; não será presumida uma equivalência automática com outras entidades jurídicas.

O campo `fund_type` não será armazenado nesta tabela inicialmente, pois sua estabilidade ao longo do tempo ainda não foi demonstrada.

## 5. Tabela `daily_reports`

**Responsabilidade:** representar a identidade permanente de um informe diário para determinado fundo ou classe, data de competência e eventual subclasse.

| Coluna           | Tipo PostgreSQL | Restrições iniciais            |
| ---------------- | --------------- | ------------------------------ |
| `id`             | `BIGINT`        | PRIMARY KEY, identidade gerada |
| `fund_id`        | `BIGINT`        | NOT NULL, FOREIGN KEY          |
| `subclass_id`    | `VARCHAR(15)`   | NULL permitido                 |
| `reference_date` | `DATE`          | NOT NULL                       |

### Relacionamento

Cada informe deverá pertencer a um registro existente em `funds`.

A relação entre `funds` e `daily_reports` será de um para muitos (`1:N`).

### Identidade de negócio

A identidade candidata de um informe será:

`(fund_id, subclass_id, reference_date)`

Cada combinação deverá identificar um único informe, independentemente da quantidade de versões financeiras existentes.

A restrição de unicidade deverá tratar valores ausentes de `subclass_id` como equivalentes para fins de identificação.

### Regras

- Um informe deverá estar associado a um fundo ou classe existente.
- A data de competência será obrigatória.
- A ausência de subclasse deverá ser normalizada de maneira consistente.
- Um mesmo informe não poderá possuir identidades duplicadas.
- Os indicadores financeiros não serão armazenados diretamente nesta tabela.
- Os valores financeiros serão preservados em `daily_report_versions`.

## 6. Tabela `import_executions`

**Responsabilidade:** registrar cada tentativa de importação de dados da CVM, incluindo identificação do arquivo, execução, resultados e eventuais falhas.

| Coluna              | Tipo PostgreSQL | Restrições iniciais            |
| ------------------- | --------------- | ------------------------------ |
| `id`                | `BIGINT`        | PRIMARY KEY, identidade gerada |
| `source_filename`   | `VARCHAR(255)`  | NOT NULL                       |
| `source_checksum`   | `CHAR(64)`      | NOT NULL                       |
| `status`            | `VARCHAR(20)`   | NOT NULL                       |
| `started_at`        | `TIMESTAMPTZ`   | NOT NULL                       |
| `finished_at`       | `TIMESTAMPTZ`   | NULL permitido                 |
| `total_records`     | `INTEGER`       | NOT NULL, DEFAULT 0            |
| `inserted_records`  | `INTEGER`       | NOT NULL, DEFAULT 0            |
| `unchanged_records` | `INTEGER`       | NOT NULL, DEFAULT 0            |
| `revised_records`   | `INTEGER`       | NOT NULL, DEFAULT 0            |
| `rejected_records`  | `INTEGER`       | NOT NULL, DEFAULT 0            |
| `error_message`     | `TEXT`          | NULL permitido                 |

### Identificação da origem

O campo `source_filename` armazenará o nome do arquivo processado.

O campo `source_checksum` armazenará o hash SHA-256 dos bytes do arquivo efetivamente processado.

O checksum não será uma restrição de unicidade, pois múltiplas tentativas de processamento do mesmo arquivo deverão ser registradas.

### Estados da execução

- `PENDING`: execução registrada, ainda não iniciada.
- `RUNNING`: processamento em andamento.
- `COMPLETED`: processamento concluído.
- `FAILED`: execução encerrada por falha.

Uma execução poderá ser concluída mesmo contendo registros rejeitados, desde que o processamento tenha terminado conforme as regras estabelecidas.

### Contadores operacionais

- `total_records`: quantidade de registros de dados lidos, excluindo o cabeçalho.
- `inserted_records`: registros financeiros novos.
- `unchanged_records`: registros financeiros existentes e sem alterações.
- `revised_records`: registros financeiros com novas versões.
- `rejected_records`: registros rejeitados durante a validação.

Em uma execução normalmente concluída, cada linha lida deverá pertencer a exatamente uma dessas quatro categorias de resultado.

Consequentemente:

`total_records = inserted_records + unchanged_records + revised_records + rejected_records`

Execuções interrompidas poderão apresentar contadores parciais.

### Regras

- Cada tentativa de importação deverá possuir seu próprio identificador.
- Importações repetidas deverão ser registradas, mesmo sem alterações financeiras.
- Os contadores não poderão assumir valores negativos.
- `finished_at`, quando informado, não poderá ser anterior a `started_at`.
- Uma execução em andamento poderá não possuir `finished_at`.
- Execuções concluídas ou encerradas por falha deverão possuir `finished_at`.
- Falhas operacionais poderão ser registradas em `error_message`.
- O status deverá pertencer ao conjunto de estados permitidos.

## 7. Tabela `daily_report_versions`

**Responsabilidade:** armazenar versões imutáveis dos indicadores financeiros de cada informe diário, preservando o histórico de alterações identificadas durante as importações.

| Coluna                | Tipo PostgreSQL  | Restrições iniciais            |
| --------------------- | ---------------- | ------------------------------ |
| `id`                  | `BIGINT`         | PRIMARY KEY, identidade gerada |
| `daily_report_id`     | `BIGINT`         | NOT NULL, FOREIGN KEY          |
| `import_execution_id` | `BIGINT`         | NOT NULL, FOREIGN KEY          |
| `version_number`      | `INTEGER`        | NOT NULL                       |
| `fund_type`           | `VARCHAR(20)`    | Obrigatoriedade a validar      |
| `total_value`         | `NUMERIC(17,2)`  | Obrigatoriedade a validar      |
| `quota_value`         | `NUMERIC(27,12)` | Obrigatoriedade a validar      |
| `net_asset_value`     | `NUMERIC(17,2)`  | Obrigatoriedade a validar      |
| `subscriptions`       | `NUMERIC(17,2)`  | Obrigatoriedade a validar      |
| `redemptions`         | `NUMERIC(17,2)`  | Obrigatoriedade a validar      |
| `shareholder_count`   | `INTEGER`        | Obrigatoriedade a validar      |
| `created_at`          | `TIMESTAMPTZ`    | NOT NULL                       |

### Relacionamentos

- Cada versão deverá pertencer a um informe existente em `daily_reports`.
- Cada versão deverá estar associada à execução que a originou.
- Um informe poderá possuir múltiplas versões.
- Uma execução poderá originar múltiplas versões.

### Identificação das versões

A combinação `(daily_report_id, version_number)` deverá ser única.

A primeira versão de um informe receberá `version_number = 1`.

Cada alteração posterior dos dados versionados gerará um novo número sequencial.

### Regras de versionamento

- As versões financeiras deverão ser imutáveis após sua criação.
- Uma nova versão somente será criada quando os dados recebidos forem diferentes dos valores da versão corrente.
- Importações repetidas com dados idênticos aos valores correntes não deverão gerar novas versões.
- A versão corrente será aquela com o maior `version_number` para determinado informe.
- O histórico deverá permitir identificar os valores anteriores e a importação responsável por cada versão.
- A comparação deverá considerar todos os campos financeiros e descritivos versionados, após normalização.
- Uma correção que restaure valores de uma versão antiga também deverá gerar nova versão quando diferir da versão corrente.
- A criação de versões deverá ser protegida contra condições de concorrência durante a implementação.

### Precisão financeira

Os indicadores financeiros utilizarão tipos `NUMERIC` com precisão e escala compatíveis com o dicionário de dados da CVM.

Na aplicação Python, os valores deverão ser representados utilizando `Decimal`, evitando perdas de precisão decorrentes de operações com `float`.

### Auditoria

O campo `import_execution_id` permitirá identificar qual processamento originou a versão.

O campo `created_at` registrará quando a versão foi persistida no FundWatch, não a data de competência do informe.

A execução que apenas reencontra valores idênticos não será considerada origem de uma nova versão.

## 8. Tabela `import_rejections`

**Responsabilidade:** registrar os registros rejeitados durante uma importação, preservando a origem, a classificação do erro e os dados necessários para investigação.

| Coluna                | Tipo PostgreSQL | Restrições iniciais            |
| --------------------- | --------------- | ------------------------------ |
| `id`                  | `BIGINT`        | PRIMARY KEY, identidade gerada |
| `import_execution_id` | `BIGINT`        | NOT NULL, FOREIGN KEY          |
| `source_row_number`   | `INTEGER`       | NOT NULL                       |
| `error_code`          | `VARCHAR(50)`   | NOT NULL                       |
| `error_message`       | `TEXT`          | NOT NULL                       |
| `raw_data`            | `JSONB`         | NOT NULL                       |
| `created_at`          | `TIMESTAMPTZ`   | NOT NULL                       |

### Relacionamento

Cada rejeição deverá estar associada a uma execução existente em `import_executions`.

A relação entre `import_executions` e `import_rejections` será de um para muitos (`1:N`).

### Identificação da origem

O campo `source_row_number` deverá identificar a linha física do arquivo de origem, considerando o cabeçalho como linha 1.

O campo `raw_data` deverá preservar os dados textuais originais disponíveis para investigação, sem substituir os valores inválidos por versões corrigidas.

### Classificação dos erros

Os códigos inicialmente previstos incluem:

- `MISSING_REQUIRED_FIELD`: campo obrigatório ausente.
- `INVALID_DATE`: data inválida.
- `INVALID_NUMERIC_VALUE`: valor numérico inválido.
- `INVALID_IDENTIFIER`: identificador inválido.
- `INVALID_RECORD_STRUCTURE`: estrutura incompatível com o formato esperado.

A lista poderá ser ampliada conforme os problemas encontrados nos arquivos reais.

### Regras

- Cada rejeição deverá pertencer a uma execução existente.
- O número da linha deverá ser maior que zero.
- Cada linha rejeitada deverá contribuir uma única vez para `rejected_records`, mesmo quando apresentar múltiplos problemas.
- Uma linha poderá possuir mais de um motivo de rejeição; inicialmente será registrado um motivo principal, conforme a ordem de validação definida pela aplicação.
- Registros rejeitados não deverão gerar versões financeiras.
- Rejeições não deverão impedir automaticamente o processamento de outros registros válidos.
- Falhas que comprometam a estrutura global do arquivo poderão encerrar a execução como `FAILED`.
- A política de preservação de linhas malformadas que não possam ser representadas integralmente como JSON será definida na implementação.

## 9. Decisões pendentes

### DP-01 — Validação dos campos financeiros

Verificar, utilizando dados reais da CVM, quais indicadores admitem valores ausentes e quais restrições de domínio podem ser aplicadas sem rejeitar dados legítimos.

### DP-02 — Unicidade com subclasses ausentes

Definir a implementação da restrição de unicidade de `daily_reports` quando `subclass_id` for `NULL`, considerando a versão efetivamente utilizada do PostgreSQL.

### DP-03 — Integridade das versões

Definir os mecanismos transacionais e de concorrência necessários para garantir a numeração sequencial e evitar versões conflitantes.

### DP-04 — Política de rejeições

Definir a ordem das validações, os erros recuperáveis, os erros fatais e o tratamento de linhas CSV malformadas.

### DP-05 — Normalização e comparação

Definir as regras de normalização de CNPJ, subclasse, datas e valores numéricos antes da identificação de duplicações ou alterações.

### DP-06 — Proveniência de registros inalterados

Definir se os contadores de `import_executions` são suficientes para os requisitos de auditoria ou se será necessário registrar associações individuais entre execuções e registros reencontrados sem alterações.

### DP-07 — Política de processamento de arquivos

Definir o tratamento de arquivos repetidos, arquivos corrigidos, falhas parciais e retomada de execuções interrompidas.

### DP-08 — Índices e consultas

Definir índices para consultas por CNPJ, data de competência, versão corrente e histórico de importações, com base nos padrões reais de acesso.

---

## 10. Referências

- [Análise do domínio](analysis.md)
- [Requisitos do produto](../product/requirements.md)
- [Fonte oficial — Informes Diários de Fundos de Investimento (CVM)](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)

**Observação:** este documento define o modelo lógico-relacional inicial. A implementação física, as migrações SQL e as validações automatizadas serão desenvolvidas nas etapas seguintes.
