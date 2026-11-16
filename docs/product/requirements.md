# FundWatch — Especificação de Requisitos

**Projeto:** FundWatch  
**Versão:** 0.1  
**Status:** Implementação em validação  
**Tecnologias:** Python, PostgreSQL, Psycopg 3 e pytest  
**Fonte de dados:** Comissão de Valores Mobiliários (CVM)

---

## 1. Objetivo

Definir os requisitos funcionais, as regras de negócio, os requisitos não funcionais e os critérios de aceite do FundWatch v0.1.

O documento estabelece uma referência para implementação, testes, validação e evolução do sistema.

A v0.1 concentra-se na importação de arquivos CSV da CVM, validação, persistência histórica, controle de duplicidades e auditoria.

A API REST e outras funcionalidades de integração pertencem ao planejamento de versões posteriores.

## 2. Escopo

### 2.1. Incluído na v0.1

- Leitura de arquivos CSV locais.
- Validação de estrutura e registros.
- Persistência em PostgreSQL.
- Identificação de fundos e informes.
- Prevenção de duplicidades.
- Identificação de alterações financeiras.
- Preservação de versões históricas.
- Auditoria de tentativas e execuções.
- Controle de concorrência.
- Integridade transacional.
- Execução por linha de comando.
- Testes automatizados.

### 2.2. Fora do escopo da v0.1

- API REST.
- Interface web.
- Download automático de arquivos da CVM.
- Agendamento periódico de importações.
- Autenticação de usuários.
- Dashboard financeiro.
- Recomendações de investimento.
- Operações financeiras.
- Infraestrutura distribuída.

## 3. Requisitos funcionais

### RF-01 — Leitura de arquivos CSV

**Prioridade:** Obrigatória  
**Situação:** Implementado; validação com arquivo completo em andamento

O sistema deve permitir a leitura de arquivos CSV compatíveis com o formato de informes diários da CVM.

**Critérios de aceite:**

- CA-01.1: O sistema aceita um caminho de arquivo local.
- CA-01.2: O CSV é interpretado utilizando o delimitador esperado.
- CA-01.3: Arquivos inexistentes produzem erro identificável.
- CA-01.4: O processamento utiliza leitura iterativa, sem exigir o carregamento integral do arquivo em memória.
- CA-01.5: Um arquivo real completo pode ser processado.

### RF-02 — Validação de registros

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve validar os dados recebidos antes da persistência.

**Critérios de aceite:**

- CA-02.1: Campos obrigatórios ausentes são identificados.
- CA-02.2: Datas incompatíveis são rejeitadas.
- CA-02.3: Valores decimais inválidos são identificados.
- CA-02.4: Valores inteiros incompatíveis são identificados.
- CA-02.5: As mensagens de erro permitem identificar a incompatibilidade.
- CA-02.6: Os dados financeiros preservam a precisão decimal aplicável.

### RF-03 — Identificação de fundos

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve identificar fundos ou classes pelo CNPJ informado pela CVM.

**Critérios de aceite:**

- CA-03.1: Um CNPJ existente não gera outro fundo equivalente.
- CA-03.2: Um CNPJ ainda não cadastrado pode originar um novo registro.
- CA-03.3: A classificação do fundo é armazenada conforme o formato aceito pelo esquema.
- CA-03.4: A associação entre fundos e informes preserva a integridade referencial.

### RF-04 — Persistência de informes

**Prioridade:** Obrigatória  
**Situação:** Implementado; validação integral pendente

O sistema deve armazenar informes financeiros em PostgreSQL.

**Critérios de aceite:**

- CA-04.1: Cada informe está associado a um fundo.
- CA-04.2: A data de competência é armazenada como `DATE`.
- CA-04.3: Os indicadores financeiros utilizam tipos `NUMERIC`.
- CA-04.4: A ausência de subclasse é permitida.
- CA-04.5: As restrições SQL impedem estados incompatíveis.
- CA-04.6: Os registros persistidos podem ser recuperados por consultas SQL.

### RF-05 — Controle de duplicidades

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve impedir a duplicação indevida de informes.

A chave de negócio é:

`(fund_id, reference_date, subclass_id)`

**Critérios de aceite:**

- CA-05.1: Registros duplicados dentro do mesmo arquivo são identificados.
- CA-05.2: Subclasses ausentes são tratadas de maneira consistente.
- CA-05.3: A importação não cria duas versões vigentes da mesma identidade.
- CA-05.4: As restrições do banco complementam as validações da aplicação.

### RF-06 — Idempotência de arquivos

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve identificar arquivos já importados com sucesso.

**Critérios de aceite:**

- CA-06.1: O conteúdo do arquivo é identificado por hash SHA-256.
- CA-06.2: Uma nova tentativa com arquivo anteriormente importado com sucesso é recusada.
- CA-06.3: A recusa não duplica dados financeiros.
- CA-06.4: A tentativa recusada permanece auditável.

### RF-07 — Revisões históricas

**Prioridade:** Obrigatória  
**Situação:** Implementado; validação operacional em andamento

O sistema deve identificar alterações em informes existentes e preservar a rastreabilidade das versões.

**Critérios de aceite:**

- CA-07.1: Um informe existente pode ser comparado com novos valores recebidos.
- CA-07.2: Valores inalterados não geram revisões desnecessárias.
- CA-07.3: Valores modificados seguem a política de revisão.
- CA-07.4: Somente uma versão permanece vigente para cada identidade de informe.
- CA-07.5: Versões anteriores permanecem disponíveis para investigação.

### RF-08 — Auditoria de importações

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve registrar tentativas e execuções de importação.

**Critérios de aceite:**

- CA-08.1: Cada execução possui identificador próprio.
- CA-08.2: O arquivo e seu hash são identificáveis.
- CA-08.3: O estado da execução é registrado.
- CA-08.4: Falhas controladas são registradas com mensagem de diagnóstico.
- CA-08.5: Tentativas recusadas podem ser auditadas separadamente das execuções.
- CA-08.6: Informações de auditoria podem ser consultadas no PostgreSQL.

### RF-09 — Controle de concorrência

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve impedir importações simultâneas incompatíveis.

**Critérios de aceite:**

- CA-09.1: O controle utiliza mecanismos de sincronização no PostgreSQL.
- CA-09.2: O sistema identifica arquivos já associados a importações em andamento.
- CA-09.3: Tentativas incompatíveis são recusadas sem comprometer a integridade dos dados.
- CA-09.4: As restrições SQL complementam o controle da aplicação.

### RF-10 — Integridade transacional

**Prioridade:** Obrigatória  
**Situação:** Implementado

A persistência financeira deve ocorrer de forma transacional.

**Critérios de aceite:**

- CA-10.1: Alterações financeiras são confirmadas apenas após o processamento bem-sucedido.
- CA-10.2: Falhas antes da confirmação provocam rollback.
- CA-10.3: O rollback não deixa registros financeiros parcialmente confirmados.
- CA-10.4: A auditoria de falhas pode permanecer registrada independentemente do rollback financeiro.

### RF-11 — Execução por linha de comando

**Prioridade:** Obrigatória  
**Situação:** Implementado

O sistema deve disponibilizar um comando para iniciar importações.

**Critérios de aceite:**

- CA-11.1: O usuário pode informar o caminho do arquivo.
- CA-11.2: O schema de destino pode ser selecionado entre os valores permitidos.
- CA-11.3: Argumentos inválidos produzem mensagens identificáveis.
- CA-11.4: O comando retorna código de saída apropriado nos cenários tratados.

### RF-12 — Recuperação de execuções interrompidas

**Prioridade:** Obrigatória para conclusão operacional  
**Situação:** Pendente

O sistema deve tratar execuções abandonadas após encerramento inesperado do processo.

**Critérios de aceite:**

- CA-12.1: Uma execução interrompida pode ser identificada com segurança.
- CA-12.2: O mecanismo não confunde importações demoradas com execuções abandonadas.
- CA-12.3: A recuperação preserva o histórico de auditoria.
- CA-12.4: A recuperação permite novas tentativas legítimas.
- CA-12.5: O procedimento é coberto por testes.

## 4. Regras de negócio

**RN-01 — Identidade do fundo**

Um CNPJ normalizado deve corresponder a uma única entidade `Fund`.

**RN-02 — Identidade do informe**

Um informe é identificado por fundo, data de competência e subclasse opcional.

**RN-03 — Subclasse ausente**

A ausência de subclasse é válida e não deve permitir duplicações da mesma identidade.

**RN-04 — Validação obrigatória**

Registros incompatíveis com as regras de validação devem produzir erros identificáveis.

**RN-05 — Atomicidade da importação**

Na v0.1, uma falha durante o processamento impede a confirmação parcial dos dados financeiros da execução.

A importação parcial de registros válidos, prevista na especificação inicial, não faz parte da política transacional atual.

**RN-06 — Idempotência**

Um arquivo concluído com sucesso não deve produzir uma nova importação financeira equivalente.

**RN-07 — Revisões**

Alterações nos indicadores de informes existentes devem preservar o histórico de versões.

**RN-08 — Versão vigente**

Uma identidade de informe pode possuir múltiplas versões históricas, mas somente uma versão vigente.

**RN-09 — Auditoria**

Tentativas e execuções devem possuir registros suficientes para investigar seus resultados.

**RN-10 — Concorrência**

Importações concorrentes incompatíveis devem ser impedidas.

**RN-11 — Recuperação**

Uma interrupção abrupta não deve impedir indefinidamente novas importações legítimas.

## 5. Requisitos não funcionais

### RNF-01 — Integridade

O banco deve utilizar chaves, restrições e relacionamentos compatíveis com as regras de domínio.

**Verificação:** testes de persistência e inspeção do esquema SQL.

### RNF-02 — Precisão financeira

Valores monetários e de cotas devem preservar a precisão decimal definida.

**Verificação:** testes de validação e persistência.

### RNF-03 — Confiabilidade

Falhas controladas devem produzir resultados previsíveis, com rollback e auditoria apropriados.

**Verificação:** testes de falhas e transações.

### RNF-04 — Manutenibilidade

O código deve possuir responsabilidades separadas entre leitura, validação, serviço de importação e persistência.

**Verificação:** revisão de arquitetura e testes automatizados.

### RNF-05 — Desempenho

O tempo de processamento de arquivos completos deve ser mensurável.

Metas quantitativas serão definidas após a obtenção de benchmarks reais.

**Verificação:** execução com arquivos da CVM e registro do tempo decorrido.

### RNF-06 — Observabilidade

O sistema deve registrar informações suficientes para diagnosticar execuções e falhas.

O acompanhamento detalhado de progresso durante a importação ainda não está implementado.

**Verificação:** auditoria, mensagens de erro e inspeção de execução.

### RNF-07 — Segurança de configuração

Credenciais não devem ser incorporadas ao código-fonte ou aos arquivos versionados.

**Verificação:** revisão de `.gitignore`, `.env.example` e configuração do banco.

### RNF-08 — Reprodutibilidade

Outro desenvolvedor deve conseguir instalar as dependências, configurar o banco e executar o importador seguindo a documentação.

**Verificação:** instalação em ambiente configurado a partir das instruções do README.

### RNF-09 — Testabilidade

O sistema deve possuir testes automatizados de unidade e integração.

**Verificação:** execução da suíte com pytest.

## 6. Tecnologias e dependências

A implementação v0.1 utiliza:

| Tecnologia    | Responsabilidade                       |
| ------------- | -------------------------------------- |
| Python        | Implementação backend                  |
| PostgreSQL    | Persistência relacional                |
| Psycopg 3     | Comunicação com PostgreSQL             |
| pytest        | Testes automatizados                   |
| python-dotenv | Configuração por variáveis de ambiente |
| Git/GitHub    | Versionamento e colaboração            |

A versão de desenvolvimento utiliza Python 3.14 e PostgreSQL 18.6.

O projeto declara suporte a Python 3.11 ou superior em sua configuração de empacotamento.

## 7. Evolução posterior

Após a conclusão da v0.1, poderão ser desenvolvidos:

- API REST com FastAPI.
- Endpoints de consulta histórica.
- Download automático dos arquivos da CVM.
- Agendamento de importações.
- Monitoramento de progresso.
- Otimizações de processamento em lote.
- Docker Compose.
- Pipeline de integração contínua.
- Camada analítica e visualizações financeiras.

Essas funcionalidades não fazem parte dos critérios obrigatórios da v0.1, exceto quando incorporadas formalmente ao seu escopo.

## 9. Referências

- [Definição do Problema](problem-statement.md)
- [Análise do Domínio](../domain/analysis.md)
- [Modelo Relacional](../domain/data-model.md)
- [CVM — Informes Diários de Fundos de Investimento](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)

---

**Nota:** os requisitos refletem a implementação conhecida do FundWatch v0.1 em novembro de 2026. Os estados de validação deverão ser atualizados conforme os testes operacionais forem concluídos.
