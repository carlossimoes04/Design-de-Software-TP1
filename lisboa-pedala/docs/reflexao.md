# RELATÓRIO DE REFLEXÃO CRÍTICA E ANÁLISE ARQUITETURAL

## 1. Enquadramento

O sistema **Lisboa Pedala** foi criado usando *Domain-Driven Design* e *Architecture as Code*. O domínio foi dividido em componentes coesos (`GestaoViagens`, `SincronizacaoDocas`, `RelatoriosMunicipais`, `ContaUtilizador`, `MonitorizacaoEstacoes`, `FaturacaoEPagamentos`, `RedistribuicaoFrota`, `RelatoriosMunicipais`, `ManutencaoFrota`). Esses componentes usam uma camada de persistência relacional em SQLite. 
 Este relatório resume uma análise crítica sobre os desvios, os desafios inesperados e a sensibilidade dos mecanismos de validação usados ao longo do ciclo de vida do software.


## 2. Aspetos não previstos e ajustes
A especificação inicial do projeto mostrava os limites gerais dos componentes. Porém, ao começar a implementação, surgiram detalhes que exigiram alguns ajustes. Um dos principais problemas técnicos aconteceu na validação estática de dependências feita pelo `import-linter` no contrato 7. O motor da ferramenta calculava o fecho transitivo das importações em memória. Ele via o uso cruzado de Objetos de Transferência de Dados (`DTOs`) compartilhados em `src/shared/models.py` como uma quebra de isolamento entre pacotes de suporte e domínios. A especificação abstrata inicial não previu essa rigidez da ferramenta de análise. Para resolver o problema sem quebrar os princípios de baixo acoplamento, foi preciso ajustar a configuração e adicionar a diretiva `allow_indirect_imports = true`. Isso permitiu o uso seguro de estruturas de dados sem criar dependências de execução cruzadas entre os módulos de negócio. Além disso, surgiu um desafio ao lidar com concorrência e previsibilidade das *fixtures* de teste. Como o sistema interativo CLI permitia mudanças manuais no inventário, a base de dados ficava com efeitos colaterais que tiravam a previsibilidade dos testes de regressão. O ajuste pediu a criação de rotinas rígidas de limpeza de estado (`setup_database`) que rodavam antes de cada ciclo de testes no `pytest`. Assim, garantiu-se total isolamento entre as execuções.


## 3. Violações cometidas pela IA

De acordo com o exigido no enunciado, foram forçados e catalogados os desvios arquiteturais da IA durante a geração dos componentes. As três violações obrigatórias foram barradas imediatamente pelas *fitness functions* em pipeline de CI, correspondendo com rigor aos registos formais presentes na pasta `prompts/`:

1. **Violação 1: Quebra de Isolamento no Domínio Estável (`prompts/02-utilizadores.md`):**
   - *Desvio da IA:* Ao implementar a gestão de saldo em `conta_utilizador.py`, a IA importou diretamente `src.faturacao.faturacao_pagamentos` para emitir o recibo de pagamento.
   - *Deteção:* A *fitness function* falhou imediatamente no **Contrato 2** (`Utilizadores nao pode importar outros dominios`).
   - *Correção e Princípio:* O módulo `utilizadores` deve ser estritamente estável ($C_e = 0, I = 0,00$). A orquestração do carregamento foi delegada à camada de interface (CLI), que invoca a faturação de forma independente, preservando o isolamento de `utilizadores`.

2. **Violação 2: Acoplamento Ilícito entre Domínios Periféricos (`prompts/03-estacoes.md`):**
   - *Desvio da IA:* No componente `monitorizacao_estacoes.py`, ao validar a libertação física de uma bicicleta numa doca, a IA importou `src.utilizadores.conta_utilizador` para verificar o perfil e o nome do ciclista na estação.
   - *Deteção:* Chumbo imediato no **Contrato 4** (`Estacoes so pode importar manutencao e shared`).
   - *Correção e Princípio:* As estações desconhecem identidades de utilizadores; operam apenas com o identificador mecânico da bicicleta e da doca. A relação de negócio entre utilizador e viagem pertence exclusivamente ao orquestrador `GestaoViagens`.

3. **Violação 3: Criação de Ciclo Bidirecional e Quebra do ADP (`prompts/04-faturacao.md`):**
   - *Desvio da IA:* No ficheiro `faturacao_pagamentos.py`, para calcular o valor a cobrar, a IA importou `src.viagens.gestao_viagens` para carregar os registos originais da base de dados, gerando um ciclo fatal (`viagens` $\leftrightarrow$ `faturacao`).
   - *Deteção:* Violação bloqueada no **Contrato 5** (`Faturacao nao pode importar viagens nem estacoes`), prevenindo a quebra do *Acyclic Dependencies Principle* (ADP).
   - *Correção e Princípio:* A função de cobrança foi refatorada para receber um objeto de transferência imutável (`ViagemDTO`) por parâmetro. Desta forma, a dependência tornou-se estritamente unidirecional (`viagens` $\to$ `faturacao`), mantendo o Grafo Acíclico Dirigido (DAG) validado no ADR-007.

## 4. *Fitness Functions* vs. testes funcionais

As *fitness functions* são sensíveis a pequenas mudanças nos parâmetros do sistema, já que costumam medir o desempenho com base em critérios quantitativos específicos. Isso pode levar a uma avaliação detalhada das melhorias ou pioras, mas também pode tornar o processo mais vulnerável a flutuações menores, que nem sempre refletem mudanças reais de funcionalidade.

Já os testes funcionais focam em garantir que o sistema cumpra requisitos definidos e funciona como esperado em situações reais. Eles não costumam captar pequenas diferenças de desempenho, mas ajudam a identificar falhas mais evidentes ou desvios em relação ao comportamento esperado.

De forma geral, *fitness functions* permitem comparações precisas entre diferentes soluções ou versões de um sistema. No entanto, podem deixar de lado aspectos qualitativos importantes. Por outro lado, testes funcionais dão uma visão mais prática do funcionamento, mas podem não perceber mudanças sutis que afetam o desempenho. Assim, usar ambos de forma complementar pode trazer uma avaliação mais completa e confiável.
A estratégia de garantia de qualidade baseou-se numa dupla abordagem, cujos limites práticos ficaram claros. De um lado, as *fitness functions* fazem uma validação estática, rigorosa e sensível, que detecta erros estruturais grandes, ciclos de dependência, importações erradas entre camadas e violações de limites de pacotes. Essas funções impedem que a arquitetura se deteriore com o tempo ou com mudanças feitas pela IA. No entanto, elas não entendem o significado do negócio. Se a estrutura dos pacotes estiver certa, a *fitness function* aprova o código, mesmo que o algoritmo de cálculo de tarifas esteja errado. Do outro lado, os testes funcionais em `pytest` fazem uma validação dinâmica e semântica, voltada para o comportamento do negócio e para as regras do domínio. Esses testes pegam erros lógicos e funcionais de ponta a ponta. Eles cobrem desde o fluxo completo de desbloqueio, percurso e faturação na US-1, passando pela checagem matemática da idempotência com hash SHA-256 no reenvio de lotes offline na US-3, até a verificação da agregação certa de métricas de sustentabilidade na US-4. Porém, não garantem a organização estrutural do código. Assim, um sistema com muitos acoplamentos desnecessários pode passar nos testes funcionais, se as funções entregarem o resultado esperado.

## 5. Conclusão
A combinação de *fitness functions* com testes funcionais automatizados em `pytest` foi fundamental para o sucesso do projeto **Lisboa Pedala**. As primeiras garantem que a forma e a estrutura geral do sistema permanecem intactas, o que assegura a resiliência necessária para o teste de regeneração em aula. Os segundos garantem que a função e a lógica de negócio atendem de forma correta aos requisitos funcionais do utilizador.