class Player:
    def __init__(self, id, team=None):
        self.id = id
        self.team = team
        self.reset()

    def __str__(self):
        return f"Joueur {self.id}"

    def add_score(self, points):
        self.score += points
        return self.score

    def reset(self):
        self.score = 0
        self.won = False
        self.rank = 0
        self.turn_score = 0
        self.is_active = False

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def reset_turn(self):
        self.turn_score = 0

    @staticmethod
    def activate_next_player(current_player, players):

        # Filter players who are eligible to play
        valid_players = [p for p in players if p.order is not None and not p.won]

        # If no valid players or only one is left, no activation needed
        if not valid_players:
            return None
        elif len(players) == 1 and valid_players:
            return current_player
        elif len(players) == 1 and not valid_players:
            return None
        elif len(players) > 1 and len(valid_players) == 1:
            return None

        sorted_players = sorted(valid_players, key=lambda x: x.order)

        # If no active player is found (e.g., if the current player has just won)
        if current_player not in valid_players:
            current_order = current_player.order
            # Find the first player with an order greater than the current player's order
            for player in sorted_players:
                if player.order > current_order:
                    next_player = player
                    break
            else:
                # Wrap around to the first player in the sorted list if none are greater
                next_player = sorted_players[0]

        else:
            # Find the next player in the sorted list
            current_index = sorted_players.index(current_player)
            next_index = (current_index + 1) % len(
                sorted_players
            )  # Use modulo for wrapping around
            next_player = sorted_players[next_index]

        # Reset the turn score for cleanup
        current_player.reset_turn()

        # Deactivate current and activate next player
        current_player.deactivate()
        next_player.activate()

        return next_player

