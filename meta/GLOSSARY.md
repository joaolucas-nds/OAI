# GLOSSARY.md — Termos do Projeto

> **Opcional.** Use quando o projeto tem vocabulário próprio (nomes de módulos, conceitos, identificadores) que o assistente reexplicaria a cada sessão sem isto.
> Mantenha curto: só o que não é óbvio para alguém de fora.

---

## Conceitos do projeto
- **Código de referência** — código do fabricante (ex: `1660730013300`, `PR70671`, `00611`). Aparece no nome do arquivo, no padrão `Marca - Código Referência - Descrição`. É a âncora principal do matching. NÃO confundir com código interno.
- **Código interno** — ID do sistema da loja (coluna `Interno`). NÃO aparece nos nomes dos arquivos e NÃO é usado para casar arquivos. Serve só como identificador no sistema do usuário.
- **Sufixo (de variação)** — marcador no FIM do nome que indica uma variação da mesma imagem: `(A)` = ambiente, `v2`/`v3` = segunda/terceira versão, `face 2` = variação de face. É destacado antes do matching e reescrito depois (`(A)`→`(Ambiente)`), conforme a tabela configurável.
- **Base (do nome)** — o nome do arquivo sem extensão e sem sufixo de variação, usado para o matching. Ex: de `ALMEIDA - 00611 - PISO... (A).jpg` a base é `ALMEIDA - 00611 - PISO...`.
- **Marcadores internos** — símbolos `* # + !` no fim de valores da planilha indicando status da loja (descontinuado etc.). Devem ser ignorados no matching e removidos do novo nome (`limpar_valor_planilha`).
- **Imagem de ambiente** — foto do produto aplicado em um ambiente (vs. foto do produto isolado). Marcada com `(A)`.
- **Golden set** — conjunto de pares (nome de arquivo → linha esperada da planilha) extraído de uma pasta real bem-feita, usado para medir a % de acerto do motor a cada mudança.
- **Threshold de seleção** vs **threshold de exibição** — o primeiro define a partir de que score um match é pré-selecionado para ação; o segundo, a partir de que score um match aparece na tabela (para revisão). Hoje há só um; a separação está no ROADMAP F2.

## Arquiteturas / módulos
- **MotorMatching** — classe que encapsula o matching hierárquico (código→fuzzy). Coração do acerto.
- **ThreadVarredura** — QThread que varre a pasta e roda o matching sem travar a UI.
- **ThreadAcao** — QThread que executa renomear/copiar/mover sem travar a UI.
- **matching_engine** (planejado) — módulo puro-Python a ser extraído da GUI para permitir testes (ROADMAP F2).

## Ações (os 5 modos)
- **renomear** — renomeia in-place na mesma pasta.
- **copiar** — copia para a pasta destino, mantém o original.
- **mover** — move para a pasta destino.
- **renomear_copiar** — renomeia in-place e copia o renomeado para a pasta destino.
- **renomear_mover** — renomeia in-place e move o renomeado para a pasta destino.

## Scorers do RapidFuzz (referência rápida)
- **token_sort_ratio** — ordena os tokens e compara; sensível a conteúdo extra (não infla com subconjunto).
- **token_set_ratio** — compara conjuntos; **retorna 100 se uma string é subconjunto da outra** → causa da inflação; evitar como scorer único (DEC-002).
- **WRatio** — escolhe a estratégia conforme a razão de comprimento das strings; mais equilibrado.
- **partial_ratio** — melhor substring; útil quando uma string é claramente trecho da outra.
