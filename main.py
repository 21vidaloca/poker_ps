import random
import math
import matplotlib.pyplot as plt
import itertools
from collections import Counter

# ==========================================
# 1. STRUCTURI DE DATE SI LOGICA (POKER ENGINE)
# ==========================================

# Folosim notatia standard internationala pentru input (e mai sigur), 
# dar afisam in romana si cu simboluri.
# s=Spades(Pica), h=Hearts(Inima), d=Diamonds(Romb), c=Clubs(Trefla)
SUITS = 'shdc'
RANKS = '23456789TJQKA'
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}

# Dictionar pentru afisare frumoasa in consola
PRETTY_SUITS = {
    's': '♠', # Pica
    'h': '♥', # Inima
    'd': '♦', # Romb
    'c': '♣'  # Trefla
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __repr__(self):
        # Cand printam cartea, apare simbolul (ex: A♥)
        return f"{self.rank}{PRETTY_SUITS[self.suit]}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash(self.rank + self.suit)

def create_deck():
    """Creeaza un pachet complet de 52 de carti."""
    return [Card(r, s) for s in SUITS for r in RANKS]

def parse_hand(hand_str):
    """
    Transforma textul utilizatorului (ex: 'Ah Kh') in obiecte Card.
    """
    cards = []
    if not hand_str: return []
    
    # Curatam spatiile si virgulele
    clean_str = hand_str.replace(" ", "").replace(",", "")
    
    # Citim cate 2 caractere
    for i in range(0, len(clean_str), 2):
        if i+1 < len(clean_str):
            r = clean_str[i]
            s = clean_str[i+1].lower() # acceptam si litere mari la culori
            if r in RANKS and s in SUITS:
                cards.append(Card(r, s))
            else:
                print(f"⚠️ Avertisment: Cartea '{r}{s}' nu este valida si a fost ignorata.")
    return cards

def get_rank_5(cards):
    """
    Evalueaza scorul unei maini de exact 5 carti.
    Returneaza: (Categorie, [Lista Kicker-i])
    """
    # Sortam descrescator dupa valoare
    cards.sort(key=lambda c: c.value, reverse=True)
    values = [c.value for c in cards]
    suits = [c.suit for c in cards]
    
    is_flush = len(set(suits)) == 1
    
    # Verificare Chinta (Straight)
    is_straight = False
    if len(set(values)) == 5:
        if values[0] - values[4] == 4:
            is_straight = True
        # Cazul special A-2-3-4-5 (Chinta mica / Roata)
        if values == [14, 5, 4, 3, 2]:
            is_straight = True
            values = [5, 4, 3, 2, 1] 
            
    counts = Counter(values)
    counts_vals = counts.most_common() 
    
    # Ierarhia Poker (8=Chinta Roiala/Culoare, ..., 0=Carte Mare)
    if is_straight and is_flush:
        return (8, values)
    if counts_vals[0][1] == 4: # Careu
        return (7, [counts_vals[0][0], counts_vals[1][0]])
    if counts_vals[0][1] == 3 and counts_vals[1][1] == 2: # Full House
        return (6, [counts_vals[0][0], counts_vals[1][0]])
    if is_flush: # Culoare
        return (5, values)
    if is_straight: # Chinta
        return (4, values)
    if counts_vals[0][1] == 3: # Trei de un fel
        kickers = [c[0] for c in counts_vals[1:]]
        return (3, [counts_vals[0][0]] + kickers)
    if counts_vals[0][1] == 2 and counts_vals[1][1] == 2: # Doua Perechi
        kicker = counts_vals[2][0]
        return (2, [counts_vals[0][0], counts_vals[1][0], kicker])
    if counts_vals[0][1] == 2: # O Pereche
        kickers = [c[0] for c in counts_vals[1:]]
        return (1, [counts_vals[0][0]] + kickers)
    
    return (0, values) # Carte Mare

def evaluate_hand(cards):
    """Gaseste cea mai buna combinatie de 5 carti din totalul disponibil."""
    if len(cards) < 5: return (-1, [])
    best_score = (-1, [])
    # itertools.combinations genereaza toate variantele posibile de 5 carti
    for hand_5 in itertools.combinations(cards, 5):
        score = get_rank_5(list(hand_5))
        if score > best_score:
            best_score = score
    return best_score

# ==========================================
# 2. MOTORUL DE SIMULARE (MONTE CARLO)
# ==========================================

def run_simulation(hero_str, villain_str=None, board_str=None, n_sims=5000):
    """
    Ruleaza simularea Monte Carlo.
    Returneaza: (Equity Final, Istoric Evolutie)
    """
    hero_hand = parse_hand(hero_str)
    
    # Verificare input
    if len(hero_hand) != 2:
        print("Eroare: Trebuie sa introduci exact 2 carti pentru tine.")
        return 0, []

    # Parsam board-ul cunoscut (daca exista)
    known_board = []
    if board_str:
        known_board = parse_hand(board_str)
        
    full_deck = create_deck()
    
    # Scoatem din pachet tot ce e vizibil (Cartile mele + Ce e pe masa)
    visible_cards = hero_hand + known_board
    base_deck = [c for c in full_deck if c not in visible_cards]
    
    wins = 0
    history = []
    
    # Pregatim adversarul specific (daca exista)
    villain_specific = parse_hand(villain_str) if villain_str else None
    
    # Cate carti comune mai trebuie trase? (5 minus cate sunt deja jos)
    cards_needed = 5 - len(known_board)
    
    for i in range(1, n_sims + 1):
        # Amestecam pachetul ramas
        current_deck = base_deck[:]
        random.shuffle(current_deck)
        
        if villain_specific:
            # CAZ 1: Stim ce are adversarul
            v_hand = villain_specific
            # Adversarul nu poate avea carti care sunt deja in pachetul nostru simulat
            # Deci tragem board-ul din restul cartilor
            deck_for_board = [c for c in current_deck if c not in v_hand]
            drawn_board = deck_for_board[:cards_needed]
        else:
            # CAZ 2: Adversar Aleatoriu (Random Range)
            # Tragem 2 carti pentru adversar
            v_hand = current_deck[:2]
            # Tragem restul de carti pentru masa
            drawn_board = current_deck[2 : 2 + cards_needed]
            
        # Compunem masa completa
        full_board = known_board + drawn_board
        
        # Evaluam cine castiga
        score_hero = evaluate_hand(hero_hand + full_board)
        score_villain = evaluate_hand(v_hand + full_board)
        
        if score_hero > score_villain:
            wins += 1
        elif score_hero == score_villain:
            wins += 0.5 # Egalitate (Split pot)
            
        # Salvam progresul pentru grafic
        history.append(wins / i)
        
    final_equity = wins / n_sims
    return final_equity, history

# ==========================================
# 3. ANTRENORUL (COACH & PLOTTING)
# ==========================================

def get_coach_advice(equity, vs_random=False):
    """Genereaza un sfat in romana bazat pe procentaj."""
    if vs_random:
        # Sfat general (vs Mana necunoscuta)
        if equity > 0.65: return "🚀 MONSTRU! (Raise / All-in / Joaca-ti casa)"
        if equity > 0.55: return "✅ Mana Buna (Joaca agresiv)"
        if equity > 0.45: return "⚠️ Marginala (Pozitie sau Fold)"
        return "🗑️ Slaba (Fold recomandat / Du-te acasa / Iesi baa)"
    else:
        # Sfat specific (vs Mana cunoscuta)
        if equity > 0.60: return "Esti FAVORIT clar! Sanse peste 60"
        if equity > 0.45: return "Discutabil"
        return "Probabil pierzi"

def run_poker_coach():
    print("\n" + "="*50)
    print("      ♠ ♥ ♦ ♣  POKER MONTE CARLO  ♣ ♦ ♥ ♠")
    print("="*50)
    print("Alege modul de simulare:")
    print(" [1] Eu vs. Adversar Specific (Ex: KK vs AA)")
    print(" [2] Eu vs. Mana Aleatorie (Cat de buna e mana mea?)")
    
    mode = input("\nIntrodu 1 sau 2: ").strip()
    
    print("\n--- NOTATIE CARTI ---")
    print("Foloseste: 2-9, T, J, Q, K, A")
    print("Culori: h=Inima(♥), d=Romb(♦), s=Pica(♠), c=Trefla(♣)")
    print("Exemplu: AhKh (As si Popa de Inima)")
    
    h_str = input("\n>> Mana ta: ").strip()
    
    print(">> Carti pe masa? (Lasa GOL si apasa Enter daca esti Pre-Flop)")
    b_str = input(">> Board: ").strip()
    
    v_str = None
    if mode == "1":
        v_str = input(">> Mana adversar: ").strip()
        titlu_grafic = f"Simulare: {h_str} vs {v_str}"
        vs_random = False
    else:
        titlu_grafic = f"Simulare: {h_str} vs Random"
        vs_random = True
        
    # Configurare simulare
    N_SIMS = 100000
    print(f"\nRulez {N_SIMS} simulari...")
    
    # Rulare
    equity, istoric = run_simulation(h_str, v_str, b_str, N_SIMS)
    
    # Calcule statistice (Inegalitatea Hoeffding)
    # E = sqrt(ln(2/alpha) / 2N). Pentru 95% incredere, termenul e ~1.36 / sqrt(N)
    marja_eroare = 1.36 / math.sqrt(N_SIMS)
    
    print("\n" + "="*40)
    print(f" REZULTATE FINALE")
    print("="*40)
    print(f"Sanse de Castig (Equity): {equity:.2%}")
    print(f"Marja eroare teoretica:   +/- {marja_eroare:.2%}")
    print("-" * 40)
    print(f"SFATUL ANTRENORULUI:\n👉 {get_coach_advice(equity, vs_random)}")
    print("="*40)
    
    # GRAFIC
    plt.figure(figsize=(10, 6))
    x_axis = range(1, len(istoric) + 1)
    
    # Plotare linie principala
    plt.plot(x_axis, istoric, label='Evolutie Monte Carlo', color='#007acc', linewidth=1.5)
    
    # Linie orizontala finala
    plt.axhline(y=equity, color='red', linestyle='--', label=f'Final: {equity:.3f}')
    
    # Zona de incredere
    limita_sus = [min(1.0, equity + marja_eroare)] * len(istoric)
    limita_jos = [max(0.0, equity - marja_eroare)] * len(istoric)
    plt.fill_between(x_axis, limita_jos, limita_sus, color='red', alpha=0.1, label='Marja Eroare 95%')
    
    # Estetica grafic
    plt.title(titlu_grafic, fontsize=14)
    plt.xlabel('Numar de Simulari', fontsize=12)
    plt.ylabel('Probabilitate de Castig (0-1)', fontsize=12)
    plt.ylim(0, 1)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    print("Generare grafic...")
    plt.show()

run_poker_coach()