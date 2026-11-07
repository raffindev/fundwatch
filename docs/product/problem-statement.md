# FundWatch — Definição do Problema

**Projeto:** FundWatch  
**Categoria:** Backend Python / Engenharia de Dados Financeiros  
**Documento:** Definição do Problema  
**Status:** Definição inicial — V1

---

## 1. Contexto

O mercado de fundos de investimento produz informações periódicas utilizadas por analistas, instituições financeiras e aplicações que acompanham a evolução de fundos ao longo do tempo.

No Brasil, a Comissão de Valores Mobiliários (CVM) disponibiliza conjuntos de dados públicos contendo informações sobre fundos de investimento, incluindo patrimônio líquido, valor das cotas, captações, resgates e quantidade de cotistas.

Essas informações são disponibilizadas em arquivos que precisam ser obtidos, interpretados e consolidados para permitir análises históricas.

Embora os dados estejam publicamente disponíveis, sua utilização em aplicações exige processos de ingestão, validação, armazenamento e consulta.

O FundWatch nasce como uma proposta de solução backend para esse processo, utilizando dados públicos oficiais como fonte primária.

**Fonte de referência:**  
[Informe Diário de Fundos de Investimento — CVM](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)

## 2. Problema Central

O consumo recorrente de dados públicos de fundos de investimento pode exigir atividades repetitivas de obtenção, leitura, validação e consolidação de arquivos.

Quando essas atividades dependem de operações manuais, surgem dificuldades relacionadas à eficiência operacional, confiabilidade dos dados e manutenção de históricos consistentes.

Entre os principais problemas identificados estão:

- **Processamento repetitivo:** necessidade de obter e tratar periodicamente novos arquivos.
- **Volume de informações:** dificuldade de localizar e consultar registros específicos em conjuntos extensos de dados.
- **Inconsistências:** possibilidade de registros incompletos, inválidos ou incompatíveis com a estrutura esperada.
- **Duplicidade:** risco de armazenar informações repetidas durante reimportações.
- **Atualizações da fonte:** necessidade de tratar registros corrigidos ou reapresentados.
- **Rastreabilidade:** dificuldade de identificar quais registros foram processados, rejeitados ou atualizados.
- **Consulta histórica:** necessidade de consolidar informações de diferentes períodos para acompanhar a evolução dos fundos.

O problema central não é a ausência de dados, mas a necessidade de transformá-los em informações estruturadas, persistentes, verificáveis e acessíveis.

## 3. Público-Alvo

O FundWatch é direcionado principalmente a contextos em que informações públicas sobre fundos de investimento precisam ser processadas e consultadas de maneira recorrente.

### 3.1 Analistas de dados financeiros

Profissionais que precisam consultar informações históricas de fundos, comparar períodos e identificar alterações nos dados publicados.

### 3.2 Equipes de tecnologia de instituições financeiras

Desenvolvedores e equipes responsáveis por integrar dados externos a sistemas internos, mantendo consistência, rastreabilidade e disponibilidade das informações.

### 3.3 Aplicações consumidoras de dados

Sistemas que necessitam acessar informações históricas estruturadas por meio de uma interface programática, sem implementar individualmente todo o processo de leitura e consolidação dos arquivos originais.

**Delimitação:** esses públicos representam usuários e consumidores potenciais da solução. Ainda não foram realizadas entrevistas ou validações de uso com instituições reais.

## 4. Impactos Operacionais

Os problemas identificados podem produzir diferentes consequências operacionais.

### 4.1 Aumento do esforço manual

A repetição de atividades de coleta, preparação e consolidação exige tempo que poderia ser destinado à análise dos dados.

### 4.2 Risco de informações inconsistentes

Registros inválidos, duplicados ou incorretamente interpretados podem comprometer consultas e análises posteriores.

### 4.3 Dificuldade de investigação de falhas

Sem um histórico estruturado de processamento, pode ser difícil determinar por que determinado registro não foi importado ou por que uma informação foi alterada.

### 4.4 Dificuldade de manutenção do histórico

Arquivos publicados em períodos distintos precisam ser consolidados de maneira consistente, considerando possíveis correções e reapresentações.

### 4.5 Dependência do formato original

Aplicações que consomem diretamente os arquivos ficam responsáveis por interpretar a estrutura da fonte, implementar validações e administrar atualizações.

Esses impactos constituem hipóteses operacionais fundamentadas nas características do problema. Sua magnitude deverá ser avaliada por meio de testes, medições e eventual utilização real do sistema.

## 5. Solução Proposta

O FundWatch será um serviço backend desenvolvido em Python, responsável por transformar arquivos públicos oficiais da CVM em dados históricos estruturados e consultáveis.

A primeira versão deverá oferecer as seguintes capacidades:

1. **Ingestão:** obter e processar arquivos de dados a partir de uma origem configurável.
2. **Validação:** verificar estrutura, tipos e consistência dos registros.
3. **Tratamento de rejeições:** identificar registros inválidos e apresentar os motivos correspondentes.
4. **Persistência:** armazenar dados históricos normalizados em PostgreSQL.
5. **Idempotência:** permitir reprocessamentos sem gerar duplicidades.
6. **Atualização:** aplicar uma política definida para registros corrigidos ou reapresentados.
7. **Consultas:** disponibilizar informações históricas por fundo e intervalo de datas.
8. **Rastreabilidade:** registrar resultados e falhas das execuções de importação.
9. **Integração:** disponibilizar consultas por meio de uma API REST documentada.

### 5.1 Diretrizes técnicas

A implementação deverá priorizar:

- Separação clara de responsabilidades.
- Modelagem consistente do domínio.
- Integridade e precisão dos dados financeiros.
- Tratamento explícito de erros.
- Testes automatizados.
- Configuração segura da aplicação.
- Execução reproduzível.
- Documentação técnica e funcional.

### 5.2 Resultado esperado

Ao concluir a V1, deverá ser possível iniciar o ambiente, importar um arquivo real da CVM, verificar o resultado do processamento e consultar os registros persistidos por meio da API.

O comportamento deverá ser verificável por testes automatizados e por instruções de execução documentadas.

## 6. Limites da Solução

A primeira versão terá escopo deliberadamente controlado.

Não fazem parte da V1:

- Autenticação e gerenciamento de usuários.
- Controle avançado de permissões.
- Dashboard financeiro elaborado.
- Recomendações de investimento.
- Previsões de preços ou rentabilidade.
- Execução de ordens financeiras.
- Integração com contas de corretoras.
- Alertas automáticos.
- Infraestrutura distribuída de alta complexidade.

O FundWatch não pretende substituir sistemas de negociação, custódia, gestão de carteiras ou serviços especializados de análise financeira.

A utilização de dados públicos oficiais não implica certificação, homologação ou conformidade regulatória da aplicação.

Funcionalidades adicionais poderão ser avaliadas após a conclusão e validação da primeira versão.

---

## 7. Critérios de Sucesso da V1

A primeira versão será considerada funcional quando:

- Um desenvolvedor conseguir configurar e executar o projeto seguindo a documentação.
- Um arquivo real da CVM puder ser importado e processado.
- Registros inválidos forem identificados com motivos verificáveis.
- Dados válidos forem armazenados com integridade.
- Reimportações não produzirem registros duplicados.
- Correções de dados seguirem uma política documentada.
- Consultas históricas estiverem disponíveis por API REST.
- Testes automatizados cobrirem comportamentos normais e situações de falha.
- A aplicação e o banco puderem ser iniciados com Docker Compose.
- Um pipeline de integração contínua executar os testes.
- O README apresentar claramente a finalidade, a arquitetura, a instalação, as limitações e os exemplos de uso.

O sucesso técnico será demonstrado por funcionalidades executáveis e evidências verificáveis.

Ganhos operacionais, adoção por usuários e resultados de produção somente serão declarados quando existirem medições ou evidências correspondentes.

---

## 8. Referências

**Comissão de Valores Mobiliários (CVM)**  
Conjunto de dados: Informe Diário de Fundos de Investimento  
https://dados.cvm.gov.br/dataset/fi-doc-inf_diario

**Documentação complementar do projeto:**  
Os requisitos funcionais, regras de negócio, decisões arquiteturais e detalhes da modelagem serão mantidos em documentos específicos, evitando duplicação desnecessária neste documento.
