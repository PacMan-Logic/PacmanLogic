class Ghost:
    def __init__(self):
        self._coord = [-1, -1]
        self.score = 0

    def coord(self):
        return self._coord

    def set_coord(self, coord):
        self.coord = coord

    def update_score(self, points):
        self.score += points

    def score(self):
        return self.score

    def up(self, board):
        if board[self._coord[0] - 1][self._coord[1]] == 1:
            return False
        self._coord[0] -= 1
        return True

    def down(self, board):
        if board[self._coord[0] + 1][self._coord[1]] == 1:
            return False
        self._coord[0] += 1
        return True

    def left(self, board):
        if board[self._coord[0]][self._coord[1] - 1] == 1:
            return False
        self._coord[1] -= 1
        return True

    def right(self, board):
        if board[self._coord[0]][self._coord[1] + 1] == 1:
            return False
        self._coord[1] += 1
        return True
