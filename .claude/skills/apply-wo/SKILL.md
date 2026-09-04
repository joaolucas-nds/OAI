---
name: apply-wo
description: Aplica uma WO de meta/workorders/ ao repo — localiza cada âncora exatamente, substitui, e para se não achar. Use quando o usuário pedir /apply-wo ou para aplicar uma WO nomeada.
disable-model-invocation: true
---
Leia o arquivo de WO indicado em `meta/workorders/` e execute-o.
ANTES de editar: se a WO edita arquivo existente e o cabeçalho dela NÃO traz o campo «Âncoras lidas em» preenchido, RECUSE — não aplique, e diga que falta. Quem escreveu a WO é quem tem o viés; esta conferência é sua justamente por isso.
Localize cada âncora EXATAMENTE; se não achar uma, PARE e reporte — não chute um lugar próximo.
Não toque em nada fora das edições nomeadas. Ao fim, rode `git diff` e confira a forma esperada antes de commitar.
Ao terminar, RELATE: o que foi feito, achados/desvios do texto da WO, arquivos tocados, build/validação e o commit.
Resolva o push ANTES de escrever o relatorio, e escreva o campo do push com o RESULTADO REAL — nunca «pendente» por antecipacao. Se ele ficar mesmo pendente, REABRA o relatorio e corrija quando resolver: o arquivo que afirma o falso e o que a proxima sessao le. Confira tambem que nenhum relatorio `.txt` ficou DENTRO do repo (`git status` o mostraria como nao rastreado): o lugar dele e a pasta-pai, e relatorio na raiz vira `??` que ninguem identifica. Verde: `add`, `commit` e `push` sem perguntar — e, se a WO declarar um **Proximo comando**, termine o relatorio com ele CRU e SOZINHO na ultima linha, sem frase de apresentacao (texto em volta esconde o comando). Vermelho: nao commite nem empurre — feche com MENU DE OPCOES pela ferramenta `AskUserQuestion`, com a recomendada em primeiro lugar e marcada `(Recomendado)`. **Nunca pergunte em prosa — e menu numerado escrito no corpo da mensagem TAMBEM e prosa**, porque obriga o dono a digitar a resposta em vez de clicar. Sem a ferramenta, caia no menu numerado em texto e DIGA que caiu no fallback. **O cartao serve para ESCOLHER, nao para DISPARAR:** ele nao contorna `disable-model-invocation`, entao nao o use para oferecer «rodar a skill agora» — medido duas vezes, isso acrescenta um passo sem tirar nenhum. Resolva o push ANTES de escrever o relatorio. Grave o MESMO relatório em `../AAMMDD-HHMM-code-<slug>.txt` (pasta-pai do repo). Se a escrita for negada, diga e siga.
WO: $ARGUMENTS


*Gerado pelo Kit de Contexto Universal v1.122.0 — 2026-09-03 — esta linha e do KIT: nao funda, substitua pela do pacote mais recente.*
