# <NOME DO PROJETO> — guia para o Claude Code

> Arquivo-raiz lido pelo Claude Code em todo turno. Mantenha CURTO (< 200 linhas — custa token em todo turno).
> Regra prática: se remover uma linha e o Claude ainda acerta, ela não pertence aqui. Procedural detalhado → vira skill em `.claude/skills/`.
> O comportamento detalhado do assistente está em `meta/CEREBRO.md`.

## Ritual de início
Leia `meta/CEREBRO.md` → o doc de contexto do projeto (ex.: `meta/CONTEXT.md`) → `meta/STATUS.md` antes de agir. Confirme em uma frase o que entendeu.

## Build / validação
- Build: `<seu comando de build, ex.: npm run build>`  (PLACEHOLDER — troque pelo do seu projeto)
- Testes/validação: `<seu comando de teste>` — rode antes de commitar mudança de código.
- Mudança só de doc (meta/) NÃO precisa de build; a rede é o `git diff`.
- Adicione seus comandos de build/teste ao `allow` de `.claude/settings.json`.

## Convenções
- Mensagens de commit **sem acento**.
- Edições nos meta/ são **append-only** pelo Code (STATUS, DECISIONS); curadoria que reescreve vem do chat (arquivo inteiro OU WO).
- Ao aplicar uma WO de `meta/workorders/`: ache cada âncora exatamente; se não achar, PARE e reporte. Não mexa fora das edições nomeadas. `git diff` antes do commit.
- **Ao fechar a tarefa, RELATE o trabalho** — o que fez, achados e desvios do que a tarefa pedia, arquivos tocados, resultado do build/validação e o commit. **Não** copie o bloco de fecho do `meta/CEREBRO.md`: aquele é da raia de planejamento, e trocar relatório por formulário perde o que só você viu.

## Quando eu pedir medição
- Eu leio só o que chega pelo mount; você lê o disco. Se eu pedir para **medir**, o pedido não tem âncora nem commit: não edite nada, não conserte nada, não sugira nada.
- Responda com o **número cru e o comando que o produziu**. Sem interpretação, sem recomendação — se você achar que o número indica um problema, diga o número primeiro e a suspeita depois, separada.
- Se o alvo estiver fora da raiz do repositório, isso depende de `permissions.additionalDirectories` no `.claude/settings.json` (a mesma chave do relatório em arquivo). Se a leitura for negada, DIGA — não estime.

## Push e relatório — nesta ordem, sempre
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add`, `commit` e **`push`, sem perguntar.** Não peça permissão para o que já está decidido.
- **Vermelho** (validação falhou, âncora não encontrada, `git diff` com arquivo fora do previsto) → **não commite e não empurre.** E **não pergunte em prosa** («posso dar push?») — pergunta escrita no meio do texto passa despercebida. Feche com um **menu numerado** de saídas reais, a recomendada em **1** — ex.: `1) corrigir <o quê> e revalidar (recomendado)  2) reverter as edições  3) commitar local, sem push  4) empurrar assim mesmo`.
- **O relatório é o ÚLTIMO passo** — só depois de resolvido o push. Ele diz o que de fato aconteceu: empurrado (com o hash), não empurrado (com o motivo), ou aguardando a escolha do menu. **Relatório escrito antes da decisão conta metade da história** e vira mentira assim que o push sai; se a escolha chegar depois, **reescreva o relatório**, não deixe a versão velha valendo.

## Relatório em arquivo (sempre, sem pedir)
- Ao fechar QUALQUER tarefa (`/apply-wo` ou `/wrap`), grave o MESMO relatório também em `../AAMMDD-HHMM-code-<slug>.txt` — pasta-PAI do repo, fora do versionamento (troque `<slug>` pelo nome curto do projeto; a pasta-pai costuma ser compartilhada por vários repos).
- Exige `permissions.additionalDirectories` no `.claude/settings.json`. Se a escrita for negada, DIGA e siga — o relatório no chat continua sendo a entrega.
- **Para desligar:** apague esta seção. O relatório no chat não muda.

## Config (modelo × esforço)
- WO com diff exato já validado → **Sonnet**, esforço proporcional (mecânico = baixo/médio).
- Tarefa com julgamento sem rede (refator multi-arquivo, WO que delega decisão) → **Opus**, esforço alto.
- Esforço proporcional à ambiguidade; `/effort low` para o trivial.
