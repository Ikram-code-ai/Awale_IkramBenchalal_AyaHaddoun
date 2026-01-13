from game import AwaleGame
from bot import MinimaxBot
import time

def main():
    # initialisation du jeu
    game = AwaleGame()
    
    # print("1. humain vs humain")
    # print("2. humain vs bot")
    # print("3. bot vs bot")
    # choice = input("choisis le mode (1, 2 ou 3) : ").strip()
    choice = '3'
    
    bot1 = None
    bot2 = None

    if choice == '2':
        # le bot sera le joueur 2 (trous pairs)
        bot2 = MinimaxBot(player_id=1, depth=3)
        # print("je suis joueur 1 (impairs). le bot est joueur 2 (pairs).")
    
    elif choice == '3':
        # deux bots s'affrontent
        bot1 = MinimaxBot(player_id=0, depth=3)
        bot2 = MinimaxBot(player_id=1, depth=3)
        # print("mode bot vs bot active.")
        time.sleep(1)
    
    # print("commandes : '1 r' (trou 1, rouge), '15 tb' (trou 15, transparent en bleu)")
    
    while True:
        # affichage du plateau a chaque tour
        # game.display_board()
        
        # verification si la partie est finie
        is_over, message = game.is_game_over()
        if is_over:
            # print(f"partie terminee: {message}")
            break
            
        # --- TOUR DU BOT 1 (S'il existe et c'est son tour) ---
        if bot1 and game.current_player == bot1.player_id:
            # print(f"[bot 1] reflechit...")
            # Petit délai pour qu'on ait le temps de voir ce qui se passe (optionnel)
            # time.sleep(0.5) 
            best_move = bot1.get_best_move(game)
            if best_move:
                hole_idx, color = best_move
                print(f"{hole_idx + 1}{color}")
                game.play_move(hole_idx, color)
            else:
                # print("[bot 1] bloque ou abandon.")
                break
            continue

        # --- TOUR DU BOT 2 (S'il existe et c'est son tour) ---
        if bot2 and game.current_player == bot2.player_id:
            # print(f"[bot 2] reflechit...")
            # Petit délai pour qu'on ait le temps de voir ce qui se passe (optionnel)
            # time.sleep(0.5)
            best_move = bot2.get_best_move(game)
            if best_move:
                hole_idx, color = best_move
                print(f"{hole_idx + 1}{color}")
                game.play_move(hole_idx, color)
            else:
                # print("[bot 2] bloque ou abandon.")
                break
            continue

        # --- TOUR DE L'HUMAIN (Si aucun bot ne joue ce tour) ---
        player_name = "joueur 1" if game.current_player == 0 else "joueur 2"
        # user_input = input(f"[{player_name}] entre mon coup (ex: 3 r) : ").strip().upper()
        
        # Minimal input support
        try:
             user_input = input().strip().upper()
        except EOFError:
             break
        
        if user_input == "EXIT":
            break
            
        try:
            parts = user_input.split()
            # support du format colle (ex: 3R) ou separe (ex: 3 R)
            if len(parts) == 1:
               # parsing simple pour "3R"
               import re
               match = re.match(r"(\d+)([A-Z]+)", parts[0])
               if match:
                   hole_num = int(match.group(1))
                   color = match.group(2)
               else:
                   continue
            elif len(parts) == 2:
                hole_num = int(parts[0])
                color = parts[1]
            else:
                # print("format invalide. utilise 'numero couleur' (ex: 1 r)")
                continue
            
            # conversion 1-16 (utilisateur) vers 0-15 (interne)
            hole_idx = hole_num - 1
            
            success, msg = game.play_move(hole_idx, color)
            if success:
                # print(f"coup joue : {msg}")
                pass
            else:
                # print(f"erreur : {msg}")
                pass
                
        except ValueError:
            pass # print("erreur : le numero du trou doit etre un entier.")
        except Exception as e:
            pass # print(f"erreur inattendue : {e}")

if __name__ == "__main__":
    main()
