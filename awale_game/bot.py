import random
import time

class MinimaxBot:
    def __init__(self, player_id, depth=3):
        self.player_id = player_id
        self.depth = depth
        self.time_limit = 1.9  # marge de securite sur 2s
        self.node_count = 0  # pour verifier timeout regulierement

    def _time_up(self, start):
        return (time.perf_counter() - start) > self.time_limit

    def evaluate(self, game):
        my_score = game.scores[self.player_id]
        opp_score = game.scores[1 - self.player_id]
        
        # victoire ou defaite immediate
        if my_score > 48:
            return 10000
        if opp_score > 48:
            return -10000
        
        # indices de mes trous et ceux de l'adversaire
        my_start = 0 if self.player_id == 0 else 1
        opp_start = 1 - my_start
        
        # compter mes graines et ma mobilite
        my_seeds = 0
        my_mobility = 0
        for i in range(my_start, 16, 2):
            r, b, t = game.board[i]
            my_seeds += r + b + t
            if r > 0: my_mobility += 1
            if b > 0: my_mobility += 1
            if t > 0: my_mobility += 2
        
        # compter les graines adverses et le potentiel de capture
        opp_seeds = 0
        capture_potential = 0
        for i in range(opp_start, 16, 2):
            r, b, t = game.board[i]
            total = r + b + t
            opp_seeds += total
            # trous avec 1 ou 2 graines = capturable facilement
            if total == 1 or total == 2:
                capture_potential += 3
        
        # penalite si on a peu de mobilite (risque de blocage)
        mobility_bonus = my_mobility * 2
        if my_mobility <= 2:
            mobility_bonus -= 10
        
        # bonus si on a plus de graines que l'adversaire (controle du jeu)
        seed_control = (my_seeds - opp_seeds) // 2
        
        # formule finale : score * 10 car c'est le plus important
        # puis les bonus secondaires
        return (my_score - opp_score) * 10 + capture_potential + mobility_bonus + seed_control

    def get_best_move(self, game):
        # iterative deepening pour utiliser le max de temps dispo
        start_time = time.perf_counter()
        best_move = None
        self.node_count = 0
        
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # au cas ou on timeout direct, on a au moins un coup
        best_move = valid_moves[0]

        # on limite la profondeur max pour eviter les timeouts
        max_depth_to_search = 5

        for d in range(1, max_depth_to_search + 1):
            if self._time_up(start_time):
                break
            try:
                move, score = self.minimax_root(game, d, start_time)
                if move is not None:
                    best_move = move
                    
            except TimeoutError:
                break
                
        return best_move

    def minimax_root(self, game, depth, start_time):
        # point d'entree du minimax, on teste tous les coups
        best_score = float('-inf')
        local_best_move = None
        
        valid_moves = game.get_valid_moves()
        random.shuffle(valid_moves)  # un peu de random pour varier

        for move in valid_moves:
            if self._time_up(start_time):
                raise TimeoutError()
            
            hole_idx, color = move
            
            simulated_game = game.clone()
            simulated_game.play_move(hole_idx, color)
            
            score = self.minimax(simulated_game, depth - 1, float('-inf'), float('inf'), False, start_time)
            
            if score > best_score:
                best_score = score
                local_best_move = move
        
        return local_best_move, best_score

    def minimax(self, game, depth, alpha, beta, is_maximizing, start_time):
        # check timeout
        if self._time_up(start_time):
            raise TimeoutError()
            
        # fin de recursion
        is_over, _ = game.is_game_over()
        if depth == 0 or is_over:
            return self.evaluate(game)

        if is_maximizing:
            max_eval = float('-inf')
            moves = game.get_valid_moves()
            for move in moves:
                if self._time_up(start_time):
                    raise TimeoutError()
                hole_idx, color = move
                
                sim_game = game.clone()
                sim_game.play_move(hole_idx, color)
                
                eval = self.minimax(sim_game, depth - 1, alpha, beta, False, start_time)
                max_eval = max(max_eval, eval)
                
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break 
            return max_eval
        else:
            min_eval = float('inf')
            moves = game.get_valid_moves()
            for move in moves:
                if self._time_up(start_time):
                    raise TimeoutError()
                hole_idx, color = move
                
                sim_game = game.clone()
                sim_game.play_move(hole_idx, color)
                
                eval = self.minimax(sim_game, depth - 1, alpha, beta, True, start_time)
                min_eval = min(min_eval, eval)
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
