from .gamedata import *


class Ghost:
    def __init__(self):
        self._coord = [-1, -1]
        self._score = 0

    def get_coord(self):
        return self._coord.copy()

    def set_coord(self, coord):
        self._coord = coord

    def update_score(self, points):
        self._score += points

    def get_score(self):
        return self._score

    def up(self, board):
        if board[self._coord[0] - 1][self._coord[1]] == Space.WALL.value:
            return False
        self._coord[0] -= 1
        return True

    def down(self, board):
        if board[self._coord[0] + 1][self._coord[1]] == Space.WALL.value:
            return False
        self._coord[0] += 1
        return True

    def left(self, board):
        if board[self._coord[0]][self._coord[1] - 1] == Space.WALL.value:
            return False
        self._coord[1] -= 1
        return True

    def right(self, board):
        if board[self._coord[0]][self._coord[1] + 1] == Space.WALL.value:
            return False
        self._coord[1] += 1
        return True

    def update_score(self, points):
        self._score += points

