import copy

class AwaleGame:
    def __init__(self):
        # 16 holes, each with [Red, Blue, Transparent]
        # Index 0-15. 
        # Player 0 (Odd holes in UI 1..15) -> Indices 0, 2, 4... wait.
        # Rules: "First player has the odd holes (1, 3..), second player has even holes (2, 4..)"
        # Let's map UI 1-16 to Internal 0-15.
        # Player 0 owns: 0, 2, 4, 6, 8, 10, 12, 14 (Indices are 0-based, so Hole 1 is Index 0)
        # Player 1 owns: 1, 3, 5, 7, 9, 11, 13, 15
        
        self.board = [[2, 2, 2] for _ in range(16)] # [R, B, T]
        self.scores = [0, 0] # Player 0, Player 1
        self.current_player = 0 # 0 starts
        self.moves_played = 0 # Track number of moves
        self.history = [] # To store moves if needed
        self.winner = None

    def clone(self):
        """Creates a deep copy of the game state for simulation."""
        return copy.deepcopy(self)

    def set_state(self, board_values, score_p1, score_p2):
        """Force l'état du jeu (utilisé quand le serveur nous envoie le plateau)."""
        self.board = copy.deepcopy(board_values)
        self.scores = [score_p1, score_p2]

    def display_board(self):
        print(f"\ntour: {self.moves_played + 1}/400")
        print(f"score j1 (impair): {self.scores[0]}")
        print(f"score j2 (pair)  : {self.scores[1]}")
        
        # affichage simple 1-16
        for i in range(16):
            owner = "j1" if i % 2 == 0 else "j2"
            r, b, t = self.board[i]
            print(f"trou {i+1:2} ({owner}): {r}R {b}B {t}T")
        print("")

    def get_valid_moves(self):
        """Returns a list of valid moves for current player."""
        moves = []
        # Player 0 owns indices 0, 2, 4...
        # Player 1 owns indices 1, 3, 5...
        start_idx = 0 if self.current_player == 0 else 1
        
        for i in range(start_idx, 16, 2):
            r, b, t = self.board[i]
            if r > 0: moves.append((i, 'R'))
            if b > 0: moves.append((i, 'B'))
            if t > 0:
                moves.append((i, 'TR')) # Transparent as Red
                moves.append((i, 'TB')) # Transparent as Blue
        return moves

    def play_move(self, hole_idx, color_code):
        """
        hole_idx: 0-15
        color_code: 'R', 'B', 'TR', 'TB'
        """
        # Validation
        if hole_idx < 0 or hole_idx > 15:
            return False, "Invalid hole number."
        
        # Check ownership
        # Player 0 must play even indices (Hole 1, 3...), Player 1 odd indices (Hole 2, 4...)
        if hole_idx % 2 != self.current_player:
            return False, "That hole does not belong to you."

        r, b, t = self.board[hole_idx]
        
        seeds_to_sow = []
        
        # Determine what seeds we pick up
        if color_code == 'R':
            if r == 0: return False, "No Red seeds in this hole."
            self.board[hole_idx][0] = 0
            seeds_to_sow = ['R'] * r
            target_mode = 'ALL' # Sows in all holes
            
        elif color_code == 'B':
            if b == 0: return False, "No Blue seeds in this hole."
            self.board[hole_idx][1] = 0
            seeds_to_sow = ['B'] * b
            target_mode = 'OPPONENT' # Sows only in opponent holes
            
        elif color_code == 'TR':
            if t == 0: return False, "No Transparent seeds in this hole."
            # Take Transparent AND Red
            self.board[hole_idx][2] = 0 # Remove T
            self.board[hole_idx][0] = 0 # Remove R
            # Transparent distributed FIRST
            seeds_to_sow = ['T'] * t + ['R'] * r
            target_mode = 'ALL' # Acts like Red
            
        elif color_code == 'TB':
            if t == 0: return False, "No Transparent seeds in this hole."
            # Take Transparent AND Blue
            self.board[hole_idx][2] = 0 # Remove T
            self.board[hole_idx][1] = 0 # Remove B
            # Transparent distributed FIRST
            seeds_to_sow = ['T'] * t + ['B'] * b
            target_mode = 'OPPONENT' # Acts like Blue
            
        else:
            return False, "Invalid color code."

        if not seeds_to_sow:
             return False, "No seeds to sow."

        # --- SOWING PROCESS ---
        current_idx = hole_idx
        last_sown_idx = -1
        
        for seed in seeds_to_sow:
            while True:
                current_idx = (current_idx + 1) % 16
                
                # Skip original hole
                if current_idx == hole_idx:
                    continue
                
                # Check constraints based on color/mode
                # If mode is OPPONENT, we only sow in opponent's holes
                # Opponent of P0 (Even indices) is P1 (Odd indices)
                # Opponent of P1 (Odd indices) is P0 (Even indices)
                
                is_opponent_hole = (current_idx % 2 != self.current_player)
                
                if target_mode == 'OPPONENT' and not is_opponent_hole:
                    continue # Skip this hole
                
                # If we are here, we can drop the seed
                break
            
            # Drop the seed
            # If it's a Transparent seed, it stays Transparent in the hole
            # If it's R or B, it stays R or B
            if seed == 'R':
                self.board[current_idx][0] += 1
            elif seed == 'B':
                self.board[current_idx][1] += 1
            elif seed == 'T':
                self.board[current_idx][2] += 1
                
            last_sown_idx = current_idx

        # --- CAPTURE PROCESS ---
        # Check capture starting from last_sown_idx and moving backwards
        self._check_capture(last_sown_idx)
        
        # Switch player
        self.current_player = 1 - self.current_player
        self.moves_played += 1
        return True, "Move successful."

    def _check_capture(self, start_idx):
        curr = start_idx
        captured_total = 0
        
        # We loop backwards. We need a safety break to avoid infinite loops if board is full of 2s and 3s
        # But logically we stop when a hole doesn't meet criteria.
        # We can check at most 16 holes.
        
        for _ in range(16):
            r, b, t = self.board[curr]
            total = r + b + t
            
            if 2 <= total <= 3:
                # Capture!
                self.scores[self.current_player] += total
                self.board[curr] = [0, 0, 0] # Empty the hole
                captured_total += total
                
                # Move to previous hole
                curr = (curr - 1) % 16
            else:
                # Chain broken
                break
                
    def is_game_over(self):
        # 1. 49 or more seeds
        if self.scores[0] >= 49: return True, "Player 1 Wins!"
        if self.scores[1] >= 49: return True, "Player 2 Wins!"
        
        # 2. Less than 10 seeds remaining on board
        total_on_board = sum(sum(hole) for hole in self.board)
        if total_on_board < 10:
            if self.scores[0] > self.scores[1]: return True, "Player 1 Wins (Board < 10)!"
            elif self.scores[1] > self.scores[0]: return True, "Player 2 Wins (Board < 10)!"
            else: return True, "Draw!"
            
        # 3. 400 moves limit
        if self.moves_played >= 400:
             if self.scores[0] > self.scores[1]: return True, "Player 1 Wins (400 moves limit)!"
             elif self.scores[1] > self.scores[0]: return True, "Player 2 Wins (400 moves limit)!"
             else: return True, "Draw (400 moves limit)!"

        return False, None
