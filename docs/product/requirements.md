# FundWatch — Especificação de Requisitos

**Projeto:** FundWatch  
**Documento:** Requisitos do Sistema  
**Versão:** 1.0 — Especificação inicial da V1  
**Status:** Proposta para validação técnica

---

## 1. Objetivo

Este documento define os requisitos funcionais, as regras de negócio, os requisitos não funcionais e os critérios de aceite da primeira versão do FundWatch.

Seu propósito é estabelecer uma referência verificável para análise, implementação, testes e evolução do sistema.

O problema, o público-alvo e a proposta de valor estão descritos em [Definição do Problema](problem-statement.md).

Os requisitos poderão ser refinados conforme a análise dos dados reais e a evolução da implementação. Alterações relevantes deverão ser registradas e justificadas.

## 2. Escopo da V1

A primeira versão compreenderá:

- Ingestão de arquivos oficiais de informes diários de fundos de investimento da CVM.
- Validação de estrutura e registros.
- Identificação e comunicação de inconsistências.
- Persistência histórica em PostgreSQL.
- Reprocessamento idempotente.
- Tratamento de registros corrigidos ou reapresentados.
- Consulta histórica por fundo e intervalo de datas.
- Registro de resultados e falhas das importações.
- Disponibilização de consultas por API REST.

O sistema utilizará dados públicos, sem integração com contas financeiras ou execução de operações de investimento.

## 3. Requisitos Funcionais

### RF-01 — Ingestão de dados oficiais

**Prioridade:** Obrigatória

O sistema deverá permitir a importação de arquivos de informes diários disponibilizados pela CVM, utilizando uma origem configurável.

**Critérios de aceite:**

- CA-01.1: Um arquivo real compatível poderá ser processado.
- CA-01.2: O sistema identificará falhas de leitura ou arquivos inacessíveis.
- CA-01.3: A origem utilizada será identificável no registro da execução.

### RF-02 — Validação de dados

**Prioridade:** Obrigatória

O sistema deverá verificar a compatibilidade dos dados recebidos com o esquema esperado.

As verificações deverão considerar campos obrigatórios, tipos, formatos e regras de consistência aplicáveis.

**Critérios de aceite:**

- CA-02.1: Campos obrigatórios ausentes serão identificados.
- CA-02.2: Valores incompatíveis com os tipos esperados serão identificados.
- CA-02.3: Arquivos estruturalmente incompatíveis serão rejeitados com motivo explícito.

### RF-03 — Tratamento de registros inválidos

**Prioridade:** Obrigatória

O sistema deverá identificar registros inválidos e disponibilizar informações suficientes para explicar sua rejeição.

**Critérios de aceite:**

- CA-03.1: Registros inválidos terão motivos de rejeição identificáveis.
- CA-03.2: Registros válidos poderão ser processados quando houver erros isolados em outros registros.
- CA-03.3: O relatório distinguirá registros aceitos, rejeitados e não processados, quando aplicável.

### RF-04 — Persistência histórica

**Prioridade:** Obrigatória

O sistema deverá armazenar dados históricos normalizados em PostgreSQL, respeitando a integridade e a precisão das informações.

**Critérios de aceite:**

- CA-04.1: Registros válidos serão persistidos.
- CA-04.2: Restrições de integridade impedirão estados incompatíveis com o modelo definido.
- CA-04.3: Valores numéricos serão preservados conforme a precisão aplicável.
- CA-04.4: Registros persistidos poderão ser recuperados posteriormente.

### RF-05 — Reprocessamento idempotente

**Prioridade:** Obrigatória

O sistema deverá permitir reprocessamentos sem gerar duplicidades de registros lógicos.

**Critérios de aceite:**

- CA-05.1: Reimportar dados idênticos não produzirá registros duplicados.
- CA-05.2: Reprocessamentos sem alterações preservarão os valores anteriormente armazenados.
- CA-05.3: O resultado da execução permitirá identificar registros sem alteração.

### RF-06 — Tratamento de atualizações

**Prioridade:** Obrigatória

O sistema deverá reconhecer registros previamente armazenados cujos valores tenham sido modificados na fonte e aplicar uma política documentada de atualização.

**Critérios de aceite:**

- CA-06.1: Registros existentes com informações alteradas serão identificados.
- CA-06.2: A política definida será aplicada de maneira consistente.
- CA-06.3: O resultado da execução informará a quantidade de registros atualizados.

A política definitiva será estabelecida após a análise da identidade dos registros e das características dos arquivos reais.

### RF-07 — Consulta histórica

**Prioridade:** Obrigatória

O sistema deverá permitir consultar registros históricos de um fundo ou classe em determinado intervalo de datas.

**Critérios de aceite:**

- CA-07.1: Será possível filtrar registros pelo identificador definido no modelo.
- CA-07.2: Será possível informar um intervalo de datas.
- CA-07.3: Consultas sem resultados retornarão uma resposta válida e documentada.
- CA-07.4: Parâmetros inválidos produzirão erros claros.

### RF-08 — Histórico de importações

**Prioridade:** Obrigatória

O sistema deverá registrar informações sobre cada execução de importação, incluindo seu resultado e eventuais falhas.

**Critérios de aceite:**

- CA-08.1: Cada execução terá um identificador próprio.
- CA-08.2: O resultado distinguirá registros inseridos, atualizados, rejeitados e sem alteração, conforme aplicável.
- CA-08.3: Falhas relevantes serão registradas sem exposição de credenciais ou dados sensíveis.
- CA-08.4: Será possível consultar o resultado de uma execução.

### RF-09 — API REST

**Prioridade:** Obrigatória

O sistema deverá disponibilizar consultas por meio de uma API REST implementada com FastAPI.

**Critérios de aceite:**

- CA-09.1: Os endpoints necessários às consultas da V1 estarão disponíveis.
- CA-09.2: Os contratos de entrada e saída estarão documentados.
- CA-09.3: A documentação OpenAPI será disponibilizada.
- CA-09.4: Entradas inválidas receberão respostas HTTP apropriadas.

Os caminhos e contratos definitivos serão definidos durante o desenho da API.

---

## 4. Regras de Negócio

### RN-01 — Importação parcial controlada

Erros isolados em registros não deverão necessariamente impedir a importação dos demais registros válidos.

Falhas que comprometam a interpretação estrutural do arquivo deverão interromper o processamento.

### RN-02 — Justificativa das rejeições

Todo registro rejeitado deverá possuir uma justificativa identificável e informações suficientes para investigação.

### RN-03 — Unicidade dos registros

Um mesmo registro lógico não poderá ser armazenado múltiplas vezes.

A chave de identificação será definida após a validação do esquema e dos dados reais.

### RN-04 — Idempotência

O reprocessamento de informações idênticas não deverá gerar duplicidades nem modificar desnecessariamente os valores persistidos.

### RN-05 — Atualização de informações

Registros existentes que apresentem alterações deverão seguir uma política explícita e testável de atualização.

### RN-06 — Integridade da persistência

Os resultados de uma importação deverão refletir as operações efetivamente confirmadas no banco de dados.

Falhas de persistência deverão seguir uma política transacional documentada.

### RN-07 — Rastreabilidade

Cada execução deverá produzir informações que permitam compreender seu resultado e investigar falhas relevantes.

### RN-08 — Consistência das consultas

As consultas deverão utilizar os dados efetivamente persistidos, respeitando os filtros e as regras de identificação definidos pelo domínio.

---

## 5. Requisitos Não Funcionais

### RNF-01 — Integridade

O banco de dados deverá utilizar tipos, chaves e restrições compatíveis com as regras de integridade estabelecidas.

**Verificação:** testes de persistência e restrições.

### RNF-02 — Confiabilidade

O sistema deverá apresentar comportamento previsível diante de registros inválidos, reprocessamentos e falhas controladas.

**Verificação:** testes de cenários normais, limites e falhas.

### RNF-03 — Observabilidade

As execuções deverão produzir informações estruturadas que auxiliem no diagnóstico e acompanhamento do processamento.

**Verificação:** inspeção de logs e resultados de importação.

### RNF-04 — Desempenho

O sistema deverá permitir a medição do tempo de processamento e do volume de registros tratados.

Metas quantitativas serão estabelecidas após a obtenção de medições com arquivos reais.

**Verificação:** execução de benchmarks documentados.

### RNF-05 — Manutenibilidade

O código deverá possuir responsabilidades bem delimitadas, organização consistente e testes automatizados.

**Verificação:** revisão de arquitetura, código e testes.

### RNF-06 — Reprodutibilidade

A aplicação e o PostgreSQL deverão poder ser iniciados em ambiente documentado com Docker Compose.

**Verificação:** execução seguindo as instruções do README.

### RNF-07 — Segurança básica

Credenciais e configurações sensíveis não deverão ser incorporadas ao código-fonte ou ao histórico do repositório.

**Verificação:** revisão de configuração, arquivos versionados e logs.

### RNF-08 — Integração contínua

O repositório deverá possuir um pipeline de integração contínua que execute verificações automatizadas.

**Verificação:** execução bem-sucedida do pipeline.

---

## 6. Premissas e Dependências

- A CVM será a fonte oficial primária dos dados da V1.
- A estrutura dos arquivos poderá sofrer alterações ao longo do tempo.
- O esquema deverá ser validado antes da implementação definitiva do modelo.
- A aplicação deverá tratar dados públicos de maneira responsável.
- A disponibilidade da fonte externa não estará sob controle do FundWatch.
- A execução local deverá ser reproduzível por outro desenvolvedor.

## 7. Decisões Técnicas Pendentes

As seguintes decisões serão resolvidas durante a análise e a implementação:

| ID    | Decisão pendente                                    | Dependência                         |
| ----- | --------------------------------------------------- | ----------------------------------- |
| DP-01 | Definição da chave lógica dos registros             | Análise do esquema e dos dados      |
| DP-02 | Política de atualização de registros reapresentados | Identidade e comportamento da fonte |
| DP-03 | Tratamento transacional de falhas parciais          | Estratégia de persistência          |
| DP-04 | Estratégia de leitura e processamento de arquivos   | Volume e medições reais             |
| DP-05 | Contratos e caminhos dos endpoints                  | Modelagem do domínio e casos de uso |
| DP-06 | Metas quantitativas de desempenho                   | Benchmarks iniciais                 |

Decisões arquiteturais relevantes deverão ser documentadas com contexto, alternativas consideradas e justificativa.

---

## 8. Critério Geral de Conclusão da V1

A V1 somente será considerada concluída quando seus requisitos obrigatórios estiverem implementados, testados e documentados.

A validação deverá incluir:

- Importação de dados reais da CVM.
- Tratamento verificável de registros inválidos.
- Persistência e consulta dos dados.
- Reimportação sem duplicidades.
- Tratamento documentado de atualizações.
- Testes unitários e de integração.
- Execução reproduzível com Docker Compose.
- Pipeline de integração contínua.
- README com instalação, exemplos de uso, arquitetura e limitações.

A conclusão da V1 não implica validação em ambiente de produção ou adoção por instituições financeiras.

---

## 9. Referências

- [FundWatch — Definição do Problema](problem-statement.md)
- [CVM — Informe Diário de Fundos de Investimento](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)

A documentação de domínio, arquitetura, esquema de dados e decisões técnicas complementará esta especificação conforme o projeto evoluir.
