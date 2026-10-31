# Características Arquiteturais

## 1. Enquadramento 
Este documento apresenta a análise, classificação e priorização das características arquiteturais (*-ilities*) para o novo sistema municipal de bicicletas partilhadas *Lisboa Pedala*.

O objetivo principal desta fase é traduzir as necessidades do negócio, os requisitos funcionais e o contexto operacional (como picos de procura, falhas de rede e restrições legais) em capacidades estruturais e operacionais mensuráveis que irão governar as decisões de design e a escolha do estilo arquitetural do sistema.

Seguindo a metodologia de Richards & Ford, este ficheiro organiza-se em: 
1. **Características candidatas:** identificação de até 7 características (explícitas e implícitas) diretamente fundamentadas em pistas do enunciado;
2. **Seleção das Top 3 prioritárias:** definição dos três principais direcionadores do sistema, sem ordenação estrita;
3. **Decomposição de característica composta:** desdobramento de uma preocupação ampla em fatores mensuráveis;
4. **Cenários concretos:** definição de cenários objetivos para cada uma das Top 3 características.

## 2. Características candidatas
| Característica Candidata | Tipo | Categoria | Pista/Excertos |
| :---------------- | :------: | :----: | ----: |
| Elasticidade a pedido | Implícita | *Cloud* | "Cerca de 70% dos desbloqueios acontecem entre as 8h00–9h30 e as 17h30–19h00. Em eventos (Santos Populares, maratona) a procura em algumas estações multiplica por 4." |
| Disponibilidade | Implícita | Operacionais | "O contrato de concessão aplica uma multa por cada hora em que mais de 10% das estações não conseguirem desbloquear bicicletas." |
| Robustez | Implícita | Operacionais | "As docas comunicam por rede móvel e há zonas onde a rede falha com frequência." |
| Privacidade | Explícita | Transversais | "O percurso de cada viagem é dado pessoal (RGPD)." |
| Arquivabilidade | Explícita | Transversais | "As faturas são comunicadas à Autoridade Tributária e guardadas durante 10 anos." |
| Configurabilidade | Explícita | Estruturais | "Duas câmaras vizinhas mostraram interesse em usar a plataforma com tarifários próprios." |
| Extensibilidade | Explícita | Estruturais | "Dentro de um ano, a Câmara quer publicar a ocupação das estações como dados abertos." |

## 3. Top 3
O Top 3 escolhido foi **Disponibilidade; Elasticidade a pedido e Privacidade**:
- **Disponibilidade**: como a internet móvel das estações falha muitas vezes, o sistema tem de continuar a funcionar mesmo offline. A estação precisa de guardar as viagens na sua própria memória e enviá-las mais tarde para o servidor, garantindo que as pessoas conseguem sempre tirar ou devolver bicicletas sem que a empresa pague multas;
- **Elasticidade a pedido (On-Demand Elasticity)**: quase toda a gente usa as bicicletas à mesma hora (nas horas de ponta ou em dias de grandes eventos). O sistema tem de conseguir aumentar a sua capacidade sozinho durante esses picos para não encravar, e voltar ao normal quando a cidade acalma para não gastar dinheiro em servidores desnecessários;
- **Privacidade**: como o GPS regista o caminho exato de cada viagem, estes dados são muito sensíveis. O sistema tem de separar a identidade da pessoa do percurso que ela fez antes de guardar a informação, para que seja impossível saber por onde um utilizador específico esteve a andar.

### 3.1. Outras consideradas
As outras características que foram consideradas para o Top 3 foram:
- **Robustez**:
    - *O que significa:* é a capacidade de as estações aguentarem falhas técnicas (como a internet cair) sem irem abaixo;
    - *Por que não ficou no Top 3:* funciona como um meio para atingir um fim. A robustez é apenas o mecanismo técnico que se usa para garantir a **Disponibilidade** (que é o que realmente importa para não se pagar multas).
- **Arquivabilidade:**
    - *O que significa:* é a obrigação de guardar as faturas e dados de pagamento em segurança durante 10 anos para as finanças;
    - *Por que não ficou no Top 3:* é uma regra legal obrigatória, mas fica resolvida apenas dentro do módulo de faturação. Não altera a estrutura nem a forma como o sistema principal funciona no dia a dia.
- **Configurabilidade:**
    - *O que significa:* é a facilidade de alterar preços, tempos gratuitos ou criar tarifários para novos municípios sem ter de chamar programadores para alterar o código;
    - *Por que não ficou no Top 3:* consegue-se resolver facilmente com tabelas de definições dentro do módulo de tarifários, sem precisar de mudar a arquitetura de todo o sistema.
- **Extensibilidade:**
    - *O que significa:* é a facilidade de juntar novas funcionalidades no futuro (como partilhar os dados de ocupação das estações com a Câmara daqui a um ano) sem estragar o que já está feito;
    - *Por que não ficou no Top 3:* é uma melhoria para o futuro. Resolve-se deixando APIs bem preparadas no módulo das estações, não sendo um problema crítico para o lançamento do sistema.

## 4. Característica composta
Uma característica composta para este sistema seria a **agilidade**. A agilidade é a capacidade de o sistema se adaptar e mudar rapidamente sem compilações. Como não se consegue medir a agilidade diretamente, dividimo-la em três partes fáceis de controlar:
1. **Modularidade**: permite alterar uma regra, como os preços do passe, apenas no seu sítio próprio, sem correr o risco de estragar o resto da aplicação;
2. **Testabilidade**: garante que existem verificações automáticas para ter a certeza de que uma alteração nova não estragou nada do que já funcionava;
3. **Deployabilidade**: permite lançar melhorias ou correções rapidamente e sem ter de desligar o sistema para os utilizadores.

## 5. Cenários concretos
Para cada característica do Top 3, é necessário um cenário concreto do que significa neste sistema:
- **Disponibilidade**
    - *O que acontece*: a ligação de internet falha em 15 estações na hora de ponta da manhã;
    - *O que o sistema faz*: a estação passa a trabalhar sozinha em modo offline, permitindo que as pessoas continuem a tirar e devolver bicicletas normalmente com o cartão ou a app. Assim que a internet voltar, a estação envia os dados das viagens pendentes para o servidor;
    - *Como se sabe que correu bem*: nenhuma viagem é recusada por falta de rede e a empresa não paga multas por indisponibilidade.
- **Elasticidade a pedido**
    - *O que acontece*: durante os Santos Populares, surge quatro vezes mais gente a tentar tirar bicicletas ao mesmo tempo;
    - *O que o sistema faz*: o sistema percebe a enchente de pedidos e dá automaticamente mais força aos computadores centrais para responder a toda a gente sem encravar;
    - *Como se sabe que correu bem*: a aplicação confirma a abertura da bicicleta em menos de dois segundos e ninguém fica preso à espera.
- **Privacidade**
    - *O que acontece*: o utilizador termina a viagem e o GPS envia o caminho percorrido;
    - *O que o sistema faz*: o sistema separa imediatamente a identidade do utilizador (como o nome ou NIF) do percurso feito, guardando a rota de forma totalmente anónima;
    - *Como se sabe que correu bem*: é impossível para qualquer pessoa olhar para a base de dados de rotas e saber por onde um utilizador específico andou.