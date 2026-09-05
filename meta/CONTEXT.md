# CONTEXT.md — Organizador de Arquivos Inteligente

> Arquivo **estável**. O assistente lê no início de cada sessão para se ambientar.
> Muda pouco: só em alteração estrutural (stack, arquitetura, escopo, nova armadilha descoberta).
> Mantenha enxuto — descreve o que o projeto É, não o que está acontecendo agora (isso é o STATUS).

---

## Estrutura de Documentação (KCM v1.122.0)
Este projeto migrou do layout flat antigo (KCM pré-v1.90) para o contrato atual:
- **Raiz:** `CLAUDE.md` (guia raiz do Claude Code), `.claude/settings.json` (permissões), `.claude/skills/{apply-wo,wrap}/SKILL.md` (comandos do modo Code), `.gitignore`, `.flatdropignore`.
- **`meta/`:** `CEREBRO.md` (comportamento do assistente), `CONTEXT.md`, `STATUS.md`, `DECISIONS.md`, `CHANGELOG.md`, `IDEAS.md`, `ROADMAP.md`, `GLOSSARY.md`, `HISTORY.md`, `SPEC.md`, `LOG-TEMPLATE.md`, `workorders/_TEMPLATE.md`.
- **Modo:** Code ligado (ASU desligado). Ver DEC-007 para a migração.

## Visão Geral
Ferramenta desktop (Windows) que organiza arquivos em massa usando uma planilha como fonte de verdade. Lê um CSV/XLSX exportado do Google Sheets, varre uma pasta de arquivos (imagens de produtos: pisos, louças, etc.), e associa cada arquivo físico a uma linha da planilha por **código de referência** e/ou **comparação aproximada de nome (fuzzy)**. A partir do match, permite renomear, copiar e mover os arquivos em massa — com preview, seleção manual e log auditável. O usuário é dono de uma loja de materiais de construção e mantém ~milhares de itens cujas imagens precisam ser nomeadas e agrupadas segundo a planilha do sistema.

## Stack Tecnológica
- **Linguagem:** Python 3.11+
- **Interface gráfica:** PySide6 (Qt6)
- **Leitura de dados:** pandas + openpyxl (XLSX) / leitura nativa CSV
- **Detecção de encoding:** chardet
- **Comparação aproximada:** RapidFuzz (`fuzz`, `process`) — usado dentro de `UTILITÁRIOS/matching_engine.py`, não em `main.py`
- **Operações de arquivo:** pathlib + shutil (stdlib)
- **Log/export:** openpyxl
- **Build do executável:** PyInstaller (`--onefile --windowed`)
- **Persistência de config:** JSON local (`config.json` ao lado do .exe)
- **Testes:** golden set + harness (`UTILITÁRIOS/test_matching.py`, sem argumentos, 24/24) — ver DEC-008

## Estrutura do Projeto
```
OrganizadorArquivos/
├── main.py                       # GUI (~1300 linhas) — importa o motor, não o contém
│   ├── ThreadVarredura            # varredura+matching em background (QThread)
│   ├── ThreadAcao                 # renomear/copiar/mover em background (QThread)
│   ├── AbaCorrespondencias        # tabela de resultados editável + ações
│   ├── AbaSemMatch                # arquivos sem correspondência
│   ├── AbaConfiguracoes           # mapeamento de sufixos editável
│   ├── AbaLog                     # log + exportar Excel + desfazer
│   └── JanelaPrincipal            # orquestra tudo + barra superior
├── UTILITÁRIOS/
│   ├── matching_engine.py        # MOTOR v2: MotorMatching, Resultado, PesosScore — puro Python, sem PySide6/pandas
│   ├── spreadsheet_loader.py     # carregar_planilha(), coluna_como_texto() — loader único (GUI + harness)
│   └── test_matching.py          # harness do golden set (ver test/)
├── test/
│   ├── planilha_referencia.csv   # referência congelada (119 linhas) — ver DEC-008
│   └── golden_set.csv            # 24 casos, chave = Interno
├── config.json                    # gerado na 1ª execução (não versionar dados sensíveis)
└── dist/OrganizadorArquivos.exe  # saída do PyInstaller
```
> A modularização prevista no ROADMAP F2 está feita desde a WO 0005 (2026-09-05): o motor vive só em `UTILITÁRIOS/matching_engine.py`, testável isoladamente e sem duplicata em `main.py`.

## Convenções de Código
- **Nomes:** arquivos/funções/variáveis em inglês quando possível; este projeto tem forte presença de PT-BR no domínio (nomes de colunas, rótulos de UI), então identificadores de domínio podem ser PT-BR.
- **Comentários:** PT-BR; explicam o PORQUÊ, não o QUÊ.
- **Commits:** imperativo curto em PT-BR.
- **Estilo:** legibilidade primeiro; performance só se medida.
- **Docstring:** em toda função/classe pública.

## Como o MOTOR DE MATCHING funciona (CRÍTICO)
> Esta é a peça que mais gera bug e a que mais precisa de cuidado. Leia antes de mexer.
> **Implementação real:** `UTILITÁRIOS/matching_engine.py` (classe `MotorMatching`, dataclass `Resultado`). Desde a WO 0005, `main.py` só importa — não há mais motor embutido na GUI. O comportamento descrito abaixo é conceitual e continua valendo; para o scorer atual (ponderado, não `token_set_ratio`), ver DEC-002.

O matching é **hierárquico**, em duas prioridades:

**Prioridade 1 — Código de referência (âncora segura).**
Extrai sequências alfanuméricas do nome do arquivo via regex `\b([A-Za-z]{0,4}\d[\dA-Za-z]{3,})\b` — captura `1660730013300`, `PR12147`, `00611`, `32HDA60`. Compara com os códigos extraídos da coluna de matching da planilha, de forma **BIDIRECIONAL**: match exato, código-da-planilha contido no código-do-arquivo (`PR7067 ⊂ PR70671`), ou código-do-arquivo contido no da planilha. Match por código → confiança 100.
- Motivo do bidirecional: no CSV real do usuário, a planilha às vezes tem o código "encurtado" (`PR7067`) enquanto o arquivo tem o completo (`PR70671`). Sem checar os dois sentidos, esses casos falhavam (FIX-001).

**Prioridade 2 — Fuzzy (quando não há código ou ele falha).**
Compara a *base* do nome do arquivo (sem extensão, sem sufixo, normalizada) com a coluna de matching da planilha.

**Pré-processamento essencial antes de qualquer comparação:**
1. `limpar_valor_planilha()` remove `* # + !` do FINAL dos valores da planilha (marcadores internos da loja: descontinuado, etc.). Esses símbolos NÃO entram no matching nem no novo nome.
2. `separar_sufixos()` detecta e destaca sufixos de variação (`(A)`, `v2`, `face 2`…) do final do nome ANTES do match; o match acontece só na base; o sufixo é recolado (reescrito) depois — ver GLOSSARY «sufixo».
3. `normalizar_texto()` aplica maiúsculas, troca hífen/underscore por espaço, remove `* # + ! ( ) [ ] ² ³ °`, colapsa espaços.

**Exemplo completo:**
- Arquivo: `ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62 (A).jpg`
- `separar_sufixos` → base=`ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62`, sufixo=`(A)`
- P1 extrai `00611` → encontra a linha da planilha → confiança 100
- novo nome = valor da coluna escolhida + sufixo reescrito (`(A)`→`(Ambiente)`)
- resultado: `ALMEIDA - 00611 - PISO ACET RETIF 32HDA60 32X62 CX 1,95MT² (Ambiente).jpg`

## Arquitetura — pontos-chave
- Motor de matching hierárquico (código→fuzzy) — ver DEC-001.
- Bidirecionalidade do match por código — ver FIX-001.
- Escolha de scorer fuzzy é o ponto fraco atual — ver DEC-002 e STATUS.
- GUI em abas + 2 QThreads (varredura e ação) para não travar — ver DEC-003.
- Sistema de sufixos configurável e persistido — ver DEC-004.

## Armadilhas Conhecidas (o que NÃO fazer)
1. **Usar `token_set_ratio` como scorer fuzzy** — parece ótimo porque "ignora ordem", mas retorna **100 sempre que uma string é subconjunto da outra**, independentemente de quanto texto extra a outra tenha. Resultado: nome curto/genérico ganha nota altíssima contra entradas longas da planilha → "alto valor para pouca semelhança". É a causa raiz do fuzzy ruim atual. → Usar abordagem ponderada (ver DEC-002).
2. **Comparar o nome do arquivo COM o sufixo ainda colado** — `(A)`, `v2` viram ruído e baixam o score do match correto. → Sempre `separar_sufixos()` antes de comparar.
3. **Deixar `* # +` da planilha entrarem no matching/nome** — sujam tanto o score quanto o nome final do arquivo. → `limpar_valor_planilha()` sempre.
4. **Match por código unidirecional** — só checar `cod_plan in cod_arq` perde os casos inversos. → Bidirecional sempre (FIX-001).
5. **Copiar arquivo sobre si mesmo** em `renomear_copiar`/`renomear_mover` quando a pasta destino é a mesma do original → checar `pasta_final.resolve() == origem.parent.resolve()` antes (FIX-002).
6. **Layout PySide6 com tudo numa `QHBoxLayout` só** — combos e slider se sobrepõem em telas estreitas. → Agrupar em `QGroupBox` com sub-linhas e `setFixedWidth` nos labels (FIX-003).
7. **Ler CSV do Google Sheets sem `utf-8-sig`** — vira `CÃ³digo ReferÃªncia`. → Detectar encoding (chardet) com fallback `utf-8-sig`.
8. **Deixar a regex de código capturar dimensões** — `33X57`, `50MT²` parecem código e fazem produtos de mesma medida casarem entre si (confiança 100 falsa). → Excluir medidas/dimensões de `extrair_codigos` (FIX-004). Medida é campo discriminante (DEC-005), nunca âncora de código.
9. **Assumir que medida é ruído / que a ferramenta é só para pisos** — FALSO: 27 medidas distintas em 80 linhas; a ferramenta atende vários grupos de produto. Medida discrimina e a planilha varia por grupo. → Tratar medida como campo discriminante com penalidade de divergência (DEC-005).
10. **Deduzir a estrutura do repositório a partir do mount** — O mount do Projeto é ACHATADO: não tem subpastas, então `meta/CEREBRO.md` chega como `CEREBRO.md` e `.claude/skills/wrap/SKILL.md` chega como `SKILL__wrap.md`. Deduzir layout daí produz conclusão errada sobre o repo real (já custou uma volta inteira: gerou-se uma "limpeza" de arquivos que já estavam nos lugares certos). → **Ler `_MANIFEST_OAI.md` primeiro**: ele mapeia cada nome plano ao caminho original, traz a raiz em disco e uma foto do Git (último commit, modificados, não rastreados). Nomes com ponto inicial chegam com `_` (`.gitignore` → `_gitignore`).
11. **Carregar a planilha sem forçar texto** — coluna cujos valores são todos numéricos (código interno, código de referência) é inferida `int64` pelo pandas, e `00611` vira `611` **antes** de qualquer `str()` do código. Não dá erro, não avisa — o zero à esquerda só falta no nome final do arquivo ou no match por código (FIX-005). → `carregar_planilha()` em `UTILITÁRIOS/spreadsheet_loader.py` sempre lê com `dtype=str` + `keep_default_na=False`. É o loader único; não reintroduza uma segunda leitura solta em `main.py` ou no harness.
12. **Tratar `UTILITÁRIOS/` como candidato a virar pacote Python** — o nome tem acento (não é identificador Python válido), então `import UTILITÁRIOS.matching_engine` não funciona. → `main.py` faz `sys.path.insert(0, str(Path(__file__).resolve().parent / "UTILITÁRIOS"))` e importa `matching_engine`/`spreadsheet_loader` direto, com `# noqa: E402` nos imports (dependem do `sys.path` da linha acima, não podem subir). Virar pacote de verdade (`core/` + `__init__.py`) é mudança de nome de pasta — decisão do dono, registrada no backlog, não faça sozinho.

## Contexto de Produto
- **Usuário-alvo:** dono/operador de loja de materiais de construção que mantém imagens de produtos e uma planilha-mestre (Google Sheets) com marca, código de referência, descrição, tipo, material, etc.
- **Dor que resolve:** nomear e organizar centenas/milhares de imagens manualmente é inviável; os nomes dos arquivos divergem da planilha (abreviações, sufixos de variação, códigos encurtados).
- **O que é sucesso:** identificar corretamente o máximo de arquivos (meta: ~100% numa pasta bem-feita), renomear pelo padrão `Marca - Código Referência - Descrição`, e permitir agrupar por coluna escolhida — com erro quase zero e total reversibilidade.
- **O que o projeto deliberadamente NÃO é:** não é um gerenciador de pastas profundas/categóricas (o usuário prefere estrutura "flat" por GRUPO de produto + busca/filtro por nome); não cria hierarquia de marca (o nome já ordena por marca); não usa código interno do sistema (não está nos arquivos).
