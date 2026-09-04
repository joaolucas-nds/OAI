# WO 0001 — Registrar fecho da migração KCM no STATUS e a armadilha do mount no CONTEXT

> **Tipo:** WO de DOC (registro).
> **Config sugerida:** Sonnet, esforço baixo — são duas inserções de texto, sem lógica.
> **Pré-requisito:** commit `72f38c5` + migração KCM v1.122.0 já aplicada em disco (meta/ e .claude/ existem).
> **Base:** conversa de 2026-09-03 (fecho da migração KCM v1.122.0) — ver `logs/2026-09-03.md`.
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte** — não chute lugar próximo.
> **Idempotência:** antes de cada inserção, procure a frase-chave do texto NOVO. Se já existir, **PULE** e diga no relatório.
> **Âncoras lidas em:** 2026-09-03, neste turno, com `sed -n` sobre os arquivos do mount:
> - `meta/STATUS.md` linhas 45-46 — li literalmente: `## 💬 Última Sessão` seguido de `**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness.`
> - `meta/CONTEXT.md` linha 95 — li literalmente: `9. **Assumir que medida é ruído / que a ferramenta é só para pisos**` … terminando em `(DEC-005).`, seguido de linha em branco e `## Contexto de Produto`.
> **Próximo comando:** `/wrap`

> **Canal dos meta neste ciclo = CODE.** Esta WO É o registro: aplique os appends e não espere doc do chat.

---

## 1. Por que

O fecho da migração KCM v1.122.0 aconteceu no chat e ainda não está no repositório. Duas lacunas concretas: (a) o `STATUS.md` ainda traz o cabeçalho `Última Sessão` — resíduo vivo da linha revogada REV-3 (par sessão/turno), num arquivo que FICA, então a substituição do CEREBRO não o alcançou; (b) o `CONTEXT.md` não registra a armadilha que custou uma volta inteira nesta conversa: o mount do Projeto é achatado e existe `_MANIFEST_OAI.md` mapeando cada nome plano ao caminho real — ignorá-lo levou a deduzir estrutura errada e a escrever uma limpeza para um problema inexistente.

## 2. Contexto factual

Fatos na ordem em que aconteceram, com origem marcada:

- **[medido por instrumento]** `grep` em `meta/STATUS.md` (2026-09-03): `## 💬 Última Sessão` presente na linha 45 — REV-3 viva.
- **[medido por instrumento]** `grep` em `meta/DECISIONS.md`, `meta/CHANGELOG.md`, `meta/IDEAS.md`: DEC-007 presente, entrada `0.4.1` presente, seção `Feedback para o Kit` presente. Já registrados — **não** repetir.
- **[medido por instrumento]** `head -1 meta/HISTORY.md`: título já corrigido para `# HISTORY.md — Conhecimento Consolidado`. Já resolvido — **não** repetir.
- **[medido por instrumento]** `_MANIFEST_OAI.md` (gerado 2026-09-03 22:30): origem `C:\Users\alexk\Tools\Organizador de Arquivos Inteligente\OAI`; estrutura real inclui `test/golden_set.csv`, `UTILITÁRIOS/matching_engine.py`, `UTILITÁRIOS/test_matching.py`, `meta/README.md`.
- **[medido por instrumento]** `_MANIFEST_OAI.md`, foto do Git na geração: último commit `72f38c5 2026-06-27 first commit`; 10 modificados, 8 não rastreados; 5 arquivos do mount fora do commit (`meta/CEREBRO.md`, `meta/CHANGELOG.md`, `meta/CONTEXT.md`, `meta/DECISIONS.md`, `meta/IDEAS.md`).
- **[relatado pelo dono]** removeu do repo `INSTRUCTION_GUIDE.md`, `PROMPT_IA.md`, `demo.yaml` (artefatos do ASU) — **confirmado [medido]**: ausentes do mount.
- **[relatado pelo dono]** já havia posicionado os arquivos nos caminhos corretos antes desta conversa — **confirmado [medido]** pela tabela do `_MANIFEST_OAI.md`.
- **[relatado pelo dono]** o ASU foi desativado deliberadamente: projeto em modo Code não precisa de ASU.

## Inventário — de onde saiu a lista de edições

Dois pontos, achados por varredura do FATO (não da frase) nos arquivos do mount:

- REV-3 (par sessão/conversa) foi grepada em todos os `meta/*.md` vivos. Ocorrências como **instrução** que sobrevivem em arquivo que fica: **1** (`meta/STATUS.md`, cabeçalho). As demais ocorrências de "sessão" nos meta são **relato histórico** (STATUS corpo, DECISIONS, IDEAS, CHANGELOG) e **ficam** — reescrever relato falsifica o registro.
- Armadilha do mount achatado: **0** ocorrências no `CONTEXT.md` atual (a lista de armadilhas termina em 9). É inserção nova, não correção.

**Total: 2 edições.** Conteste a contagem antes de agir se o seu `grep` divergir.

---

## Edição 1 — `meta/STATUS.md`: corrigir REV-3 e registrar o estado atual

**Localize** (âncora exata, duas linhas consecutivas):

```
## 💬 Última Sessão
**2026-05-31 (2ª sessão)** — Construído o motor v2 modular, o golden set (24 casos reais) e o harness.
```

**Idempotência:** se `## 💬 Última conversa` já existir no arquivo, PULE esta edição.

**Substitua a linha do cabeçalho** `## 💬 Última Sessão` por:

```
## 💬 Última conversa
```

**E, logo abaixo, ANTES do parágrafo que começa com `**2026-05-31 (2ª sessão)**`, insira o parágrafo novo:**

```
**2026-09-03** — Migração para o contrato KCM v1.122.0 concluída e aplicada em disco pelo dono (ver DEC-007). Estrutura passou do layout flat antigo para `meta/` + `.claude/`; `CEREBRO.md` novo em v1.122.0 sem seção ASU; skills `apply-wo` e `wrap` adotadas; `HISTORICO.md` → `meta/HISTORY.md`. As linhas revogadas REV-2/REV-3/REV-4 morreram junto com o CEREBRO/CLAUDE antigos (substituição, não edição); o resíduo de REV-3 que sobrevivia neste arquivo foi corrigido por esta WO. Modo ASU desligado por decisão do dono. **Pendência de repositório [medido em 2026-09-03 22:30, `_MANIFEST_OAI.md`]:** a árvore tinha 10 modificados e 8 não rastreados sobre o commit `72f38c5`, com 5 arquivos de `meta/` fora do commit — confirmar `git add -A && git commit && git push` antes de abrir a próxima conversa. Nenhuma linha de código foi tocada nesta conversa; o backlog de código segue intacto, com a integração do `matching_engine.py` na GUI como item 1.

```

---

## Edição 2 — `meta/CONTEXT.md`: acrescentar a armadilha do mount achatado

**Localize** (âncora exata — fim da armadilha 9, linha em branco, e o cabeçalho seguinte):

```
9. **Assumir que medida é ruído / que a ferramenta é só para pisos** — FALSO: 27 medidas distintas em 80 linhas; a ferramenta atende vários grupos de produto. Medida discrimina e a planilha varia por grupo. → Tratar medida como campo discriminante com penalidade de divergência (DEC-005).

## Contexto de Produto
```

**Idempotência:** se a frase `O mount do Projeto é ACHATADO` já existir no arquivo, PULE esta edição.

**Insira o item 10 entre a armadilha 9 e a linha `## Contexto de Produto`**, preservando a linha em branco antes do cabeçalho:

```
10. **Deduzir a estrutura do repositório a partir do mount** — O mount do Projeto é ACHATADO: não tem subpastas, então `meta/CEREBRO.md` chega como `CEREBRO.md` e `.claude/skills/wrap/SKILL.md` chega como `SKILL__wrap.md`. Deduzir layout daí produz conclusão errada sobre o repo real (já custou uma volta inteira: gerou-se uma "limpeza" de arquivos que já estavam nos lugares certos). → **Ler `_MANIFEST_OAI.md` primeiro**: ele mapeia cada nome plano ao caminho original, traz a raiz em disco e uma foto do Git (último commit, modificados, não rastreados). Nomes com ponto inicial chegam com `_` (`.gitignore` → `_gitignore`).
```

---

## Verificação

Para CADA passo: **quem roda** = o Code, no repo local, na raiz `C:\Users\alexk\Tools\Organizador de Arquivos Inteligente\OAI`; **como chegar no ramo** = `main` (é onde a migração foi aplicada); **o que o passo NÃO responde** está dito em cada item.

1. `findstr /C:"## 💬 Última conversa" meta\STATUS.md` → deve achar 1.
   *Não responde* se o parágrafo novo entrou no lugar certo — só que o cabeçalho mudou. Confira visualmente que o parágrafo de 2026-09-03 está ANTES do de 2026-05-31.
2. `findstr /C:"Última Sessão" meta\STATUS.md` → deve achar **0**.
   *Não responde* nada sobre as ocorrências de "sessão" no corpo (relato histórico) — essas devem continuar existindo.
3. `findstr /C:"O mount do Projeto é ACHATADO" meta\CONTEXT.md` → deve achar 1.
   *Não responde* se a numeração ficou correta; confira que o item é `10.` e que `## Contexto de Produto` continua logo abaixo, separado por linha em branco.
4. `git status` → a árvore deve mostrar `meta/STATUS.md` e `meta/CONTEXT.md` modificados, e nada mais desta WO.
   *Não responde* se os demais 10 modificados/8 não rastreados pré-existentes foram commitados — isso é o passo de fecho, não desta WO.

## Se der VERMELHO

Se qualquer âncora não bater exatamente, **PARE**, não aplique nada, e reporte qual âncora falhou com o trecho que encontrou no lugar. Os arquivos podem ter mudado entre a escrita e a aplicação.

/apply-wo meta/workorders/260903-wo0001-registro-fecho-migracao.md
