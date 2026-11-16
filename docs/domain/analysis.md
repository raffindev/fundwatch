# FundWatch — Análise do Domínio

**Versão:** 0.1  
**Status:** Domínio implementado parcialmente; validação operacional em andamento  
**Fonte de dados:** Comissão de Valores Mobiliários (CVM) — Informes Diários de Fundos de Investimento

## 1. Objetivo

Documentar os conceitos, as entidades, os relacionamentos e as regras de negócio do FundWatch, um sistema backend responsável pela ingestão, validação, persistência e rastreabilidade de informes diários de fundos de investimento publicados pela CVM.

O domínio prioriza:

- Integridade e precisão dos dados financeiros.
- Identificação consistente de fundos e informes.
- Prevenção de duplicidades.
- Histórico de revisões.
- Auditoria das tentativas e execuções de importação.
- Comportamento transacional previsível diante de falhas.

Este documento descreve o domínio da versão 0.1. Detalhes de colunas, tipos SQL e restrições físicas pertencem ao documento [Modelo de Dados](data-model.md).

## 2. Contexto do domínio

A CVM disponibiliza arquivos contendo informações financeiras de fundos de investimento e suas classes ou subclasses.

Cada linha do informe diário associa uma identificação de fundo ou classe a uma data de competência e a um conjunto de indicadores financeiros.

O FundWatch transforma esses registros em informações estruturadas, preservando a distinção entre:

- **Identidade:** qual fundo, classe ou subclasse está representado.
- **Competência:** a data à qual os indicadores se referem.
- **Conteúdo financeiro:** os valores publicados pela CVM.
- **Proveniência:** qual importação processou as informações.
- **Revisão:** quais alterações foram identificadas em dados previamente armazenados.

A data de competência não deve ser confundida com a data de importação.

## 3. Entidades do domínio

### 3.1. Fund

Representa um fundo ou classe identificado pelo CNPJ informado pela CVM.

Responsabilidades:

- Manter uma identidade única por CNPJ.
- Registrar a classificação informada pela fonte.
- Permitir a associação de múltiplos informes diários.

Atributos principais:

- `id`: identificador interno.
- `cnpj`: identificação fornecida pela CVM.
- `class_type`: classificação informada no arquivo.
- `created_at`: data de criação do registro no FundWatch.

O CNPJ é tratado como identificador textual.

A classificação não deve ser presumida como um código de um único caractere. O arquivo analisado contém descrições como `CLASSES - FIF`, `CLASSE FIF/FAPI` e `FI`.

### 3.2. DailyReport

Representa os indicadores de um fundo ou classe em determinada data de competência, considerando a eventual identificação de subclasse.

Atributos principais:

- `id`: identificador interno.
- `fund_id`: referência ao fundo.
- `subclass_id`: identificação opcional de subclasse.
- `reference_date`: data de competência.
- `total_value`: valor total.
- `quota_value`: valor da cota.
- `net_equity`: patrimônio líquido.
- `inflow`: captação diária.
- `outflow`: resgate diário.
- `shareholders`: quantidade de cotistas.
- `revision_id`: referência ao registro de revisão associado, quando aplicável.
- `created_at`: data de persistência.

Os indicadores financeiros devem preservar a precisão informada pela fonte, utilizando `Decimal` na aplicação e tipos `NUMERIC` no PostgreSQL.

### 3.3. ImportRun

Representa uma execução de importação aceita para processamento.

Responsabilidades:

- Identificar o arquivo processado.
- Registrar seu checksum SHA-256.
- Controlar o estado da execução.
- Registrar início e término.
- Consolidar os resultados do processamento.
- Preservar informações sobre falhas.

Estados utilizados no fluxo atual:

- `PROCESSING`: importação em andamento.
- `SUCCESS`: importação concluída.
- `FAILED`: importação encerrada com falha.

Uma execução com falha deve permanecer registrada para fins de auditoria, mesmo quando nenhuma alteração financeira é confirmada.

### 3.4. ImportAttempt

Representa uma tentativa de iniciar uma importação.

Sua responsabilidade é permitir a auditoria de solicitações aceitas ou recusadas, incluindo situações como:

- Arquivo já importado com sucesso.
- Existência de processamento concorrente incompatível.
- Solicitação aceita para execução.

A tentativa de importação e a execução de importação são conceitos distintos: nem toda tentativa resulta em uma nova execução.

### 3.5. Revision

Representa o mecanismo de rastreabilidade utilizado quando informações anteriormente importadas apresentam alterações.

Responsabilidades:

- Identificar alterações em informes existentes.
- Associar alterações à execução responsável.
- Preservar informações necessárias para investigar revisões.
- Evitar revisões desnecessárias quando os valores recebidos não mudaram.

A estrutura concreta de persistência e recuperação do histórico deve ser descrita no modelo relacional e verificada pelos testes de integração.

## 4. Relacionamentos

| Origem    | Destino       | Relação de domínio                                     |
| --------- | ------------- | ------------------------------------------------------ |
| Fund      | DailyReport   | Um fundo possui múltiplos informes                     |
| ImportRun | ImportAttempt | Tentativas e execuções possuem associação de auditoria |
| ImportRun | Revision      | Uma execução pode originar revisões                    |
| Revision  | DailyReport   | Revisões registram alterações relacionadas a informes  |

As cardinalidades físicas e as chaves estrangeiras devem ser conferidas no esquema SQL efetivamente utilizado.

## 5. Identidade e unicidade

A identidade de negócio de um informe é composta por:

`(CNPJ_FUNDO_CLASSE, ID_SUBCLASSE, DT_COMPTC)`

Na aplicação, após identificar o fundo, essa composição corresponde a:

`(fund_id, subclass_id, reference_date)`

### 5.1. Subclasse opcional

O campo `ID_SUBCLASSE` pode estar vazio no arquivo de origem.

A ausência de subclasse é válida e deve ser representada de maneira consistente.

Dois registros referentes ao mesmo fundo e à mesma data, ambos sem subclasse, representam a mesma identidade de negócio.

A ausência de subclasse não autoriza a criação de registros duplicados.

### 5.2. Duplicidade dentro do arquivo

Quando um arquivo contém duas linhas com a mesma identidade de negócio, o importador deve identificar a duplicidade e interromper a execução conforme a política de validação da v0.1.

### 5.3. Reimportação

O sistema utiliza o checksum SHA-256 do arquivo para identificar conteúdo já processado.

A reimportação de um arquivo anteriormente concluído com sucesso deve ser recusada, sem duplicar dados.

Arquivos diferentes podem conter informes já conhecidos. Nesses casos, o sistema deve distinguir valores inalterados de valores revisados.

## 6. Regras de negócio

**RD-01 — Identidade do fundo**

Cada CNPJ normalizado deve corresponder a uma única entidade `Fund`.

**RD-02 — Identidade do informe**

Um informe é identificado pela combinação de fundo, subclasse opcional e data de competência.

**RD-03 — Validação de registros**

Campos obrigatórios, datas, números decimais e inteiros devem ser validados antes da persistência.

Valores incompatíveis devem produzir erros identificáveis.

**RD-04 — Precisão financeira**

Valores financeiros não devem depender de representação binária de ponto flutuante para preservar a precisão decimal exigida.

**RD-05 — Reimportação de arquivos**

Um arquivo já importado com sucesso não deve ser processado novamente como uma nova importação de dados.

**RD-06 — Informes inalterados**

Um informe já existente com os mesmos valores não deve produzir duplicação nem revisão desnecessária.

**RD-07 — Revisões**

Alterações identificadas em informes existentes devem seguir a política de versionamento e rastreabilidade do sistema.

**RD-08 — Atomicidade da persistência**

A importação utiliza uma transação para as alterações financeiras.

Quando ocorre uma falha antes da confirmação, as alterações não confirmadas devem ser revertidas, evitando uma importação financeira parcialmente persistida.

**RD-09 — Auditoria**

Tentativas aceitas ou recusadas e execuções iniciadas devem produzir informações de auditoria conforme o fluxo implementado.

**RD-10 — Concorrência**

O sistema deve impedir que importações concorrentes incompatíveis comprometam a integridade dos dados.

**RD-11 — Falhas operacionais**

Falhas controladas devem produzir um estado de execução coerente e uma mensagem que auxilie o diagnóstico.

Interrupções abruptas exigem tratamento adicional para recuperar execuções abandonadas.

## 7. Evidências da análise exploratória

Arquivo analisado: `inf_diario_fi_202610.csv`.

| Métrica                                  | Resultado |
| ---------------------------------------- | --------: |
| Registros                                |   537.880 |
| CNPJs distintos                          |    25.507 |
| Chaves de negócio duplicadas             |         0 |
| Registros sem identificador de subclasse |   516.310 |

A análise demonstrou a necessidade de tratar subclasses ausentes e classificações textuais de fundos.

Essas observações correspondem ao arquivo de outubro de 2026 e não garantem o mesmo comportamento para outros períodos.

## 8. Decisões de domínio

| Código | Decisão                                            | Situação                                         |
| ------ | -------------------------------------------------- | ------------------------------------------------ |
| DM-01  | Separar fundos de informes diários                 | Implementada                                     |
| DM-02  | Utilizar chave composta com subclasse opcional     | Implementada na lógica de importação             |
| DM-03  | Validar tipos e campos antes da persistência       | Implementada                                     |
| DM-04  | Impedir reimportação de arquivo concluído          | Implementada                                     |
| DM-05  | Distinguir informes novos, inalterados e revisados | Implementada; validação operacional em andamento |
| DM-06  | Auditar tentativas e execuções                     | Implementada                                     |
| DM-07  | Utilizar transação para alterações financeiras     | Implementada                                     |
| DM-08  | Impedir importações concorrentes incompatíveis     | Implementada                                     |
| DM-09  | Recuperar automaticamente execuções abandonadas    | Pendente                                         |
| DM-10  | Medir desempenho com arquivos completos            | Em validação                                     |

## 9. Limitações conhecidas da v0.1

### 9.1. Recuperação de execuções interrompidas

O encerramento abrupto do processo pode deixar uma execução registrada como `PROCESSING`, mesmo após o PostgreSQL reverter a transação financeira.

O sistema ainda precisa de um mecanismo seguro para identificar e recuperar essas execuções sem confundi-las com importações legítimas de longa duração.

### 9.2. Observabilidade

O importador ainda não apresenta acompanhamento detalhado de progresso durante o processamento do CSV.

### 9.3. Desempenho

O tempo de importação de arquivos completos ainda está sendo medido.

Não há, nesta etapa, uma meta de desempenho validada por benchmark.

### 9.4. Validação operacional

A suíte automatizada possui testes de unidade e integração, mas a execução completa com o arquivo real ainda precisa ser confirmada antes da conclusão da versão.

## 10. Próximas validações

1. Concluir a importação real de outubro de 2026.
2. Conferir contadores e integridade dos dados persistidos.
3. Verificar o comportamento de reimportação do mesmo arquivo.
4. Avaliar o tempo de processamento e possíveis gargalos.
5. Implementar recuperação segura de execuções interrompidas.
6. Consolidar as evidências para a entrega da v0.1.

## 11. Referências

- [CVM — Informes Diários de Fundos de Investimento](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)
- [FundWatch — Modelo de Dados](data-model.md)
- [FundWatch — Requisitos do Sistema](../product/requirements.md)

---

**Nota:** esta documentação descreve o domínio conhecido da implementação v0.1. A conclusão funcional depende da validação do fluxo completo de importação e persistência com dados reais.
