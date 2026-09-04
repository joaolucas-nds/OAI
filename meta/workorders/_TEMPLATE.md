# WO NNNN — [titulo curto e concreto, no que a WO ENTREGA]

> **Este arquivo e o MODELO — nao o preencha aqui.** Copie para `meta/workorders/AAMMDD-woNNNN-desc.md`
> e preencha a copia. Ele sobe sempre ao Projeto (o `.flatdropignore` ignora `meta/workorders/*` mas
> reinclui `!meta/workorders/_TEMPLATE.md`), para que a primeira conversa depois de uma transferencia
> tenha o formato a mao sem precisar das WOs antigas.
>
> **O que e uma WO:** instrucao de APLICACAO — ancora + texto exato — que o chat autora e o Code posiciona.
> **O que NAO e:** a spec de feature diz **o que** construir e quando esta pronto; a WO diz **como aplicar**.
> Se voce ainda nao sabe o que construir, nao e hora de escrever WO — e hora de analise ou spec.

---

## Cabecalho — preencha as linhas que se aplicam e apague as que nao

> **Tipo:** WO de CODIGO · WO de DOC (registro) · mista.
> **Config sugerida:** modelo e esforco para quem for aplicar.
> **Pre-requisito:** versao/commit em que esta WO foi escrita, e o estado esperado (testes verdes, arvore limpa).
> **Base:** a decisao, a analise ou a conversa que originou.
> **Depende de:** WOs que precisam estar aplicadas antes — ou apague a linha.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte** — nunca chute um
> lugar proximo. Os arquivos podem ter mudado entre a escrita desta WO e a aplicacao.
> **Idempotencia:** antes de cada insercao, procure a frase-chave do texto NOVO. Se ja existir, **PULE**
> o item e diga no relatorio — nao duplique.
> **Ancoras lidas em:** para CADA edicao, o arquivo e o trecho literal que voce leu NESTE turno para escrever a ancora.
> Campo OBRIGATORIO em WO que edita arquivo existente. **Quem aplica RECUSA a WO se vier vazio** — a conferencia sai de
> quem escreveu (que tem o vies) e vai para quem aplica (que nao tem), que e o mesmo desenho que faz o «PARE e reporte»
> funcionar todas as vezes. O campo pede o TRECHO, nao uma marca de conferido: nao se escreve o trecho sem abrir o arquivo.
> **Afirmacao sobre artefato legivel nao e opiniao, e leitura** — o que uma ferramenta faz, o que um simbolo contem, em que
> estado esta o mount. Nao cite simbolo, caminho ou capacidade de ferramenta que voce nao leu neste turno; declarar «nao li»
> nao autoriza escrever a WO em cima.
> **Numero de checklist e DERIVADO, nunca estimado.** Toda contagem prevista (`grep -c`, quantidade de bullets, de
> arquivos) sai de simular o texto final DESTA WO, incluindo o que ela propria manda inserir — a WO costuma citar as
> frases que insere, na prosa e no checklist, e a contagem ingenua erra por isso. Numero de memoria vira desvio no
> relatorio de quem aplica, que estava certo.
> **Proximo comando:** o comando que o usuario deve rodar quando esta WO fechar em verde — ou apague a linha.
> Ele vai CRU e SOZINHO na ultima linha do relatorio, sem frase de apresentacao: texto em volta esconde o comando.

> **Canal dos meta neste ciclo = CHAT** *(ou **CODE** — escolha um e apague o outro)*.
> Se **CHAT**: esta WO toca so codigo/config — nao faca append nos `meta/`; o chat entrega os
> documentos depois da validacao. Se **CODE**: esta WO E o registro — aplique os appends previstos
> e nao espere doc do chat. *Uma fonte por doc por ciclo; escolher errado aqui duplica conteudo.*

---

## 1. Por que

[Uma a tres frases: a dor concreta, ou a causa raiz se for correcao. Quem aplica precisa saber o que
esta consertando para reconhecer quando o resultado sai errado. Se for correcao de defeito introduzido
por WO anterior, diga qual e assuma — historico honesto e o que impede repetir.]

## 2. Contexto factual *(so em WO de registro — apague em WO de codigo)*

[Os fatos que os textos das edicoes afirmam, na ordem em que aconteceram. Esta secao e a FONTE dos
blocos abaixo: fato que nao esta aqui nao deveria aparecer la. Marque o que foi **medido** e o que e
**deduzido** — inferencia sem rotulo vira fato na leitura seguinte.]

## Inventario — de onde saiu a lista de edicoes *(apague se a WO tem uma edicao so)*

[Quando as edicoes abaixo sao **todos os lugares** que precisam mudar, diga como voce achou esses lugares.
Lista feita de cabeca, ou herdada do texto de quem apontou o problema, ja custou caro: o que ficou de fora
fica invisivel dos dois lados, porque a correcao e a conferencia saem do mesmo inventario incompleto.]

- **Saiu do artefato, nao da memoria.** A pergunta e sempre "que lugares declaram esta grandeza?", feita ao
  codigo. Grepe o **fato**, nao a frase: o mesmo campo aparece com outro nome de variavel, e a mesma regra
  aparece parafraseada. Procure o termo literal, a parafrase, e as listas de pendencia.
- **Nao truncar.** Nada de `head`, nada de "os principais". Inventario paginado e inventario errado, e o
  item que ficou de fora e justamente o que ninguem vai procurar depois.
- **Declare quantos.** Escreva o numero de pontos encontrados — "onze lugares montam este caminho" — para
  que quem aplica possa **contestar a contagem antes de agir**. Ja foi assim que um inventario truncado foi
  pego: a WO dizia onze, o executor achou doze. A contagem e a rede; a proibicao do `head` sozinha nao pega.

---

## Edicao 1 — `caminho/real/do/arquivo.ext` · [o que muda, em cinco palavras]

**Ancora** *(diga ONDE fica: secao, funcao, item — nunca numero de linha)*:

```
[trecho literal e unico do arquivo vivo, copiado sem reformatar]
```

**Substituir por:**

```
[texto exato que entra]
```

> Variantes — use a que couber, sempre com a ancora acima: **Inserir IMEDIATAMENTE APOS** ·
> **Inserir IMEDIATAMENTE ANTES** · **Remover o bloco inteiro** · **Criar arquivo novo** (sem ancora;
> diga o que fazer se ele ja existir).

## Edicao 2 — `caminho/real/do/arquivo.ext` · [...]

[Repita. Uma edicao por bloco. Se um arquivo recebe mudancas distantes entre si, numere 2a/2b/2c em
vez de empilhar num bloco so — cada uma com a propria ancora.]

---

## Fora de escopo

[O que esta WO deliberadamente NAO faz, para que quem aplica nao "aproveite a viagem". Melhoria que
voce enxergou no caminho vira ideia no IDEAS ou outra WO — nao entra aqui.]

## Medicao previa *(so quando houver; nao e edicao)*

[So quando esta WO depender de um numero que a raia de planejamento nao pode ler. Diga O QUE contar e o
comando sugerido; peca de volta o valor e o comando que o produziu, sem interpretacao. Isto NAO tem ancora,
NAO tem commit e NAO muda arquivo — se a medicao contrariar o que a WO assume, PARE antes de editar e relate.]

## Armadilhas desta WO

[So quando houver. O que ja deu errado antes neste mesmo lugar e o que quem aplica pode quebrar sem
perceber: ancora que aparece duas vezes, arquivo com fim de linha CRLF (ancora multi-linha colada com
\\n nao casa), bloco gerado que sera reescrito, numero de check ja usado. Contra o CRLF a saida e
sempre a mesma: ancora de UMA linha nao tem quebra dentro, entao o fim de linha nao morde — para
inserir varias linhas, ancore em UMA so e diga se o texto novo entra antes ou depois dela.]

---

## Depois de aplicar — conferencia antes do commit

- [ ] `git diff` mostra **exatamente** os arquivos previstos, e nada alem.
- [ ] [Conferencia de forma especifica desta WO — ex.: "a entrada nova ficou dentro da secao certa".]
- [ ] **Se algum passo mede um termo com `grep -c`, o numero esperado foi simulado contra o texto FINAL
      de TODAS as edicoes desta WO?** Termo citado por duas edicoes conta 2, nao 1 — e o checklist que
      olha cada edicao isolada produz um VERMELHO falso, que para a aplicacao e gasta um ciclo. Quando um
      termo aparece em mais de uma edicao, declare: «esta frase e citada por duas edicoes; esperado = 2».
      E lembre que `grep -c` conta LINHAS: duas ocorrencias na mesma linha valem 1.
- [ ] **Se a WO declarou um inventario** ("onze lugares"), refaca a contagem no repo. Numero diferente:
      **PARE e reporte antes de editar** — a divergencia e o achado, nao um detalhe a acomodar.
- [ ] **O que esta tarefa criou FORA do repositorio ja foi fechado?** Processo, porta, servidor de
      desenvolvimento, arquivo temporario, download de teste. O que nao deu para fechar entra no
      relatorio **com o caminho** — nao como nota vaga.
- [ ] **WO de codigo:** o comando de validacao do projeto passa com **0 erros**. Se acusar erro,
      **PARE e reporte antes de commitar**.
- [ ] **WO so de doc:** nao precisa de build — a rede e o `git diff`.
- [ ] **Teste manual que a validacao NAO cobre** (obrigatorio quando a WO toca dado carregado ou UI).
      Cada passo de verificacao — nao cada item deste checklist — traz os tres campos abaixo. Passo
      sem os tres nao esta pronto para ser escrito:
      - **Quem roda:** por padrao, **quem aplica**. So vai ao dono o passo que toca **rede de terceiro**
        ou **destroi algo fora do repositorio**; leitura e operacao reversivel na mesma maquina nunca sao
        dele. E quando for dele, o passo chega com o comando exato, o que esperar ver, e o que fazer se
        vier diferente — **nunca peca um resultado que voce nao ensinou a produzir.**
      - **Chega no ramo?** Uma linha nomeando o arquivo e a funcao por onde a execucao passa pelo codigo
        que esta WO mudou. Se voce nao consegue tracar essa linha, o passo nao verifica esta WO: verifica
        que o programa continua rodando. E o unico campo que da trabalho, e e o que separa conferir de
        parecer conferir.
      - **Esta e qual pergunta: «esta la?» ou «presta?»** Contagem, existencia e extensao sao propriedades
        do INVOLUCRO; a aptidao esta no conteudo. Diga qual das duas este passo NAO responde — 45 arquivos
        existindo, com a extensao certa e o indice batendo, ja passaram verdes estando destruidos por dentro,
        porque nenhum instrumento abriu um deles. Fechar a lacuna costuma custar pouco.
      - **Prova de vida:** quando "passou" se parece com "nada aconteceu", o passo precisa do par negativo
        que forca o sinal. Lista vazia so significa alguma coisa depois de voce ter visto a mesma checagem
        devolver um item.
      - **`grep` casa por LINHA.** Se a frase que voce mandou conferir esta quebrada em duas linhas — e o
        proprio texto que a WO insere costuma quebra-la —, o `grep` devolve zero e o passo acusa ausencia
        onde ha presenca. Conferir frase que atravessa linha pede `grep -Pzo`, `rg -U` ou uma ancora curta
        que caiba numa linha so. Vale a regra geral: **ausencia relatada por instrumento e uma afirmacao
        e precisa de prova, igual a qualquer outra** — antes de reportar «nao achei», confirme que o
        instrumento saberia achar.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal da WO · arquivos tocados · resultado da validacao · o commit e o push. Escreva-o DEPOIS de resolver o push: relatorio anterior a decisao conta so parte da historia.
**Nao** substitua este relatorio pelo bloco de fecho do chat: aquele e da raia de planejamento, e trocar
relatorio por formulario perde justamente o que so quem aplicou viu.

## Commit — blocos separados, mensagem SEM acento

**A propria WO entra no `git add`.** Ela e o registro do que foi feito; se cada WO versionar so a anterior, a ultima fica sempre nao rastreada — ja aconteceu tres vezes seguidas. Se ela ja estiver versionada, o `add` nao faz nada e isso NAO e erro.

```
git add [caminhos] [o caminho DESTA WO]
```

```
git commit -m "tipo(escopo): descricao no imperativo curto" -m "Corpo explicando o porque, sem acento."
```

```
git push
```

*Gerado pelo Kit de Contexto Universal v1.122.0 — 2026-09-03 — esta linha e do KIT: nao funda, substitua pela do pacote mais recente.*
