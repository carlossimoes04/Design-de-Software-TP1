# ADR-006: Adoção do Modelo C4 (Níveis 1 a 3)

- **Data:** 2026-10-31
- **Estado:** Aceite

## Contexto 
Segundo o enunciado, foi pedida uma forma clara de desenhar e documentar a arquitetura do *Lisboa Pedala*, desde a forma como os utilizadores usam o sistema até à organização das pastas no código.

## Decisão 
1. **Usar o Modelo C4 (Simon Brown):** organizar os desenhos no ficheiro `docs/diagramas/diagramas.md` em 3 níveis simples de detalhe:
    - **Nível 1 (Contexto):** visão geral do *Lisboa Pedala* visto de fora (quem o usa e com que sistemas externos fala);
    - **Nível 2 (Contentores):** onde o código corre na prática (CLI/REST em Python, o processo do servidor, a base de dados SQLite e os simuladores); 
    - **Nível 3 (Componentes):** como o servidor se divide internamente nas 7 pastas de código em `src/` e como elas comunicam entre si.
2. **Escrever os diagramas em *Mermaid*:** fazer os desenhos diretamente em texto/código dentro do Markdown, para que qualquer pessoa possa editar e ver as diferenças no Git; 
3. **Incluir legenda em todos os desenhos:** colocar uma legenda simples em cada nível para explicar o que significa cada elemento e cada seta.

## Consequências

**Vantagens:** 
- Qualquer pessoa entende a arquitetura rapidamente, do geral para o detalhe; 
- Os diagramas estão guardados em texto no Git, por isso é fácil ver o que mudou;
- Fica tudo 100% coerente com a estrutura de pastas em Python e com o ficheiro `03`. 

**Trade-offs:** 
- O *Mermaid* tem algumas limitações visuais em comparação com ferramentas de desenho manual; 
- É preciso ter a disciplina de atualizar o texto do Mermaid sempre que se mudar o nome de uma pasta em `src/`.