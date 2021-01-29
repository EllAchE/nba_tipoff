class Player:
    def __init__(self, player_code, tip_wins, tip_losses, first_scores, first_shots, rating_obj):
        self.player_code = player_code
        self.tip_wins = tip_wins
        self.tip_losses = tip_losses
        self.first_scores = first_scores
        self.first_shots = first_shots
        self.rating_obj = rating_obj
        self.current_team = None
        self.season_ranking = None