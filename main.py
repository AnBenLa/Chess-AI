import sys

import numpy as np
import time
import MonteCarloTree
from Chess import Chess
import random

from copy import copy, deepcopy
from PyQt5 import QtSvg, QtTest
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

current_player = 1

Game = Chess()

board_dimension = 800
offset_x = 50
offset_y = 100
recursive_enemy = True
recursive_max_depth = 3


def recursive_evaluation(current_state, original_player, current_player, depth = 1):
    if Game.finished(current_state, current_player):
        print('Game finished')
        if depth == 1:
            return Move(-1, -1, -1, -1)
        return Game.reward(current_state, original_player) * 100

    if depth > recursive_max_depth:
        difference = 0
        for x in range(0, 8):
            for y in range(0, 8):
                if np.sign(current_state[x][y]) == original_player and current_state[x][y] != 0:
                    difference += np.abs(current_state[x][y])
                elif current_state[x][y] != 0:
                    difference -= np.abs(current_state[x][y])

        return difference

    valid_moves = Game.get_valid_actions(current_state, current_player)
    move_grading = []
    max_grading = -10000
    max_index = 0
    total_grading = 0

    for i in range(len(valid_moves)):
        grading = recursive_evaluation(valid_moves[i], original_player, -current_player, depth + 1)
        move_grading.append(grading)
        total_grading += move_grading[i]
        if move_grading[i] > max_grading:
            max_grading = move_grading[i]
            max_index = i
        elif move_grading[i] == max_grading:
            p = random.randint(0, 100)
            if p > 80:
                max_grading = move_grading[i]
                max_index = i

    if depth == 1:
        original_position_x = -1
        original_position_y = -1
        new_position_x = -1
        new_position_y = -1
        print('Move grading: ', move_grading)
        for x in range(0, 8):
            for y in range(0, 8):
                if current_state[x][y] != valid_moves[max_index][x][y]:
                    if valid_moves[max_index][x][y] == 0:
                        original_position_x = x
                        original_position_y = y
                    else:
                        new_position_x = x
                        new_position_y = y
        return Move(original_position_x, original_position_y, new_position_x, new_position_y)

    else:
        return total_grading


class Move:
    def __init__(self, x, y, x_new, y_new):
        self.x = x
        self.y = y
        self.x_new = x_new
        self.y_new = y_new

    def execute_move(self):
        global Game
        global current_player

        new_board = deepcopy(Game.get_board())
        new_board[self.x_new][self.y_new] = new_board[self.x][self.y]
        new_board[self.x][self.y] = 0

        Game.set_board(new_board)
        current_player *= -1


class DragFigure(QSvgWidget):
    def __init__(self, source):
        super().__init__(source)
        self.figure_size = int(board_dimension/8)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        self.start_x = self.x()
        self.start_y = self.y()

        super(DragFigure, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(DragFigure, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            goal = event.globalPos()

            x = int((self.start_x - offset_x) / self.figure_size)
            y = int((self.start_y - offset_y) / self.figure_size)

            x_new = int(np.floor((goal.x() - offset_x) / self.figure_size))
            y_new = int(np.floor((goal.y() - offset_y) / self.figure_size))

            move = Move(x, y, x_new, y_new)

            valid_moves = Game.get_valid_actions(Game.get_board(), current_player)

            new_board = deepcopy(Game.get_board())
            new_board[x_new][y_new] = Game.get_board()[x][y]
            new_board[x][y] = 0

            valid_move = False
            for action in valid_moves:
                if action == new_board:
                    print('Valid Move!')
                    valid_move = True

            if valid_move:
                current_board = Game.get_board()
                goal_value = current_board[move.x_new][move.y_new]
                goal_position = QPoint(move.x_new * self.figure_size + offset_x, move.y_new * self.figure_size + offset_y)
                if np.sign(goal_value) != current_player and goal_value != 0:
                    tmp = self.parent().parent().figures
                    tmp[move.x_new][move.y_new].move(-10000, -1000)
                    print('Removed piece on new position')
                    #removed_piece = self.parent().childAt(goal_position)
                    #removed_piece.move(-10000, -1000)

                move.execute_move()

                self.setGeometry(goal_position.x(), goal_position.y(), self.figure_size, self.figure_size)

                tmp = self.parent().parent().figures
                tmp[move.x_new][move.y_new] = tmp[move.x][move.y]
                tmp[move.x][move.y] = 0

                print('Set new piece on new position')
                if current_player == 1:
                    self.parent().childAt(QPoint(board_dimension + offset_x + 50, offset_y)).setText('Current player: White')
                else:
                    self.parent().childAt(QPoint(board_dimension + offset_x + 50, offset_y)).setText('Current player: Red')

            else:
                self.setGeometry(self.start_x, self.start_y, self.figure_size, self.figure_size)
                print('Invalid move!')

            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragFigure, self).mouseReleaseEvent(event)


class ChessWindow(QMainWindow):
    def __init__(self, windowsize):
        super().__init__()
        self.windowsize = windowsize
        self.figure_size = int(board_dimension/8)
        self.chessboard = QSvgWidget('images/Chess_Board.svg')
        self.text = QLabel()
        self.pc_enemy_text = QLabel()
        self.figures = [[0]*8 for i in range(8)]
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.recursive_enemy)
        self.timer.start(1000)

    def initUI(self):
        self.setFixedSize(self.windowsize)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)

        widget = QWidget()
        self.setCentralWidget(widget)

        if current_player == 1:
            self.text.setText('Current player: White')
        else:
            self.text.setText('Current player: Red')


        self.text.setFont(QFont('SansSerif', 30))
        self.text.setGeometry(QRect(board_dimension + offset_x + 50, offset_y, 500, 100))
        self.text.setParent(widget)

        if recursive_enemy:
            self.pc_enemy_text.setText('PC Enemy: ON')
            self.pc_enemy_text.setFont(QFont('SansSerif', 30))
            self.pc_enemy_text.setGeometry(QRect(board_dimension + offset_x + 50, offset_y + 50, 500, 100))

        self.pc_enemy_text.setParent(widget)

        self.chessboard.setGeometry(offset_x, offset_y, board_dimension, board_dimension)
        self.chessboard.setParent(widget)

        for x in range(0, 8):
            for y in range(0, 8):
                red_color = QGraphicsColorizeEffect()
                red_color.setColor(QColor(255, 0, 0))
                found = False
                # pawns
                if abs(Game.get_board()[x][y]) == 1:
                    new_figure = DragFigure('images/Chess_plt45.svg')
                    found = True
                # towers
                elif abs(Game.get_board()[x][y]) == 2:
                    new_figure = DragFigure('images/Chess_rlt45.svg')
                    found = True
                # rooks
                elif abs(Game.get_board()[x][y]) == 3:
                    new_figure = DragFigure('images/Chess_nlt45.svg')
                    found = True
                # bishops
                elif abs(Game.get_board()[x][y]) == 4:
                    new_figure = DragFigure('images/Chess_blt45.svg')
                    found = True
                # kings
                elif abs(Game.get_board()[x][y]) == 5:
                    new_figure = DragFigure('images/Chess_klt45.svg')
                    found = True
                # queens
                elif abs(Game.get_board()[x][y]) == 6:
                    new_figure = DragFigure('images/Chess_qlt45.svg')
                    found = True

                if found:
                    if Game.get_board()[x][y] < 0:
                        new_figure.setGraphicsEffect(red_color)
                    self.figures[x][y] = new_figure
                    new_figure.setGeometry(x * self.figure_size + offset_x, y * self.figure_size + offset_y, self.figure_size, self.figure_size)
                    new_figure.setParent(widget)

    def recursive_enemy(self):
        if not Game.finished(Game.get_board(), current_player):
            if current_player == -1:
                if recursive_enemy:
                    if not Game.finished(Game.get_board(), current_player):
                        print('Evaluating best move')
                        best_move = recursive_evaluation(Game.get_board(), current_player, current_player)
                        print('Best move found')
                        self.move_figure(best_move)
                    else:
                        self.pc_enemy_text.setText('Game finished!')
                        print('Game finished!')

    def move_figure(self, move):
        global current_player
        global Game

        if -1 < move.x < 8 and -1 < move.y < 8 and -1 < move.x_new < 8 and -1 < move.y_new < 8:
            valid_moves = Game.get_valid_actions(Game.get_board(), current_player)

            new_board = deepcopy(Game.get_board())
            new_board[move.x_new][move.y_new] = Game.get_board()[move.x][move.y]
            new_board[move.x][move.y] = 0

            valid_move = False
            for action in valid_moves:
                if action == new_board:
                    print('Valid Move!')
                    valid_move = True

            if valid_move:
                goal_value = Game.get_board()[move.x_new][move.y_new]
                goal_position = QPoint(move.x_new * self.figure_size + offset_x, move.y_new * self.figure_size + offset_y)
                if np.sign(goal_value) != current_player and goal_value != 0:
                    self.figures[move.x_new][move.y_new].move(-10000, -1000)
                    #self.parent().childAt(goal_position).move(-10000, -1000)

                move.execute_move()

                self.figures[move.x][move.y].setGeometry(goal_position.x(), goal_position.y(), self.figure_size, self.figure_size)

                self.figures[move.x_new][move.y_new] = self.figures[move.x][move.y]
                self.figures[move.x][move.y] = 0

                if current_player == 1:
                    self.centralWidget().childAt(QPoint(board_dimension + offset_x + 50, offset_y)).setText('Current player: White')
                else:
                    self.centralWidget().childAt(QPoint(board_dimension + offset_x + 50, offset_y)).setText('Current player: Red')
        else:
            print('Invalid move!')

#def iteration(game):
    #network = None
    #examples = []
    #for i in range(iteration_count):
    #    for e in range(episode_count):
    #        examples += execute_episode(game, network)
    #    new_network = train_network(examples)
    #    frac_win = pit(new_network, network)
    #    if frac_win > threshold:
    #        network = new_network
    #return  network


#def execute_episode(game, network):
#    examples = []
#    state = game.start_state()
#    tree = MonteCarloTree(board, Chess(), network)
#
#    while True:
#        for _ in range (tree_search_simulation_count):
#            tree.find_best_action(state, current_player,  c)
#        examples.append([state, tree.pi(s), None])
#        a=

def main():
    # todo network definition
    network = None




    global board_dimension
    global offset_x
    global offset_y

    # create PyQt application
    app = QApplication(sys.argv)
    screensize = app.desktop().availableGeometry().size()

    # fit the chessboard to the available screen window size
    y = screensize.height()
    x = screensize.width()
    min_dim = np.minimum(x, y)
    board_dimension = int(min_dim - 0.1 * min_dim)
    board_dimension = board_dimension - (board_dimension % 80)
    if min_dim == y:
        offset_y = int(0.05 * min_dim)
        offset_x = int((x - board_dimension)/2)
    else:
        offset_x = int(0.05 * min_dim)
        offset_y = int((y - board_dimension)/2)
    print(board_dimension, offset_x, offset_y, board_dimension/8)

    # initialize chess window
    window = ChessWindow(screensize)
    window.show()
    # wait and execute figure move
    #QtTest.QTest.qWait(2000)
    #move = Move(1, 1, 1, 2)
    #window.move_figure(move)


    # exist if window is closed
    sys.exit(app.exec_())


def out_of_bounds(move):
    return move.x > 7 or move.x < 0 or move.y > 7 or move.y < 0 or move.x_new > 7 or move.x_new < 0 or move.y_new > 7 or move.y_new < 0


def validate_move(player, move):
    if out_of_bounds(move):
        return False
    # todo scharade?
    global Game
    global current_player

    piece = Game.get_board()[move.x][move.y]
    goal = Game.get_board()[move.x_new][move.y_new]

    allowed_move = False
    if np.sign(piece) == player and (np.sign(goal) != player or goal == 0):

        # test if currently in check
        check = in_check(player)

        if abs(piece) == 1:
            allowed_move = pawn_move(player, move)
        elif abs(piece) == 2:
            allowed_move = rook_move(player, move)
        elif abs(piece) == 3:
            allowed_move = knight_move(player, move)
        elif abs(piece) == 4:
            allowed_move = bishop_move(player, move)
        elif abs(piece) == 5:
            allowed_move = king_move(player, move)
        elif abs(piece) == 6:
            allowed_move = queen_move(player, move)

        if check and allowed_move:
            # check if still in check after move
            still_check = in_check(player)
            if still_check:
                return False

    return allowed_move


def in_check(player):
    # check if in check

    return False


def pawn_move(player, move):
    diff_x = move.x_new - move.x
    diff_y = move.y_new - move.y

    if (move.x == move.x_new and move.y_new - move.y == player and Game.get_board()[move.x_new][move.y_new] == 0) or \
            (np.absolute(move.y - move.y_new) == 1 and move.x_new - move.x == player and \
             np.sign(Game.get_board()[move.x_new][move.y_new]) == -player):
        return True
    else:
        return False


def knight_move(player, move):
    diff_x = move.x_new - move.x
    diff_y = move.y_new - move.y
    if (abs(diff_x) == 2 and abs(diff_y) == 1) or (abs(diff_y) == 2 and abs(diff_x) == 1):
        if Game.get_board()[move.x_new][move.y_new] == 0 or np.sign(Game.get_board()[move.x_new][move.y_new]) != player:
            return True
    return False


def rook_move(player, move):
    diff_x = move.x_new - move.x
    diff_y = move.y_new - move.y
    if diff_x == 0 or diff_y == 0:
        x = np.sign(diff_x)
        y = np.sign(diff_y)
        if diff_x != 0:
            for i in range(1, abs(diff_x)):
                if Game.get_board()[move.x + i * x][move.y] != 0:
                    return False
        if diff_y != 0:
            for i in range(1, abs(diff_y)):
                if Game.get_board()[move.x][move.y + i * y] != 0:
                    return False
        if Game.get_board()[move.x_new][move.y_new] == 0 or np.sign(Game.get_board()[move.x_new][move.y_new]) != player:
            return True
    return False


def bishop_move(player, move):
    diff_x = move.x_new - move.x
    diff_y = move.y_new - move.y
    if abs(diff_x) == abs(diff_y) and diff_x != 0:
        x = np.sign(diff_x)
        y = np.sign(diff_y)
        for i in range(1, abs(diff_x)):
            if Game.get_board()[move.x + i * x][move.y + i * y] != 0:
                return False
        if Game.get_board()[move.x_new][move.y_new] == 0 or np.sign(Game.get_board()[move.x_new][move.y_new]) != player:
            return True
    return False


def queen_move(player, move):
    diff_x = move.x_new - move.x
    diff_y = move.y_new - move.y
    if abs(diff_x) < 2 and abs(diff_y) < 2 and (diff_x != 0 or diff_y != 0):
        if Game.get_board()[move.x_new][move.y_new] == 0 or np.sign(Game.get_board()[move.x_new][move.y_new]) != player:
            return True

    return False


def king_move(player, move):
    diff_x = move.x_new - move.x
    diff_y = move.y_new - move.y
    if abs(diff_x) < 2 and abs(diff_y) < 2 and (diff_x != 0 or diff_y != 0):
        if Game.get_board()[move.x_new][move.y_new] == 0 or np.sign(Game.get_board()[move.x_new][move.y_new]) != player:
            return True
    return False


if __name__ == '__main__':
    main()
