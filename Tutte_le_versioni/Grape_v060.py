import chess
import random
import chess.pgn
import time

# =====================================
# TUTTI I VALORI
# =====================================

VALORI = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 320,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}
PEDONE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

CAVALLO = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]

ALFIERE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20,
]

TORRE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

DONNA = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20,
]

RE_MEDIOGIOCO = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]

RE_FINALE = [
   -50,-40,-30,-20,-20,-30,-40,-50,
   -30,-20,-10,  0,  0,-10,-20,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-30,  0,  0,  0,  0,-30,-30,
   -50,-30,-30,-30,-30,-30,-30,-50,
]

TABELLE = {
    chess.PAWN: PEDONE, 
    chess.KNIGHT: CAVALLO, 
    chess.BISHOP: ALFIERE,
    chess.ROOK: TORRE, 
    chess.QUEEN: DONNA,
}

# PST[colore][tipo][casa] = valore del pezzo + bonus della casa (già specchiato)
PST = {chess.WHITE: {}, chess.BLACK: {}}
for tipo, tab in TABELLE.items():
    # Quindi sarebbe PST{ chess.WHITE{ chess.PAWN : +90 } }
    PST[chess.WHITE][tipo] = [VALORI[tipo] + tab[chess.square_mirror(c)] for c in chess.SQUARES]
    PST[chess.BLACK][tipo] = [VALORI[tipo] + tab[c] for c in chess.SQUARES]

# re: una tabella per fase e per colore
RE_PST = {}
for fase, tab in (("medio", RE_MEDIOGIOCO), ("finale", RE_FINALE)):
    RE_PST[fase, chess.WHITE] = [tab[chess.square_mirror(c)] for c in chess.SQUARES]
    RE_PST[fase, chess.BLACK] = [tab[c] for c in chess.SQUARES]

NODI = 0
SCADENZA = 0.0

# Serve a dire quando il tempo è scaduto
class Tempo_scaduto(Exception):
    pass

# =====================================
# FINE DI TUTTI I VALORI
# =====================================

def controlla_tempo():
    # time.time() costa: lo chiamiamo solo ogni 1024 nodi
    if NODI % 1024 == 0 and time.time() > SCADENZA:
        raise Tempo_scaduto

# Vede il punteggio delle mosse più 'attraenti' così l'alpha-beta deve fare meno lavoro

def punteggio_ordine(board, mossa):
    # più alto = provata prima
    punteggio = 0
    if mossa.promotion:
        punteggio += 20000 + VALORI[mossa.promotion]
    if board.is_capture(mossa):
        punteggio += 10000 + priorita(board, mossa)
    return punteggio

# E poi vengono ordinate

def ordina(board, mosse):
    return sorted(mosse, key=lambda m: punteggio_ordine(board, m), reverse=True)

def priorita(board, mossa):
    catturato = pezzo_catturato(board, mossa)
    attaccante = board.piece_type_at(mossa.from_square)
    return 10 * VALORI[catturato.piece_type] - VALORI[attaccante]

def quiescenza(board, alfa, beta):
    global NODI
    NODI+=1
    controlla_tempo()
    fermo = valuta_posizione(board, board.turn)
    if fermo >= beta:
        return beta
    alfa = max(alfa, fermo)
    catture = sorted(board.generate_legal_captures(),
                     key=lambda m: priorita(board, m), reverse=True)
    for mossa in catture:
        board.push(mossa)
        p = -quiescenza(board, -beta, -alfa)
        board.pop()
        if p >= beta:
            return beta
        alfa = max(alfa, p)
    return alfa

INF = 10**9  # Infinito: equivale a 10^9
MATTO = 100000

def negamax(board, profondita, alfa, beta):
    global NODI
    NODI += 1
    controlla_tempo()

    # patte: controlli solo quando possono essere vere
    if board.halfmove_clock >= 4 and board.is_repetition(2):
        return 0
    if board.halfmove_clock >= 100:          # regola delle 50 mosse
        return 0
    if chess.popcount(board.occupied) <= 4 and board.is_insufficient_material():
        return 0

    # mosse generate UNA volta: servono sia per matto/stallo sia per il for
    mosse = list(board.legal_moves)
    if not mosse:
        return (-MATTO - profondita) if board.is_check() else 0

    if profondita == 0:
        return quiescenza(board, alfa, beta)

    for mossa in ordina(board, mosse):
        board.push(mossa)
        punteggio = -negamax(board, profondita - 1, -beta, -alfa)
        board.pop()
        if punteggio >= beta:
            return beta                # taglio: l'avversario non ci lascerà arrivare qui
        alfa = max(alfa, punteggio)
    return alfa

def cerca_iterativa(board, secondi, prof_max=64):
    global SCADENZA
    inizio = time.time()
    SCADENZA = inizio + secondi

    b = board.copy() # se il tempo scade, b resta "sporca": non importa
    mosse = list(b.legal_moves)
    if len(mosse) == 1:
        return mosse[0] # mossa obbligata: inutile pensare
    random.shuffle(mosse) # si da veriabilità alle mosse
    mosse = ordina(b, mosse)
    migliore = mosse[0]

    for prof in range(1, prof_max + 1):
        # prova ad assegnare la mossa migliore a meno che il tempo non scada
        try:
            m, punteggio = cerca(b, prof, mosse) # m = migliore, punteggio = alfa
        except Tempo_scaduto:
            break # profondità incompleta: si tiene la precedente
        migliore = m
        print(f"  prof {prof}: {b.san(m)} ({punteggio}) dopo {time.time() - inizio:.2f}s")

        mosse.remove(m)                    # la migliore in testa per il giro dopo
        mosse.insert(0, m)

        if abs(punteggio) >= MATTO:        # trovato un matto: più a fondo non serve
            break
        if time.time() - inizio > secondi * 0.5:
            break                          # il prossimo livello non farebbe in tempo
    return migliore

def cerca(board, profondita, mosse):
    migliore, alfa = None, -INF
    for mossa in mosse:
        board.push(mossa)
        p = -negamax(board, profondita - 1, -INF, -alfa)
        board.pop()
        if p > alfa:
            alfa, migliore = p, mossa
    return migliore, alfa # Ora ritorna anche alfa in modo che il processo possa venire interrotto sempre

def pezzo_catturato(board, mossa):
    if not board.is_capture(mossa):
        return None
    if board.is_en_passant(mossa):
        casa = chess.square(chess.square_file(mossa.to_square), # vede la fila della casella e la riga della casella
                            chess.square_rank(mossa.from_square))
        return board.piece_at(casa)
    return board.piece_at(mossa.to_square)

def is_finale(board):
    pc = chess.popcount
    pezzi = pc(board.knights) * 300 + pc(board.bishops) * 320 + pc(board.rooks) * 500
    return board.queens == 0 or pezzi <= 1300

def valuta_posizione(board, colore):
    fase = "finale" if is_finale(board) else "medio"
    totale = 0
    # c = chess.WHITE
    for c in (chess.WHITE, chess.BLACK):
        miei = board.occupied_co[c]
        s = 0
        # tipo = chess.PAWN, bb = board.pawns
        for tipo, bb in ((chess.PAWN, board.pawns), (chess.KNIGHT, board.knights),
                         (chess.BISHOP, board.bishops), (chess.ROOK, board.rooks),
                         (chess.QUEEN, board.queens)):
            # tab = PST[chess.WHITE][chess.PAWN]
            tab = PST[c][tipo]
            for casa in chess.scan_forward(bb & miei):
                s += tab[casa]
        s += RE_PST[fase, c][board.king(c)]
        # se si è bianchi, aggiunge, sennò toglie
        totale += s if c == colore else -s
    return totale

def materiale(board, colore):
    # vede il vantaggio materiale
    totale = 0
    for tipo, valore in VALORI.items():
        totale += len(board.pieces(tipo, colore)) * valore
        totale -= len(board.pieces(tipo, not colore)) * valore
    return totale

n_mosse=0
nodi_s_media=0

def mossa_motore(board, secondi):
    mosse = list(board.legal_moves)
    random.shuffle(mosse)        # varietà tra mosse con lo stesso punteggio
    global NODI
    NODI = 0
    t = time.time()
    migliore = cerca_iterativa(board, secondi)
    dt = time.time() - t
    print(f"{NODI} nodi in {dt:.2f}s ({NODI/dt:.0f} nodi/s)")
    global n_mosse
    global nodi_s_media
    n_mosse+=1
    nodi_s_media+=NODI/dt
    media_calcolata=int(nodi_s_media//n_mosse)
    print(f"Media nodi/s: {media_calcolata}")
    print("Il motore gioca:", board.san(migliore))
    return board.push(migliore)

def gioca(board, tempo, colore_motore=chess.BLACK):
    print(board)
    secondi=10
    while not board.is_game_over(claim_draw=True):
        if board.turn == colore_motore:
            secondi=tempo/30
            inizio=time.time()
            mossa_motore(board, secondi)
            fine=time.time()
            tempo=tempo-(fine-inizio)
            minuti, secondi_rest = divmod(tempo, 60)
            print(f"Tempo per il motore: {int(minuti)}min {secondi_rest:.1f}s")
        else:
            testo = input("La tua mossa: ")
            try:
                board.push_san(testo)
            except ValueError:
                print("Mossa non valida, riprova")
                continue         # il turno NON passa
        print(board)
    print("Risultato:", board.result(claim_draw=True))

def gioca_solo(board, tempo):
    print(board)
    secondi=10
    while not board.is_game_over(claim_draw=True):
        secondi=tempo/30
        inizio=time.time()
        mossa_motore(board, secondi)
        fine=time.time()
        tempo=tempo-(fine-inizio)   
        minuti, secondi_rest = divmod(tempo, 60)
        print(f"Tempo per il motore: {int(minuti)}min {secondi_rest:.1f}s")
        print(board)
    print("Risultato:", board.result(claim_draw=True))
    
    partita = chess.pgn.Game.from_board(board)
    print(partita)

if __name__=='__main__':
    tempo=0
    tempo=input("tempo? ")
    while True:
        try:
            tempo_int=int(tempo)
            break

        except ValueError:
            print("Valore sbagliato!")

    board=chess.Board()
    gioca_solo(board, tempo_int)
