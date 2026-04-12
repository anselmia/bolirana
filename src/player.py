class Player:
    def __init__(self, id, team=None):
        self.id = id
        self.team = team
        self.order = 0
        self.reset()

    def __str__(self):
        return f"Joueur {self.id}"

    def sync_win_state(self, win_threshold, reset_rank_on_loss=False):
        has_won = self.score >= win_threshold
        self.won = has_won
        if reset_rank_on_loss and not has_won:
            self.rank = 0

    def apply_score_delta(self, delta, win_threshold, reset_rank_on_loss=False):
        self.score += delta
        self.sync_win_state(
            win_threshold,
            reset_rank_on_loss=reset_rank_on_loss,
        )

    def goal(self, points, win_threshold):
        self.apply_score_delta(points, win_threshold)
        self.turn_score += points
        self.turn_hits += 1
        self.successful_shots += 1
        self.max_combo = max(self.max_combo, self.turn_hits)
        self.best_turn = max(self.best_turn, self.turn_score)

    def reset(self):
        self.score = 0
        self.won = False
        self.rank = 0
        self.turn_score = 0
        self.turn_hits = 0
        self.is_active = False
        self.turns_played = 0
        self.successful_shots = 0
        self.best_turn = 0
        self.max_combo = 0
        self.sequence_progress = 0
        self.little_frog_streak = 0

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def reset_turn(self):
        self.turn_score = 0
        self.turn_hits = 0
        self.little_frog_streak = 0

    def finish_turn(self):
        self.turns_played += 1
        self.reset_turn()

    @staticmethod
    def activate_next_player(current_player, players):
        valid_players = [p for p in players if p.order is not None and not p.won]

        if not valid_players:
            current_player.finish_turn()
            current_player.deactivate()
            return current_player

        if len(players) == 1 or (len(players) > 1 and len(valid_players) == 1):
            next_player = valid_players[0]
            current_player.finish_turn()
            if current_player is not next_player:
                current_player.deactivate()
                next_player.activate()
            else:
                current_player.activate()
            return next_player

        sorted_players = sorted(valid_players, key=lambda x: x.order)

        if current_player not in valid_players:
            current_order = current_player.order
            for player in sorted_players:
                if player.order > current_order:
                    next_player = player
                    break
            else:
                next_player = sorted_players[0]
        else:
            current_index = sorted_players.index(current_player)
            next_index = (current_index + 1) % len(sorted_players)
            next_player = sorted_players[next_index]

        current_player.finish_turn()
        current_player.deactivate()
        next_player.activate()

        return next_player
