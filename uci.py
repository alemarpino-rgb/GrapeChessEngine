"""
Interfaccia UCI per GrapeChessEngine.

Avvio:   pypy uci.py
Poi la GUI (Cute Chess, Arena, ...) manda i comandi UCI su stdin
e legge le risposte su stdout.

Per usare un'altra versione del motore basta cambiare la riga di import.
"""
import sys
import threading

import chess

import Grape_v080 as motore   # Il motore

NOME = "GrapeChessEngine 0.8.0"
AUTORE = "Alessandro Marpino"
MARGINE = 0.05     # secondi tenuti da parte per la comunicazione con la GUI


def scrivi(testo):
    print(testo, flush=True)

def leggi_posizione(parole):
    # position startpos [moves ...]  oppure  position fen <FEN> [moves ...]
    if "moves" in parole:
        i = parole.index("moves")
        mosse = parole[i + 1:]
        parole = parole[:i]
    else:
        mosse = []

    if parole[1] == "startpos":
        board = chess.Board()
    else:                                   # "fen"
        board = chess.Board(" ".join(parole[2:]))

    for m in mosse:
        board.push_uci(m)
    return board


# =====================================
# TEMPO
# =====================================
def leggi_go(parole, board):
    #Trasforma il comando go in (secondi, profondità massima)
    valori = {}
    for chiave in ("wtime", "btime", "winc", "binc", "movestogo", "movetime", "depth"):
        if chiave in parole:
            valori[chiave] = int(parole[parole.index(chiave) + 1])

    if "infinite" in parole:
        # pensa finché non arriva "stop"
        return None, 64 
    if "depth" in valori:
        # profondità fissa, senza limite di tempo
        return None, valori["depth"]
    if "movetime" in valori:
        return max(valori["movetime"] / 1000 - MARGINE, 0.01), 64

    bianco = board.turn == chess.WHITE
    mio = valori.get("wtime" if bianco else "btime")
    inc = valori.get("winc" if bianco else "binc", 0)
    if mio is None:
        # nessuna informazione: 1 secondo
        return 1.0, 64                    
    mio, inc = mio / 1000, inc / 1000

    mosse_rimaste = valori.get("movestogo", 30)
    secondi = mio / mosse_rimaste + inc * 0.8
    # mai più di metà del tempo rimasto
    secondi = min(secondi, mio * 0.5)        
    return max(secondi - MARGINE, 0.01), 64

# PUNTEGGIO

def formato_punteggio(punteggio, prof):
    # Punteggio di GrapeChessEngine : 'cp X' oppure 'mate N' per la GUI
    if abs(punteggio) >= motore.MATTO:
        rimasta = abs(punteggio) - motore.MATTO
        semimosse = prof - rimasta
        mosse = (semimosse + 1) // 2
        return f"mate {mosse if punteggio > 0 else -mosse}"
    return f"cp {punteggio}"


def pensa(board, secondi, prof_max):
    # E' praticamente la mossa dl motore con tutte le info stampate e in modo che possa venirebloccato
    info = motore.cerca_iterativa(board, secondi, prof_max=prof_max)

    for l in info["livelli"]:
        mossa_uci = board.parse_san(l["mossa"]).uci()
        ms = int(l["tempo"] * 1000)
        nps = int(l["nodi"] / l["tempo"]) if l["tempo"] > 0 else 0

        scrivi(
            f"info depth {l['prof']} score {formato_punteggio(l['punteggio'], l['prof'])} "
            f"nodes {l['nodi']} time {ms} nps {nps} pv {mossa_uci}"
        )

    mossa = info["mossa"]
    if mossa is None:
        # Se per qualche motivo non trova nessuna mossa, ne sceglie una legale a caso
        mossa = next(iter(board.legal_moves), None)
    scrivi(f"bestmove {mossa.uci() if mossa else '0000'}")


def ferma(ricerca):
    # Interrompe la ricerca :(
    if ricerca is not None and ricerca.is_alive():
        motore.SCADENZA = 0
        ricerca.join()

def main():
    board = chess.Board()
    ricerca = None

    for riga in sys.stdin:
        parole = riga.split()
        # vede i comandi e li divide in una lista e la analizza
        if not parole:
            continue
        comando = parole[0]

        if comando == "uci":
            scrivi(f"id name {NOME}")
            scrivi(f"id author {AUTORE}")
            scrivi("uciok")

        elif comando == "isready":
            scrivi("readyok")

        elif comando == "ucinewgame":
            ferma(ricerca)
            motore.TT.clear()

        elif comando == "position":
            ferma(ricerca)
            board = leggi_posizione(parole)

        elif comando == "go":
            ferma(ricerca)
            secondi, prof_max = leggi_go(parole, board)
            ricerca = threading.Thread(target=pensa, args=(board.copy(), secondi, prof_max))
            ricerca.start()

        elif comando == "stop":
            ferma(ricerca)

        elif comando == "quit":
            ferma(ricerca)
            break


if __name__ == "__main__":
    main()