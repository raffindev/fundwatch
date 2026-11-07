# FundWatch — Análise do Domínio

**Status:** Modelagem inicial
**Versão:** 0.1
**Fonte principal:** Informes Diários de Fundos de Investimento — CVM

## 1. Objetivo

Definir os conceitos, as entidades, os relacionamentos e as regras de integridade necessários para processar, armazenar e consultar informações históricas de fundos de investimento disponibilizadas pela CVM.

A modelagem prioriza integridade dos dados, idempotência, rastreabilidade e capacidade de auditoria.

## 2. Contexto do domínio

O FundWatch processará informes diários publicados pela Comissão de Valores Mobiliários (CVM).

Cada registro apresenta a identificação de um fundo ou classe, uma data de competência e indicadores financeiros.

O sistema deverá distinguir:

- A identidade do fundo ou classe.
- A identificação de uma eventual subclasse.
- Os indicadores financeiros associados a uma data.
- A execução responsável pela importação.
- As alterações identificadas em registros anteriormente importados.

## 3. Entidades candidatas

### 3.1. Fund

Representa a identidade de um fundo ou classe identificada pelo CNPJ disponibilizado pela CVM.

Responsabilidades:

- Manter a identificação do fundo ou classe.
- Permitir a associação com seus informes diários.
- Evitar duplicação desnecessária de dados de identificação.

Atributos candidatos:

- `id`: identificador interno.
- `cnpj`: CNPJ informado pela CVM.
- `fund_type`: tipo de fundo ou classe, sujeito à validação de sua estabilidade nos dados.

### 3.2. DailyReport

Representa os indicadores financeiros de um fundo ou classe em determinada data de competência, considerando a eventual subclasse.

Atributos candidatos:

- `id`: identificador interno.
- `fund_id`: referência ao fundo ou classe.
- `subclass_id`: identificador de subclasse, quando informado.
- `reference_date`: data de competência.
- `quota_value`: valor da cota.
- `net_asset_value`: patrimônio líquido.
- `total_value`: valor total.
- `subscriptions`: captações diárias.
- `redemptions`: resgates diários.
- `shareholder_count`: número de cotistas.

### 3.3. ImportExecution

Representa uma execução de importação de dados.

Responsabilidades:

- Identificar o arquivo ou fonte processada.
- Registrar início, término e resultado da execução.
- Contabilizar registros processados, inseridos, repetidos, alterados e rejeitados.
- Permitir investigação de falhas e rastreabilidade operacional.

### 3.4. DailyReportRevision

Representa uma versão histórica de um informe diário que sofreu alteração.

Responsabilidades:

- Preservar os dados anteriores.
- Registrar os novos valores recebidos.
- Associar a alteração à execução de importação.
- Permitir reconstruir o histórico das modificações.

A estrutura exata de versionamento será definida na modelagem lógica.

### 3.5. ImportRejection

Representa um registro que não pôde ser aceito durante a importação.

Responsabilidades:

- Identificar a execução de origem.
- Preservar informações suficientes para investigação.
- Registrar o motivo da rejeição.
- Permitir contabilização e diagnóstico de problemas de qualidade dos dados.

## 4. Relacionamentos iniciais

| Origem          | Relação | Destino             |
| --------------- | ------- | ------------------- |
| Fund            | 1:N     | DailyReport         |
| DailyReport     | 1:N     | DailyReportRevision |
| ImportExecution | 1:N     | DailyReportRevision |
| ImportExecution | 1:N     | ImportRejection     |

A associação entre registros importados e suas execuções também deverá ser preservada, inclusive para registros sem alterações.

## 5. Identidade e unicidade

A identidade de negócio candidata de um informe diário é composta por:

- `CNPJ_FUNDO_CLASSE`
- `ID_SUBCLASSE`
- `DT_COMPTC`

A hipótese deverá ser verificada nos arquivos reais da CVM.

Como `ID_SUBCLASSE` pode estar ausente, a estratégia de unicidade deverá tratar explicitamente valores nulos.

A existência de uma chave primária interna não substitui a necessidade de uma restrição de unicidade de negócio.

## 6. Regras de integridade

**RD-01 — Identidade do fundo:** um CNPJ normalizado não deverá produzir múltiplas entidades Fund equivalentes.

**RD-02 — Identidade do informe:** dois informes ativos não poderão representar a mesma identidade de negócio.

**RD-03 — Idempotência:** a reimportação de um registro idêntico não deverá produzir duplicação ou revisão desnecessária.

**RD-04 — Correções:** alterações nos indicadores de um informe existente deverão preservar o histórico anterior.

**RD-05 — Rastreabilidade:** alterações e rejeições deverão ser associadas à execução que as identificou.

**RD-06 — Precisão financeira:** indicadores monetários e valores de cota deverão utilizar representação decimal adequada, evitando perdas de precisão decorrentes de ponto flutuante binário.

**RD-07 — Rejeições:** registros inválidos não deverão comprometer a integridade dos registros válidos, conforme a política transacional definida para a importação.

## 7. Decisões de modelagem

| Código | Decisão                                                 | Situação           |
| ------ | ------------------------------------------------------- | ------------------ |
| DM-01  | Separar Fund de DailyReport                             | Aprovada           |
| DM-02  | Considerar subclasse na identidade candidata do informe | Hipótese a validar |
| DM-03  | Impedir duplicação em reimportações                     | Aprovada           |
| DM-04  | Preservar histórico de alterações                       | Aprovada           |
| DM-05  | Registrar execuções de importação                       | Aprovada           |
| DM-06  | Registrar rejeições e suas causas                       | Aprovada           |
| DM-07  | Definir estrutura de versionamento e restrições SQL     | Pendente           |
| DM-08  | Validar cardinalidade e semântica dos dados reais       | Pendente           |

## 8. Próximos passos

1. Examinar a estrutura e os dados reais dos arquivos da CVM.
2. Validar a identidade candidata e a ocorrência de valores nulos.
3. Refinar os relacionamentos e atributos.
4. Definir a modelagem lógica para PostgreSQL.
5. Implementar e testar as restrições de integridade.

## 9. Referência

CVM — Informe Diário de Fundos de Investimento:

https://dados.cvm.gov.br/dataset/fi-doc-inf_diario

---

**Observação:** este documento representa a modelagem inicial do FundWatch. As entidades e os relacionamentos poderão ser refinados conforme evidências obtidas na análise dos dados reais.
