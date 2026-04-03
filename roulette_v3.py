import random as rd
import sys 
import time
import math
import re


# --- CONFIGURATION DIMENSIONS (168 COLONNES) ---
LARGEUR_TERM = 168
COLONNE_CROUPIER = 143 

# --- CONSTANTES DE COULEUR ---
CLR_CROUPIER = "\033[96m"    # Cyan
CLR_JOUEUR   = "\033[95m"    # Magenta
CLR_GAIN     = "\033[1;92m"  # Vert Gras
CLR_PERTE    = "\033[1;91m"  # Rouge Gras
CLR_OR       = "\033[93m"    # Jaune
RESET        = "\033[0m"

# --- CONFIGURATION DU JEU ---
TYPE_PARI = ["couleur", "chiffre", "pair-impair"]
PLATEAU = {
    0: "vert", 32: "rouge", 15: "noir", 19: "rouge", 4: "noir", 21: "rouge", 2: "noir",
    25: "rouge", 17: "noir", 34: "rouge", 6: "noir", 27: "rouge", 13: "noir",
    36: "rouge", 11: "noir", 30: "rouge", 8: "noir", 23: "rouge", 10: "noir",
    5: "rouge", 24: "noir", 16: "rouge", 33: "noir", 1: "rouge", 20: "noir",
    14: "rouge", 31: "noir", 9: "rouge", 22: "noir", 18: "rouge", 29: "noir",
    7: "rouge", 28: "noir", 12: "rouge", 35: "noir", 3: "rouge", 26: "noir"
}

# Ordre réel des numéros sur une roulette européenne
ORDRE_ROULETTE = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

CREDIT_JOUEUR = 100

# --- CONFIGURATION DU CROUPIER ---
CROUPIER_ART = [
    "      @@@@@@@@@@@@@      ", "    @@@@@@@@@@@@@@@@@    ",
    "   @@@@@@@@@@@@@@@@@@@@  ", "  @@@@@@@@@@@@@@@@@@@@@@ ",
    " @@@@               .@@@ ", " @@@@                @@@ ",
    "  @@@                @@@ ", "  @@    @#      @@:   @@ ",
    "   @                  @  ", "   @    @        @    @  ",
    " @                      @", "  @                    % ",
    "    @                    ", "          %~--~%@        ",
    "            @@           ", "       @          :      ",
    "      @  =      @   @    ", "     % %           @ @   ",
    "   @@    +            @@ ", " @@@@@      @   @      @@"
]

IDX_B1, IDX_B2 = 13, 14
B1_IDLE = "          %~--~%@        " # Sourire repos
B1_A    = "          %@@%%@         " # Bouche fermée
B1_B    = "          %@@@@@         " # Bouche ouverte
B1_C    = "          %@--@%@        " # Bouche en O
B2_IDLE = "            @@           "
B2_ANIM = "           @@@@          "

# --- PRÉ-CALCUL DES COORDONNÉES DE LA ROUE ---
# On place la roue assez bas (Y=22) pour laisser de la place au texte en haut
centre_x, centre_y = 40, 22 
rayon_x, rayon_y = 30, 10
COORDS_ROUE = {}
for i in range(37):
    angle = (i / 37) * 2 * math.pi - (math.pi / 2)
    x = round(centre_x + rayon_x * math.cos(angle))
    y = round(centre_y + rayon_y * math.sin(angle))
    COORDS_ROUE[i] = (x, y)

# --- FONCTIONS VISUELLES ---

def effacer_ecran():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def banniere():
    print(f"{CLR_OR}{'=' * LARGEUR_TERM}")
    print("🎰   BIENVENUE AU CASINO ROULETTE   🎰".center(LARGEUR_TERM))
    print(f"{'=' * LARGEUR_TERM}{RESET}")

def dessiner_croupier_statique():
    sys.stdout.write(CLR_CROUPIER)
    for i, ligne in enumerate(CROUPIER_ART):
        sys.stdout.write(f"\033[{i+6};{COLONNE_CROUPIER}H{ligne}")
    sys.stdout.write(RESET)

# ============================================================
# --- CRÉATION IA : FONCTION D'AFFICHAGE DU CROUPIER ---
# ============================================================
def dis_croupier(texte, vitesse=0.020):
    effacer_ecran()
    banniere()
    dessiner_croupier_statique()
    
    # On écrit le texte ligne 8 pour éviter la collision avec la roue (ligne 11+)
    ligne_curseur = 8 
    print(f"\033[{ligne_curseur};5H", end="")
    sys.stdout.write(CLR_CROUPIER + "Croupier : ")
    
    ansi_matcher = re.compile(r'(\033\[[0-9;]*m)')
    segments = ansi_matcher.split(texte)
    
    compteur_lettres = 0
    for seg in segments:
        if ansi_matcher.match(seg):
            sys.stdout.write(seg)
            sys.stdout.flush()
        else:
            for char in seg:
                sys.stdout.write(char)
                sys.stdout.flush()
                compteur_lettres += 1
                
                if compteur_lettres % 3 == 0:
                    cycle = (compteur_lettres // 3) % 3
                    print("\033[s", end="")
                    print(f"\033[{IDX_B1 + 6};{COLONNE_CROUPIER}H", end="")
                    sys.stdout.write(CLR_CROUPIER)
                    if cycle == 0: sys.stdout.write(B1_A)
                    elif cycle == 1: sys.stdout.write(B1_B)
                    else: sys.stdout.write(B1_C)
                    print(f"\033[{IDX_B2 + 6};{COLONNE_CROUPIER}H{B2_ANIM if cycle > 0 else B2_IDLE}", end="")
                    print("\033[u", end="")
                time.sleep(vitesse)
            
    # Retour au sourire
    print("\033[s", end="")
    sys.stdout.write(CLR_CROUPIER)
    print(f"\033[{IDX_B1 + 6};{COLONNE_CROUPIER}H{B1_IDLE}\033[{IDX_B2 + 6};{COLONNE_CROUPIER}H{B2_IDLE}", end="")
    sys.stdout.write(RESET)
    print("\033[u", end="")
    print(f"\033[35;5H")

def animation_roulette(numero_gagnant):
    index_gagnant = ORDRE_ROULETTE.index(numero_gagnant)
    total_deplacements = (37 * 2) + index_gagnant
    
    sys.stdout.write("\033[?25l") # Cache le curseur
    
    for d in range(total_deplacements + 1):
        sys.stdout.write("\033[H") # Home sans clear pour fluidité
        banniere()
        dessiner_croupier_statique()
        
        index_balle = d % 37
        for pos, num in enumerate(ORDRE_ROULETTE):
            x, y = COORDS_ROUE[pos]
            couleur = PLATEAU[num]
            balle = "●" if pos == index_balle else " "
            num_str = f"{num:2}"
            
            if couleur == "rouge": bg = "\033[41m"
            elif couleur == "noir": bg = "\033[40m"
            else: bg = "\033[42m"
            
            sys.stdout.write(f"\033[{y};{x}H{bg}\033[37;1m{balle}{num_str}{RESET}")
        
        sys.stdout.flush()
        
        # Ralentissement progressif
        if d > total_deplacements - 15:
            time.sleep(0.06 + (d - (total_deplacements - 15)) * 0.04)
        else:
            time.sleep(0.04)
            
    sys.stdout.write("\033[?25h") # Réaffiche le curseur
    time.sleep(1.5)

# --- FONCTIONS DE JEU (TES LOGIQUES) ---

def choix_joueur():
    global CREDIT_JOUEUR
    msg = f"Vous disposez de {CLR_OR}{CREDIT_JOUEUR}{RESET}{CLR_CROUPIER} credits.\nVoici les types de pari :\n - couleur\n - chiffre\n - pair-impair"
    dis_croupier(msg)
    
    choix_pari = [None, None, None]
    while choix_pari[0] not in TYPE_PARI:
        print(f"\033[35;5H\033[K", end="")
        choix_pari[0] = input(f"{CLR_JOUEUR}Joueur (Type): {RESET}").lower().strip()

    if choix_pari[0] == TYPE_PARI[0]:
        while choix_pari[1] not in ["noir", "rouge"]:
            dis_croupier("Sur quelle couleur voulez-vous miser ? (noir, rouge)")
            choix_pari[1] = input(f"{CLR_JOUEUR}Joueur (Couleur): {RESET}").lower().strip()
            
    elif choix_pari[0] == TYPE_PARI[1]:
        while choix_pari[1] not in PLATEAU:
            dis_croupier("Sur quel nombre voulez-vous miser ? (0-36)")
            entree = input(f"{CLR_JOUEUR}Joueur (Nombre): {RESET}")
            if entree.isdigit(): 
                n = int(entree)
                if 0 <= n <= 36: choix_pari[1] = n
                else: dis_croupier("Le nombre est hors limite !")
            else: dis_croupier("Veuillez entrer un nombre entier valide.")
                
    elif choix_pari[0] == TYPE_PARI[2]:
        while choix_pari[1] not in ["pair", "impair"]:
            dis_croupier("Voulez-vous miser sur pair ou impair ?")
            choix_pari[1] = input(f"{CLR_JOUEUR}Joueur (Choix): {RESET}").lower().strip()

    while choix_pari[2] is None:
        dis_croupier(f"Quelle somme voulez-vous miser ? (Solde: {CLR_OR}{CREDIT_JOUEUR}{RESET}{CLR_CROUPIER})")
        entree = input(f"{CLR_JOUEUR}Joueur (Mise): {RESET}")
        if entree.isdigit():
            mise = int(entree)
            if mise > CREDIT_JOUEUR: 
                dis_croupier("Helas, pas assez de credits.")
                time.sleep(1.5)
            elif mise <= 0: 
                dis_croupier("La mise doit etre positive.")
                time.sleep(1.5)
            else:
                choix_pari[2] = mise
                CREDIT_JOUEUR -= mise
        else:
            dis_croupier("Je n'accepte que les nombres.")
            time.sleep(1.5)
    return choix_pari

def resultat_roulette():
    res = rd.randint(0, 36)
    coul = PLATEAU[res]
    parite = "pair" if (res % 2 == 0 and res != 0) else "impair"
    if res == 0: parite = "neutre"
    return [res, coul, parite]

def resultat_pari(tab_joueur, res_roulette):
    global CREDIT_JOUEUR
    gain = 0
    reussite = False
    
    if tab_joueur[0] == TYPE_PARI[0] and tab_joueur[1] == res_roulette[1]:
        gain = tab_joueur[2] * 2
        reussite = True
    elif tab_joueur[0] == TYPE_PARI[1] and tab_joueur[1] == res_roulette[0]:
        gain = tab_joueur[2] * 36
        reussite = True
    elif tab_joueur[0] == TYPE_PARI[2] and tab_joueur[1] == res_roulette[2]:
        gain = tab_joueur[2] * 2
        reussite = True
        
    if reussite:
        CREDIT_JOUEUR += gain
        dis_croupier(f"{CLR_GAIN}Felicitation ! Vous avez remporte {gain} credits !{RESET}")
    else:
        dis_croupier(f"{CLR_PERTE}Dommage, la banque rafle la mise.{RESET}")
    
    time.sleep(2.0)
    dis_croupier(f"Votre nouveau solde est de {CLR_OR}{CREDIT_JOUEUR}{RESET}{CLR_CROUPIER} credits.")

def manager():
    global CREDIT_JOUEUR
    dis_croupier("Bienvenue Monsieur. La table est ouverte, desirez-vous jouer ?")
    print(f"\033[35;5H", end="")
    entree = input(f"{CLR_JOUEUR}Joueur (oui/non): {RESET}").lower().strip()
    
    if entree != "oui": return

    jouer = "oui"
    while jouer == "oui" and CREDIT_JOUEUR > 0:
        pari = choix_joueur()
        dis_croupier("Les jeux sont faits ! Rien ne va plus...")
        time.sleep(1)
        
        tirage_data = resultat_roulette()
        animation_roulette(tirage_data[0]) # Animation de ton camarade
        
        dis_croupier(f"La bille s'arrete sur le {tirage_data[0]} {tirage_data[1]} ({tirage_data[2]}).")
        time.sleep(2.5) # Pause pour voir le résultat
        
        resultat_pari(pari, tirage_data)
        
        if CREDIT_JOUEUR > 0:
            time.sleep(1.5)
            dis_croupier("Voulez-vous relancer une partie ?")
            jouer = input(f"{CLR_JOUEUR}Joueur (oui/non): {RESET}").lower().strip()
        else:
            time.sleep(2.0)
            dis_croupier("Vous n'avez plus de credits. Au revoir !")

if __name__ == "__main__":
    manager()