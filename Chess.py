from Game import Game
import numpy as np
from copy import copy, deepcopy


class Chess(Game):
    last_board = [
        [2, 1, 0, 0, 0, 0, -1, -2],
        [3, 1, 0, 0, 0, 0, -1, -3],
        [4, 1, 0, 0, 0, 0, -1, -4],
        [5, 1, 0, 0, 0, 0, -1, -5],
        [6, 1, 0, 0, 0, 0, -1, -6],
        [4, 1, 0, 0, 0, 0, -1, -4],
        [3, 1, 0, 0, 0, 0, -1, -3],
        [2, 1, 0, 0, 0, 0, -1, -2]
    ]

    board = [
        [2, 1, 0, 0, 0, 0, -1, -2],
        [3, 1, 0, 0, 0, 0, -1, -3],
        [4, 1, 0, 0, 0, 0, -1, -4],
        [5, 1, 0, 0, 0, 0, -1, -5],
        [6, 1, 0, 0, 0, 0, -1, -6],
        [4, 1, 0, 0, 0, 0, -1, -4],
        [3, 1, 0, 0, 0, 0, -1, -3],
        [2, 1, 0, 0, 0, 0, -1, -2]
    ]

# rochade: king not in check, twer and king not move, fields inbetween not under attack
# then king two steps towards tower, tower jumps over king

# only between pawns, if pawn moves two steps ahead, a pawn that could have attacked him inbetween can do so
# 0  0  1  0  0      0  0  0  0  0     0  0  0  0  0
# 0  0  0  0  0      0  0  0  0  0     0  0  -1 0  0
# 0  -1 0  0  0      0  -1 1  0  0     0  0  0  0  0

    def __init__(self):
        super().__init__()

    def start_state(self):
        return self.board

    def get_board(self):
        return self.board

    def set_board(self, new_board):
        self.last_board = self.board
        self.board = new_board

    def get_string_representation(self, current_state):
        one_d_array = [ y for x in current_state for y in x]
        string = ','.join(map(str, one_d_array))
        return string

    def get_valid_actions(self, current_state, current_player, depth=1):
        allowed_moves = []
        for x in range(0, 8):
            for y in range(0, 8):
                piece = current_state[x][y]
                if np.sign(piece) == current_player and piece != 0:
                    if abs(piece) == 1:
                        allowed_moves.extend(self.pawn_moves(current_player, x, y, current_state, depth))
                    elif abs(piece) == 2:
                        allowed_moves.extend(self.rook_moves(current_player, x, y, current_state, depth))
                    elif abs(piece) == 3:
                        allowed_moves.extend(self.knight_moves(current_player, x, y, current_state, depth))
                    elif abs(piece) == 4:
                        allowed_moves.extend(self.bishop_moves(current_player, x, y, current_state, depth))
                    elif abs(piece) == 5:
                        allowed_moves.extend(self.king_moves(current_player, x, y, current_state, depth))
                    elif abs(piece) == 6:
                        allowed_moves.extend(self.queen_moves(current_player, x, y, current_state, depth))
        return allowed_moves

    def finished(self, current_state, current_player):
        possible_actions = self.get_valid_actions(current_state, current_player)
        if len(possible_actions) == 0:
            return True
        return False

    def reward(self, current_state, current_player):
        in_check = self.in_check(current_player, current_state, 1)
        enemy_in_check = self.in_check(-current_player, current_state, 1)
        if in_check:
            return -1
        elif enemy_in_check:
            return 1
        return 0

    def pawn_moves(self, player, x, y, current_state, depth=0):
        possible_states = []

        # move two steps ahead
        if -1 < y + 2 * player < 8 and current_state[x][y + 1 * player] == 0 and current_state[x][y + 2 * player] == 0 and ((y == 1 and player == 1) or (y == 6 and player == -1)):
            board = deepcopy(current_state)
            board[x][y + 2 * player] = board[x][y]
            board[x][y] = 0

            if not self.in_check(player, board, depth):
                possible_states.append(board)
        if -1 < y + player < 8:
            # move straight ahead

            if current_state[x][y + player] == 0:
                board = deepcopy(current_state)
                if y + player == 0 or y + player == 7:
                    board[x][y + player] = 6 * player
                else:
                    board[x][y + player] = board[x][y]
                board[x][y] = 0
                if not self.in_check(player, board, depth):
                    possible_states.append(board)

            # move one step ahead and one to the right
            if x + 1 < 8 and np.sign(current_state[x + 1][y + player]) != player and current_state[x + 1][y + player] != 0:
                board = deepcopy(current_state)
                if y + player == 0 or y + player == 7:
                    board[x + 1][y + player] = 6 * player
                else:
                    board[x + 1][y + player] = board[x][y]
                board[x][y] = 0
                if not self.in_check(player, board, depth):
                    possible_states.append(board)
            # move one step ahead and one to the left
            if x - 1 > - 1 and np.sign(current_state[x - 1][y + player]) != player and current_state[x - 1][y + player] != 0:
                board = deepcopy(current_state)
                if y + player == 0 or y + player == 7:
                    board[x - 1][y + player] = 6 * player
                else:
                    board[x - 1][y + player] = board[x][y]
                board[x][y] = 0
                if not self.in_check(player, board, depth):
                    possible_states.append(board)

        return possible_states

    def knight_moves(self, player, x, y, current_state, depth=0):
        possible_states = []
        moves = [[1, 2], [1, -2], [2, 1], [2, -1], [-1, 2], [-1, -2], [-2, 1], [-2, -1]]

        for move in moves:
            d_x = move[0]
            d_y = move[1]
            if -1 < x + d_x < 8 and -1 < y + d_y < 8 and (np.sign(current_state[x + d_x][y + d_y]) != player or current_state[x + d_x][y + d_y] == 0):
                board = deepcopy(current_state)
                board[x + d_x][y + d_y] = board[x][y]
                board[x][y] = 0
                if not self.in_check(player, board, depth):
                    possible_states.append(board)

        return possible_states

    def rook_moves(self, player, x, y, current_state, depth=0):
        possible_states = []

        cant_move_further = False
        for d_x in range(1, 8):
            d_y = 0
            if -1 < x + d_x < 8 and not cant_move_further:

                if current_state[x + d_x][y + d_y] != 0:
                    cant_move_further = True

                if cant_move_further and np.sign(current_state[x + d_x][y + d_y]) == player:
                    continue
                else:
                    board = deepcopy(current_state)
                    board[x + d_x][y + d_y] = board[x][y]
                    board[x][y] = 0
                    if not self.in_check(player, board, depth):
                        possible_states.append(board)

        cant_move_further = False
        for d_x in range(-1, -8, -1):
            d_y = 0
            if -1 < x + d_x < 8 and not cant_move_further:

                if current_state[x + d_x][y + d_y] != 0:
                    cant_move_further = True

                if cant_move_further and np.sign(current_state[x + d_x][y + d_y]) == player:
                    continue
                else:
                    board = deepcopy(current_state)
                    board[x + d_x][y + d_y] = board[x][y]
                    board[x][y] = 0
                    if not self.in_check(player, board, depth):
                        possible_states.append(board)

        cant_move_further = False
        for d_y in range(1, 8):
            d_x = 0
            if -1 < y + d_y < 8 and not cant_move_further:

                if current_state[x + d_x][y + d_y] != 0:
                    cant_move_further = True

                if cant_move_further and np.sign(current_state[x + d_x][y + d_y]) == player:
                    continue
                else:
                    board = deepcopy(current_state)
                    board[x + d_x][y + d_y] = board[x][y]
                    board[x][y] = 0
                    if not self.in_check(player, board, depth):
                        possible_states.append(board)

        cant_move_further = False
        for d_y in range(-1, -8, -1):
            d_x = 0
            if -1 < y + d_y < 8 and not cant_move_further:
                if current_state[x + d_x][y + d_y] != 0:
                    cant_move_further = True

                if cant_move_further and np.sign(current_state[x + d_x][y + d_y]) == player:
                    continue
                else:
                    board = deepcopy(current_state)
                    board[x + d_x][y + d_y] = board[x][y]
                    board[x][y] = 0
                    if not self.in_check(player, board, depth):
                        possible_states.append(board)

        return possible_states

    def bishop_moves(self, player, x, y, current_state, depth = 0):
        possible_states = []

        cant_move_further_pp = False
        cant_move_further_pm = False
        cant_move_further_mp = False
        cant_move_further_mm = False

        for d in range(1, 8):

            pos_x = x + d
            pos_y = y + d
            if -1 < pos_x < 8 and -1 < pos_y < 8:
                if not cant_move_further_pp:
                    board = deepcopy(current_state)
                    if np.sign(current_state[pos_x][pos_y]) == player and current_state[pos_x][pos_y] != 0:
                        cant_move_further_pp = True
                    if not cant_move_further_pp:
                        if np.sign(current_state[pos_x][pos_y]) != player and current_state[pos_x][pos_y] != 0:
                            cant_move_further_pp = True
                        board[pos_x][pos_y] = board[x][y]
                        board[x][y] = 0
                        if not self.in_check(player, board, depth):
                            possible_states.append(board)

            pos_x = x + d
            pos_y = y - d
            if -1 < pos_x < 8 and -1 < pos_y < 8:
                if not cant_move_further_pm:
                    board = deepcopy(current_state)
                    if np.sign(current_state[pos_x][pos_y]) == player and current_state[pos_x][pos_y] != 0:
                        cant_move_further_pm = True
                    if not cant_move_further_pm:
                        if np.sign(current_state[pos_x][pos_y]) != player and current_state[pos_x][pos_y] != 0:
                            cant_move_further_pm = True
                        board[pos_x][pos_y] = board[x][y]
                        board[x][y] = 0
                        if not self.in_check(player, board, depth):
                            possible_states.append(board)

            pos_x = x - d
            pos_y = y - d
            if -1 < pos_x < 8 and -1 < pos_y < 8:
                if not cant_move_further_mm:
                    board = deepcopy(current_state)
                    if np.sign(current_state[pos_x][pos_y]) == player and current_state[pos_x][pos_y] != 0:
                        cant_move_further_mm = True
                    if not cant_move_further_mm:
                        if np.sign(current_state[pos_x][pos_y]) != player and current_state[pos_x][pos_y] != 0:
                            cant_move_further_mm = True
                        board[pos_x][pos_y] = board[x][y]
                        board[x][y] = 0
                        if not self.in_check(player, board, depth):
                            possible_states.append(board)

            pos_x = x - d
            pos_y = y + d
            if -1 < pos_x < 8 and -1 < pos_y < 8:
                if not cant_move_further_mp:
                    board = deepcopy(current_state)
                    if np.sign(current_state[pos_x][pos_y]) == player and current_state[pos_x][pos_y] != 0:
                        cant_move_further_mp = True
                    if not cant_move_further_mp:
                        if np.sign(current_state[pos_x][pos_y]) != player and current_state[pos_x][pos_y] != 0:
                            cant_move_further_mp = True
                        board[pos_x][pos_y] = board[x][y]
                        board[x][y] = 0
                        if not self.in_check(player, board, depth):
                            possible_states.append(board)

        return possible_states

    def queen_moves(self, player, x, y, current_state, depth=0):
        possible_states = []
        possible_states.extend(self.rook_moves(player, x, y, current_state, depth))
        possible_states.extend(self.bishop_moves(player, x, y, current_state, depth))
        if depth == 1:
            t = 5
        return possible_states

    def king_moves(self, player, x, y, current_state, depth=0):

        possible_states = []
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                if d_x == 0 and d_y == 0:
                    continue
                if -1 < x + d_x < 8 and -1 < y + d_y < 8:
                    if np.sign(current_state[x + d_x][y + d_y]) != player or current_state[x + d_x][y + d_y] == 0:
                        board = deepcopy(current_state)
                        board[x + d_x][y + d_y] = board[x][y]
                        board[x][y] = 0
                        if not self.in_check(player, board, depth):
                            possible_states.append(board)

        return possible_states

    def in_check(self, player, current_state, depth):
        if depth > 1:
            return False

        for x in range(0, 8):
            for y in range(0, 8):
                # if current piece is the king check if he is in check
                if current_state[x][y] == 5 * player:
                    possible_enemy_actions = self.get_valid_actions(deepcopy(current_state), -player, depth + 1)
                    for i in range(len(possible_enemy_actions)):
                        if possible_enemy_actions[i][x][y] != 5 * player:
                            return True
        return False
