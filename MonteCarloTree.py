from numpy.ma import sqrt


class Node:

    def __init__(self, state):
        self.current_state = state
        self.children = []
        self.expected_reward = 0
        self.predicted_reward = 0
        self.number_of_visits = 0
        self.visited = False


class MonteCarloTree:
    def __init__(self, initial_state, game, neural_network):
        self.root = Node(initial_state)
        self.game = game
        self.neural_network = neural_network

        # Q values for s, a
        self.Qsa = {}
        # N for edge s, a
        self.Nsa = {}
        # N for state s
        self.Ns = {}
        # initial policy of state s
        self.Ps = {}

        # stores information if game has ended for state s
        self.Es = {}
        # stores valid moves for state s
        self.Vs = {}

    def get_action_prob(self, current_state, simulation_number, current_player, temp=1):
        for i in range(simulation_number):
            self.find_best_action(current_state, current_player)

        #counts =

    def find_best_action(self, current_state, current_player,  c):
        best_action = None
        u_max = 0
        n_b = 0

        s = self.game.get_string_representation(current_state)

        if s not in self.Es:
            self.Es[s] = self.game.finished(current_state, current_player)
        if self.Es:
            return self.game.reward(current_state, current_player)

        if s not in self.Ps:
            reward = self.neural_network.predict(current_state)
            self.Ps[s] = reward

            possible_actions = self.game.get_valid_actions(current_state, current_player)
            #self.Ps[s] = self.Ps[s] *




        for action in possible_actions:
            n_b += action.number_of_visits

        for action in possible_actions:
            q = action.expected_reward
            p = self.neural_network.predict(action)
            n_a = action.number_of_visits

            u = q + c * p * (sqrt(n_b)) / (1 + n_a)

            if u >= u_max:
                u_max = u
                best_action = action

        new_state = self.game.process_action(current_state, best_action)

        reward = self.find_best_action(self.neural_network, new_state, (-1) * current_player, c)

        n = best_action.number_of_visits
        q = best_action.expected_reward

        best_action.expected_reward = (n * q + reward)/(n + 1)
        best_action.number_of_visits += 1

        return -reward
