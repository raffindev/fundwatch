# FundWatch — Definição do Problema

**Projeto:** FundWatch  
**Categoria:** Python Backend / Engenharia de Dados Financeiros  
**Versão:** 0.1  
**Status:** Implementação em validação  
**Fonte principal:** Comissão de Valores Mobiliários (CVM)

---

## 1. Contexto

O mercado brasileiro de fundos de investimento produz informações financeiras periódicas utilizadas por analistas, instituições financeiras, desenvolvedores e aplicações especializadas.

A Comissão de Valores Mobiliários (CVM) disponibiliza dados públicos sobre fundos de investimento, incluindo indicadores como:

- Patrimônio líquido.
- Valor da cota.
- Valor total.
- Captações diárias.
- Resgates diários.
- Quantidade de cotistas.

Esses dados são publicados em arquivos que precisam ser interpretados, validados e consolidados para permitir seu uso em aplicações e análises históricas.

A disponibilidade pública dos arquivos não elimina os desafios de processamento, consistência, armazenamento e rastreabilidade.

O FundWatch foi concebido para enfrentar esses desafios por meio de uma aplicação backend desenvolvida em Python e PostgreSQL.

## 2. Problema central

**Como transformar informes diários públicos da CVM em dados financeiros estruturados, consistentes, auditáveis e reutilizáveis, sem perder o histórico de alterações?**

O consumo recorrente desses arquivos apresenta desafios técnicos e operacionais.

### 2.1. Volume de dados

Arquivos mensais podem conter centenas de milhares de registros.

Na análise exploratória do arquivo `inf_diario_fi_202610.csv`, foram identificados 537.880 registros.

O processamento desse volume exige uma estratégia de leitura e persistência que preserve a integridade dos dados e permita avaliar o desempenho da aplicação.

### 2.2. Qualidade e validação

Dados externos podem apresentar campos ausentes, valores incompatíveis ou formatos inesperados.

Sem validação, essas inconsistências podem comprometer o armazenamento e as consultas posteriores.

### 2.3. Duplicidade

Reimportações podem gerar registros repetidos quando não existe um mecanismo consistente de identificação.

A duplicação de informes pode distorcer análises e comprometer a confiabilidade do histórico.

### 2.4. Correções e reapresentações

Informações referentes a períodos anteriores podem ser corrigidas ou reapresentadas.

Uma aplicação que simplesmente substitui valores anteriores perde a capacidade de investigar mudanças.

### 2.5. Rastreabilidade

Sem auditoria, torna-se difícil responder a perguntas como:

- Qual arquivo originou determinado processamento?
- Quando a importação foi executada?
- A execução terminou com sucesso?
- Por que uma tentativa foi recusada?
- Quais informações foram modificadas?

### 2.6. Consulta histórica

A utilização recorrente de arquivos isolados dificulta a construção de uma base histórica consistente.

Aplicações consumidoras precisam de dados estruturados que possam ser consultados sem repetir todo o processamento da fonte original.

## 3. Público-alvo

O FundWatch é direcionado a contextos em que dados públicos de fundos de investimento precisam ser processados e reutilizados.

### 3.1. Desenvolvedores backend

Profissionais que desenvolvem sistemas de ingestão de dados, integrações financeiras e aplicações orientadas a bancos de dados.

### 3.2. Equipes de tecnologia de instituições financeiras

Equipes responsáveis por incorporar dados públicos externos em sistemas internos, mantendo consistência e rastreabilidade.

### 3.3. Analistas de dados financeiros

Profissionais que necessitam de informações históricas organizadas para consultas, comparações e análises.

### 3.4. Aplicações consumidoras

Sistemas que futuramente poderão consultar dados estruturados do FundWatch por meio de uma interface programática.

**Delimitação:** esses públicos representam usuários potenciais. O projeto ainda não passou por validação comercial ou implantação em uma instituição financeira.

## 4. Proposta de solução

O FundWatch é uma aplicação backend responsável por importar, validar, armazenar e rastrear informações financeiras publicadas pela CVM.

Sua proposta é transformar arquivos de origem em uma base relacional consistente, com regras explícitas de integridade e histórico.

A solução está organizada em cinco capacidades principais.

### 4.1. Ingestão

Ler arquivos CSV de informes diários da CVM, interpretando sua estrutura e seus registros.

A versão 0.1 utiliza arquivos locais como entrada.

### 4.2. Validação

Verificar campos obrigatórios, datas, números decimais, inteiros e regras de identificação dos registros.

Valores incompatíveis devem produzir mensagens de erro que permitam investigar o problema.

### 4.3. Persistência

Armazenar os dados no PostgreSQL, preservando os relacionamentos entre fundos, informes, importações e revisões.

A persistência financeira utiliza controle transacional para evitar confirmações parciais diante de falhas.

### 4.4. Integridade e histórico

Impedir duplicações indevidas e identificar alterações em informes anteriormente armazenados.

A solução deve distinguir registros novos, inalterados e revisados.

### 4.5. Auditoria

Registrar tentativas e execuções de importação, incluindo recusas, falhas e informações necessárias ao diagnóstico operacional.

## 5. Escopo da versão 0.1

A v0.1 representa a primeira entrega técnica do FundWatch.

### 5.1. Capacidades implementadas

- Leitura de arquivos CSV com Python.
- Validação de registros e tipos de dados.
- Identificação de fundos por CNPJ.
- Persistência relacional em PostgreSQL.
- Identificação de arquivos por hash SHA-256.
- Controle de tentativas e execuções.
- Prevenção de importações concorrentes incompatíveis.
- Detecção de registros novos, inalterados e modificados.
- Estrutura de revisões históricas.
- Controle transacional da persistência.
- Testes automatizados de unidade e integração.
- Execução do importador por linha de comando.

Essas capacidades estão implementadas, mas a validação operacional completa com o arquivo real permanece em andamento.

### 5.2. Validações pendentes

Antes de considerar a v0.1 concluída, será necessário:

- Confirmar a importação integral de um arquivo real da CVM.
- Conferir a quantidade de registros persistidos.
- Verificar os resultados de auditoria.
- Confirmar o comportamento de reimportação.
- Validar revisões com dados modificados.
- Medir o tempo de processamento.
- Tratar com segurança execuções interrompidas.
- Consolidar instruções reproduzíveis de instalação e execução.

## 6. Evolução planejada

A evolução do FundWatch poderá incluir:

### 6.1. API REST

Disponibilizar consultas de fundos e informes históricos por meio de endpoints documentados.

FastAPI é a tecnologia prevista para essa camada.

### 6.2. Automação da ingestão

Permitir obtenção e processamento periódico dos arquivos da CVM, reduzindo a necessidade de execução manual.

### 6.3. Consultas históricas

Oferecer filtros por fundo, classe, subclasse e intervalo de datas.

### 6.4. Observabilidade e desempenho

Implementar indicadores de progresso, medições de desempenho e mecanismos de recuperação de execuções interrompidas.

### 6.5. Ambiente reproduzível

Evoluir a configuração do projeto para facilitar a instalação, os testes e a execução em diferentes ambientes.

Docker Compose e integração contínua permanecem como possibilidades previstas no planejamento da V1.

Essas funcionalidades não devem ser apresentadas como concluídas antes de sua implementação e validação.

## 7. Limites da solução

O FundWatch não pretende:

- Executar operações de compra ou venda de ativos.
- Recomendar investimentos.
- Prever rentabilidade.
- Gerenciar carteiras de clientes.
- Integrar contas de corretoras.
- Substituir plataformas de negociação ou custódia.
- Garantir a correção de informações publicadas pela fonte original.

A aplicação utiliza dados públicos oficiais, mas isso não representa certificação ou homologação pela CVM.

O projeto também não possui, nesta etapa, evidências de adoção comercial ou utilização em produção por instituições financeiras.

## 8. Critérios de sucesso da v0.1

A primeira entrega será considerada tecnicamente validada quando:

1. Um desenvolvedor conseguir configurar o ambiente seguindo a documentação.
2. Um arquivo real compatível da CVM puder ser importado integralmente.
3. Os dados forem persistidos com integridade no PostgreSQL.
4. Arquivos já importados não produzirem duplicações.
5. Registros alterados seguirem a política de revisão documentada.
6. Falhas controladas preservarem a integridade financeira.
7. O histórico de tentativas e execuções puder ser consultado.
8. Os testes automatizados forem executados com sucesso.
9. O README apresentar instalação, configuração, execução e limitações.
10. O comportamento diante de interrupções abruptas estiver documentado e adequadamente tratado para a entrega.

A conclusão da v0.1 não depende da disponibilização de uma API REST.

## 9. Valor técnico e evolução do produto

O FundWatch demonstra a aplicação de práticas de engenharia backend em um problema real de dados financeiros.

Entre os principais aspectos técnicos estão:

- Processamento de dados externos.
- Validação e normalização.
- Modelagem relacional.
- Precisão numérica.
- Transações e rollback.
- Integridade referencial.
- Idempotência.
- Controle de concorrência.
- Auditoria.
- Testes automatizados.
- Documentação técnica.

O objetivo é construir uma base confiável que possa evoluir para um serviço de consulta e integração de dados financeiros.

A adoção real, os ganhos operacionais e os benefícios quantitativos deverão ser avaliados com evidências futuras.

## 10. Referências

- [CVM — Informes Diários de Fundos de Investimento](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)
- [Análise do Domínio](../domain/analysis.md)
- [Modelo Relacional](../domain/data-model.md)
- [Requisitos do Sistema](requirements.md)

---

**Nota:** este documento representa o posicionamento e o escopo técnico do FundWatch v0.1 em novembro de 2026. Funcionalidades planejadas são apresentadas separadamente das capacidades implementadas.
