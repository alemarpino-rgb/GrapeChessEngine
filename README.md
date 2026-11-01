# GrapeChessEngine

**A small UCI chess engine written in Python**, built step by step on top of [python-chess](https://python-chess.readthedocs.io/).
Made by [Alessandro Marpino](https://github.com/alemarpino-rgb). License: MIT. The Windows build includes PyPy and python-chess (see their licenses in [the licenses folder](https://github.com/alemarpino-rgb/GrapeChessEngine/tree/main/licenses)).

## English summary

- **Search:** negamax with alpha-beta, quiescence search, iterative deepening with time management, transposition table, MVV-LVA move ordering (TT move first), cheap draw detection.
- **Evaluation:** material + piece-square tables (precomputed, read from bitboards), tapered king evaluation (smooth blend between middlegame and endgame tables based on the material left).
- **Speed:** around 100k nodes/s with PyPy.
- **Protocol:** UCI, works in Arena, Cute Chess and other GUIs.
- **Play it on Lichess:** [GrapeChessEngine](https://lichess.org/@/GrapeChessEngine) (around 1450–1500 in bot blitz).

**Windows:** download the zip from the [Releases](https://github.com/alemarpino-rgb/GrapeChessEngine/releases), unzip it and load `GrapeChessEngine.exe` as a UCI engine in your GUI. Python is not needed: a portable PyPy is included.

**From source:** install [PyPy](https://pypy.org/) and python-chess (`pypy3 -m pip install chess`), then run `pypy uci.py`.

Feedback, bug reports and test games are very welcome!

---

## Cos'è

GrapeChessEngine è un motore scacchistico in Python. È la continuazione di [klak](https://github.com/Spunc595/Klak/tree/main/alessandro), un motore sempre scritto da me: la storia delle versioni prima della 0.7.0 è lì. Tutte le versioni del motore sono nella cartella [Tutte_le_versioni](https://github.com/alemarpino-rgb/GrapeChessEngine/tree/main/Tutte_le_versioni). Usa python-chess e PyPy (le loro licenze sono [nella cartella licenses](https://github.com/alemarpino-rgb/GrapeChessEngine/tree/main/licenses)).

## Come funziona

**Ricerca**
- **Negamax con potatura alfa-beta**: esplora l'albero delle mosse e scarta i rami che l'avversario non permetterebbe mai.
- **Approfondimento iterativo con limite di tempo**: cerca a profondità 1, 2, 3… finché non scade il tempo della mossa, poi gioca la migliore mossa dell'ultima profondità completata. Si ferma subito se trova un matto o se la mossa è obbligata.
- **Tabella di trasposizione**: ricorda le posizioni già analizzate (profondità, punteggio, tipo di punteggio e mossa migliore). Le posizioni ritrovate non si ricalcolano, e la mossa migliore salvata viene provata per prima.
- **Ricerca di quiescenza**: alla fine della ricerca principale continua a esaminare le catture, per non fermarsi a metà di uno scambio.
- **Ordinamento delle mosse**: prima la mossa della tabella di trasposizione, poi promozioni e catture (MVV-LVA: la vittima più preziosa presa dall'attaccante meno prezioso).
- **Controlli di patta economici**: matto e stallo ricavati dalla stessa lista di mosse; ripetizioni, regola delle 50 mosse e materiale insufficiente controllati solo quando possono essere veri.
- **Varietà**: tra mosse con lo stesso punteggio ne sceglie una a caso.

**Valutazione**
- Materiale: P=100, C=300, A=320, T=500, D=900.
- **Piece-square tables**: un bonus o malus per ogni pezzo in base alla casa che occupa.
- **Tabelle precalcolate e bitboard**: valore del pezzo e bonus della casa sono già sommati all'avvio, e durante la ricerca i pezzi si leggono direttamente dai bitboard.
- **Fase di gioco graduale per il re**: la fase va da 24 (tutti i pezzi) a 0 (solo re e pedoni), contando cavallo e alfiere 1, torre 2, donna 4. Il valore del re è una media pesata tra la tabella di mediogioco (al riparo) e quella di finale (al centro), così il re si attiva solo man mano che spariscono i pezzi.

## Uso

### Versione per Windows (consigliata)

1. Scarica lo zip dalle [Release](https://github.com/alemarpino-rgb/GrapeChessEngine/releases) e scompattalo.
2. Nella tua interfaccia (Arena, Cute Chess, …) aggiungi un nuovo motore, scegli `GrapeChessEngine.exe` e il protocollo **UCI**.

Non serve installare niente: nella cartella c'è già una copia portatile di PyPy con python-chess.

```
GrapeChessEngine/
  GrapeChessEngine.exe   avvia il motore
  uci.py                 interfaccia UCI
  Grape_v080.py          il motore
  pypy/                  PyPy portatile
  licenses/              licenze di PyPy, python-chess e GrapeChessEngine
```

### Dal codice sorgente

Serve Python 3 (consigliato **[PyPy](https://pypy.org/)**, molto più veloce per questo tipo di codice) e python-chess:

```bash
pypy3 -m ensurepip
pypy3 -m pip install chess
```

- **Come motore UCI:** `pypy uci.py`. In Cute Chess puoi usare come comando `pypy` e come argomento `uci.py`.
- **Per giocarci contro nel terminale:** `pypy Grape_v080.py`. Il programma chiede il tempo totale in secondi per il motore, che gioca col nero; le tue mosse si scrivono in notazione SAN (`e4`, `Nf3`, `O-O`…).

## Prestazioni

Con PyPy su un PC desktop, circa **100.000 nodi/s**.

| Novità | Risultato |
|---|---|
| Valutazione precalcolata + bitboard | stessa ricerca **1,6 volte più veloce** |
| Approfondimento iterativo | tempo per mossa sotto controllo (massimo 2,04 s su un limite di 2 s) |
| Tabella di trasposizione | profondità media in 3 s sulle posizioni di prova **da 4,67 a 5,83**; nei finali di pedoni da 8 a 12 |
| Fase di gioco graduale (0.8.0) | match contro la 0.7.0: **35,5 / 58 (61%)**, circa +80 Elo |

Su Lichess gioca come [GrapeChessEngine](https://lichess.org/@/GrapeChessEngine), intorno a **1450–1500** nel blitz tra bot.

**Punti deboli noti:** la valutazione non sa ancora niente di struttura pedonale, sicurezza del re e pedoni passati.

## Novità

**0.8.0**
- Fase di gioco graduale: il re non va più al centro appena si cambiano le donne

**0.7.0**
- Tabella di trasposizione
- Interfaccia UCI ed eseguibile per Windows

**0.6.0** (come klak)
- Approfondimento iterativo con limite di tempo e gestione del tempo

**0.5.0** (come klak)
- Valutazione con tabelle precalcolate e bitboard

## Prossimi passi

- [x] Valutazione più veloce con tabelle precalcolate e bitboard
- [x] Approfondimento iterativo con limite di tempo
- [x] Tabella di trasposizione
- [x] Interfaccia UCI ed eseguibile per Windows
- [x] Fase di gioco graduale (re al centro troppo presto)
- [ ] Estensione di scacco
- [ ] Killer moves e history heuristic
- [ ] Null move pruning e late move reductions
- [ ] Valutazione più ricca: pedoni passati, struttura pedonale, sicurezza del re
- [ ] Match regolari contro altri motori per misurare l'Elo

## Crediti

- [python-chess](https://github.com/niklasf/python-chess) di Niklas Fiekas: generazione delle mosse e rappresentazione della scacchiera (GPL-3.0)
- [PyPy](https://pypy.org/): l'interprete Python veloce incluso nella versione per Windows (MIT)

## L'autore

L'autore di questo motore è Alessandro Marpino (io ;) ). Ho anche fatto altri progetti come [GrapeScript](https://github.com/alemarpino-rgb/GrapeScript), un intero linguaggio di programmazione!

## Licenza

[MIT](LICENSE)