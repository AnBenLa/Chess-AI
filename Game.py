class Game:

    def start_state(self):
        return []

    def get_string_representation(self, current_state):
        return []

    def get_valid_actions(self, current_state, current_player):
        return []

    def finished(self, current_state, current_player):
        return True

    def reward(self, current_state, current_player):
        return 0
