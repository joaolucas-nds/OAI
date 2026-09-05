# ROADMAP.md — Plano Intencional de Evolução

> **Opcional.** Use quando o projeto tem um plano em fases — não para tarefas soltas (isso é o Backlog do STATUS) nem para brainstorm (isso é o IDEAS).
> Cada fase tem um objetivo e um critério de conclusão. Marque o estado: 🟢 concluída · 🟡 em curso/próxima · 🔵 futura · 🚫 descartada.
> Médio e longo prazo vivem AQUI, não no STATUS.

---

## 🟢 F1 — Protótipo funcional *(concluída)*
**Objetivo:** provar o conceito — ler planilha, varrer pasta, casar por código+fuzzy, renomear/copiar/mover com preview e log.
**Critério de conclusão:** versão que organiza uma pasta real de ponta a ponta sem travar.
- Entregue: motor hierárquico, GUI em abas, 5 ações, log+desfazer, sufixos configuráveis, persistência. Bugs de código/layout corrigidos (0.3.1).

## 🟡 F2 — Motor de matching v2 (confiável e testável) *(próxima)*
**Objetivo:** acabar com a inflação de score e tornar o acerto medível e confiável.
**Critério de conclusão:** golden set rodando com % de acerto reportado; nota alta passa a significar semelhança real; zero regressão vs. casos já corretos.
- [x] Separar `matching_engine` (puro Python, sem PySide6) da GUI. *(0.4.0)*
- [x] Substituir `token_set_ratio` por score ponderado (token_sort + WRatio + cobertura + medida discriminante) — DEC-002. *(0.4.0)*
- [x] Criar golden set inicial (24 casos críticos) + harness que reporta % de acerto. *(0.4.0)*  → expandir para a pasta completa segue pendente.
- [x] Score com transparência: motor devolve componentes/código casado/ambiguidade. *(0.4.0, falta exibir na UI)*
- [x] **Integrar o motor v2 na GUI** (trocar o `MotorMatching` embutido pela importação do módulo). *(0.4.3, WO 0005)*
- [x] Exibir transparência na tabela (componentes, código casado, alerta de ambiguidade). *(0.4.4, WO 0006, DEC-009 — coluna "Por quê" + tooltip + alerta âmbar; detecção de ambiguidade fim-a-fim ainda sem instrumento)*
- [ ] Expandir o golden set (pasta real completa de 164 pisos + louças).
- [ ] Dois thresholds separados: exibição × seleção.
- [ ] Tornar `PesosScore` editável e persistível na aba Configurações.

## 🔵 F3 — Configuração avançada e usabilidade *(futuro, sem data)*
**Objetivo:** mais liberdade e praticidade sem virar bagunça.
- Dicionário de sinônimos/abreviações configurável (RETAN→RETANGULAR…).
- Modo "encadear ações" numa passada (renomear→copiar→mover) atendendo duplicação controlada.
- Alerta visual de ambiguidade (dois matches próximos → decisão manual).
- Perfis de configuração salvos por tipo de planilha (pisos, louças…).
- Regras compostas de sufixo (ex: `(A)v2`).

## 🔵 F4 — Robustez e escala *(futuro, sem data)*
**Objetivo:** aguentar volume grande e múltiplas planilhas com confiança.
- Evolução do scoring para TF-IDF + cosseno (catálogos grandes).
- Suporte a múltiplas planilhas/colunas heterogêneas com mapeamento salvo.
- Empacotamento .exe otimizado (tamanho/inicialização).
- Possível "ID interno" via sidecar para agrupar arquivos de um mesmo produto.

---

## 🚫 Itens descartados desta visão
- **Hierarquia de pastas por marca** — fora de escopo; o nome já ordena por marca. (Vive em IDEAS/Descartadas.)
- **Atalhos `.lnk` em vez de cópia** — incompatível com o fluxo (arquivos abertos em outros programas).
