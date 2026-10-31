# ADR-004: Algoritmo de Prevenção de Duplicados na Sincronização Offline das Docas (US-3)

- **Data:** 2026-10-29
- **Estado:** Aceite

## Contexto

Para responder à **US-3**, as docas sem rede móvel guardam temporariamente os eventos de viagem na memória local. Quando a conetividade é reestabelecida, o lote de viagens acumulado é reenviado. É necessário garantir que eventuais retransmissões não provoquem registos ou cobranças duplicadas.

## Decisão

Implementar um **mecanismo de proteção contra reenvios baseado num algoritmo de cálculo de hash único gerado na doca local**, garantindo que a execução repetida da mesma mensagem produz exatamente o mesmo efeito final no sistema do que uma única execução:

- A doca calcula um identificador único para cada viagem através do algoritmo `SHA-256(docaId + bicicletaId + timestampInicio)`.
- Ao receber o lote, o `GestaoViagens` verifica se esse hash já foi processado. Registos com hash repetido são ignorados, assegurando que o sistema mantém o estado correto sem voltar a criar a viagem.

## Alternativas Rejeitadas

- **Confiar no carimbo de data/hora de chegada ao servidor:** rejeitado porque o horário de receção no servidor não reflete o momento real da viagem;
- **Pesquisa de sobreposição de horários na base de dados:** rejeitada por ser ineficiente em termos de desempenho e sujeita a erros.

## Consequências

- **Vantagens:** garantia de que a submissão repetida da mesma viagem é processada com sucesso sem gerar registos em duplicado, eliminando o risco de dupla cobrança em envios diferidos;
- **Trade-offs / Custos:** cria uma **Conascência de Algoritmo (CoA)** entre o software da doca e o servidor central (ambos têm de partilhar a mesma fórmula de hash).