# ADR-001: Seleção do Top 3 de Características Arquiteturais 

- **Data:** 2026-10-28 
- **Estado:** Aceite 

## Contexto
O sistema de bicicletas partilhadas *Lisboa Pedala* funciona numa cidade exigente: a rede móvel falha em várias zonas, a procura dispara nas horas de ponta e em eventos (até 4 vezes a carga normal), e a câmara aplica multas se as estações ficarem indisponíveis. Além disso, o GPS de cada viagem guarda dados pessoais sensíveis, que o RGPD obriga a proteger.

É preciso decidir quais são as características mais importantes do sistema, porque são elas que vão orientar todas as decisões de design.

## Decisão 
Escolher a **Disponibilidade**, a **Elasticidade a Pedido** e a **Privacidade** como as 3 características prioritárias:
1. **Disponibilidade:** as docas têm de continuar a funcionar sem rede. Guardam as viagens localmente e enviam-nas para o servidor quando a ligação voltar;
2. **Elasticidade a Pedido:** o sistema tem de aumentar e diminuir os recursos sozinho, conforme a procura. Mais capacidade nos picos (8h00–9h30, 17h30–19h00 e grandes eventos), menos nas horas calmas;
3. **Privacidade:** quando a viagem termina, o percurso GPS deve ficar separado da identidade de quem a fez, para que ninguém consiga saber por onde andou determinada pessoa.

## Alternativas Rejeitadas 
- **Pôr a Extensibilidade e a Configurabilidade no Top 3:** a câmara quer, no futuro, abrir os dados e chegar aos concelhos vizinhos, mas isso não é o mais urgente. Se o serviço falhar no dia a dia ou houver multas por indisponibilidade, o projeto fica em risco logo à partida;
- **Escolher Segurança em geral em vez de Privacidade:** a segurança dos acessos é um requisito básico que qualquer sistema tem de cumprir. A privacidade da localização é diferente: exige decisões específicas sobre como se guardam e separam os dados.

## Consequências 
- **Vantagens:** pequenas falhas de rede deixam de afetar o serviço, o sistema responde depressa mesmo nos picos e cumpre o RGPD de forma rigorosa;
- **Desvantagens (trade-offs):** gerir o funcionamento sem rede nas docas dá mais trabalho e complica o sistema; a sincronização tem de ser feita de modo a que uma viagem enviada duas vezes não fique registada duas vezes; e deixa de ser possível ver diretamente os percursos de cada utilizador.