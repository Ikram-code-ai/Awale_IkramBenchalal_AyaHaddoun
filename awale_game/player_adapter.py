import sys
import os
import re

# Ensure we can import from local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import AwaleGame
from bot import MinimaxBot

# Recuperer l'argument joueur (Joueur1 ou Joueur2) passe par l'arbitre
# Joueur1 = trous impairs (1,3,5...) = player_id 0 = joue en premier
# Joueur2 = trous pairs (2,4,6...) = player_id 1 = joue en second
player_arg = sys.argv[1] if len(sys.argv) > 1 else "Joueur1"

# Determiner le player_id en fonction de l'argument
if player_arg == "Joueur1":
    ASSIGNED_PLAYER_ID = 0  # Trous impairs, joue en premier
elif player_arg == "Joueur2":
    ASSIGNED_PLAYER_ID = 1  # Trous pairs, joue en second
else:
    ASSIGNED_PLAYER_ID = None  # Sera determine dynamiquement

# logs sur stderr, desactive par defaut (plus stable + plus rapide)
DEBUG = os.environ.get("AWALE_DEBUG", "0") == "1"

def log(*args):
    if DEBUG:
        print(f"[{player_arg}]", *args, file=sys.stderr)

def save_score(game):
    try:
        s1, s2 = game.scores
        with open(f"score_{player_arg}.txt", "w") as f:
            f.write(f"{s1} {s2}")
    except:
        pass

def is_move_really_playable(game, move):
    hole_idx, color = move
    if hole_idx < 0 or hole_idx > 15:
        return False
    r, b, t = game.board[hole_idx]
    if color == 'R':
        return r > 0
    if color == 'B':
        return b > 0
    if color in ('TR', 'TB'):
        return t > 0
    return False

def pick_safe_move(game, preferred_move=None):
    valid_moves = game.get_valid_moves()
    if preferred_move is not None and preferred_move in valid_moves and is_move_really_playable(game, preferred_move):
        return preferred_move
    
    # Fallback: Prefer reliable moves (R/B) over Special moves (TR/TB) which might be desynced
    for m in valid_moves:
        if m[1] in ['R', 'B'] and is_move_really_playable(game, m):
            return m
            
    for m in valid_moves:
        if is_move_really_playable(game, m):
            return m
    return None

def main():
    log(f"Player Adapter Started - {player_arg} (player_id={ASSIGNED_PLAYER_ID})")
    game = AwaleGame()
    my_player_id = ASSIGNED_PLAYER_ID
    bot = MinimaxBot(player_id=my_player_id, depth=3) if my_player_id is not None else None

    while True:
        try:
            # Read from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            log(f"Received: '{line}'")

            if line == "START":
                # START means we are First Player (Player 0) - should match Joueur1
                if my_player_id is None:
                    my_player_id = 0
                    bot = MinimaxBot(player_id=my_player_id, depth=3)
                
                # We need to make the first move
                best_move = bot.get_best_move(game)
                safe_move = pick_safe_move(game, best_move)
                if safe_move:
                    hole_idx, color = safe_move
                    ok, msg = game.play_move(hole_idx, color)
                    save_score(game)
                    if not ok:
                        # si ca arrive, on prefere arreter plutot que desync
                        s1, s2 = game.scores
                        print(f"RESULT COUP_INVALIDE {s1} {s2}", flush=True)
                        break
                    move_str = f"{hole_idx + 1}{color}"
                    
                    # Check if this first move somehow wins immediately (unlikely but safe)
                    is_over, message = game.is_game_over()
                    if is_over:
                        s1, s2 = game.scores
                        print(f"RESULT {move_str} {s1} {s2}", flush=True)
                    else:
                        print(move_str, flush=True)
                        
                    log(f"Played: {move_str}")
                else:
                    print("RESULT BLOCKED 0 0", flush=True)
            
            elif "RESULT" in line:
                log("Game Over received.")
                break
            
            else:
                # It's an opponent's move
                # Expected format: "3R" or "15TB"
                match = re.match(r"(\d+)([A-Z]+)", line)
                if match:
                    hole_num = int(match.group(1))
                    color = match.group(2)
                    hole_idx = hole_num - 1 # Convert 1-based to 0-based
                    
                    # Apply opponent move
                    success, msg = game.play_move(hole_idx, color)
                    save_score(game)
                    if not success:
                        # si on continue, on desync et ensuite on joue n'importe quoi.
                        # donc on termine proprement.
                        s1, s2 = game.scores
                        print(f"RESULT INVALID_OPP_MOVE {s1} {s2}", flush=True)
                        break
                    
                    # Check if game over after opponent move
                    is_over, message = game.is_game_over()
                    if is_over:
                        log(f"Game Over detected after receive: {message}")
                        s1, s2 = game.scores
                        # We use the opponent's move 'line' as the 'coup' that ended the game
                        print(f"RESULT {line} {s1} {s2}", flush=True)
                        break
                    
                    # Si le bot n'est pas encore initialise (fallback), le creer maintenant
                    if bot is None:
                        if my_player_id is None:
                            my_player_id = 1  # Par defaut si pas d'argument
                        bot = MinimaxBot(player_id=my_player_id, depth=3)
                    
                    # My turn
                    best_move = bot.get_best_move(game)
                    safe_move = pick_safe_move(game, best_move)
                    if safe_move:
                        hole_idx, color = safe_move
                        ok, msg = game.play_move(hole_idx, color)
                        if not ok:
                            s1, s2 = game.scores
                            print(f"RESULT COUP_INVALIDE {s1} {s2}", flush=True)
                            break
                        move_str = f"{hole_idx + 1}{color}"
                        
                        # Check if my move resulted in Game Over
                        is_over, message = game.is_game_over()
                        if is_over:
                             log(f"Game Over detected after move: {message}")
                             s1, s2 = game.scores
                             print(f"RESULT {move_str} {s1} {s2}", flush=True)
                             break
                        else:
                             print(move_str, flush=True)
                             
                        log(f"Played: {move_str}")
                    else:
                        # Cannot move
                        log("No more moves possible")
                        s1, s2 = game.scores
                        print(f"RESULT BLOCKED {s1} {s2}", flush=True)
                        break
                        
                else:
                    log(f"Unknown command: {line}")

        except Exception as e:
            log(f"Error in player loop: {e}")
            break

if __name__ == "__main__":
    main()
