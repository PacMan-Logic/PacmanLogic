# Note: double_score: 0, speed_up: 1, magnet: 2
DEFAULT_SKILL_TIME = [10, 10, 10]


class Pacman:
    def __init__(
        self,
        id=0,
        score=0,
        double_score=0,
        speed_up=0,
        magnet=0,  # Note: the remaining rounds of magnet
        shield=0,  # Note: the number of shield
        x=-1,
        y=-1,
    ):
        self.id = id  # FIXME: how should it be used?
        self.score = score
        self.skill_status = [double_score, speed_up, magnet, shield]
        self.coord = [x, y]

    def update_score(self, points):
        if self.double_score:
            self.score += points * 2
        else:
            self.score += points

    def just_eat(self, board, x, y):
        if board[x][y] == 2:
            self.update_score(1)
            board[x][y] = 1
        elif board[self.x][self.y] == 3:
            self.update_score(2)
            board[x][y] = 1
        elif board[x][y] == 4:
            self.acquire_skill(1)
            board[x][y] = 1
        elif board[x][y] == 5:
            self.acquire_skill(2)
            board[x][y] = 1
        elif board[x][y] == 6:
            self.acquire_skill(3)
            board[x][y] = 1
        elif board[x][y] == 7:
            self.acquire_skill(0)
            board[x][y] = 1

    def eat_bean(self, board):
        x, y = self.coord
        if not self.magnet:
            self.just_eat(board, x, y)

        else:
            self.just_eat(board, x, y)
            self.just_eat(board, x - 1, y - 1)
            self.just_eat(board, x - 1, y)
            self.just_eat(board, x - 1, y + 1)
            self.just_eat(board, x, y - 1)
            self.just_eat(board, x, y + 1)
            self.just_eat(board, x + 1, y - 1)
            self.just_eat(board, x + 1, y)
            self.just_eat(board, x + 1, y + 1)

    # 判断pacman是否撞墙，是否与ghost相遇的部分应该放在main函数中实现

    def coord(self):
        return self.coord

    def set_coord(self, coord):
        self.coord = coord

    def get_skills_status(self):
        return self.skill_status

    def acquire_skill(self, skill_index: int):
        if skill_index > 2:
            raise ValueError("Invalid skill index")
        self.skill_status[skill_index] = DEFAULT_SKILL_TIME[skill_index]

    def new_round(self):
        if self.skill_status[0] > 0:
            self.skill_status[0] -= 1
        if self.skill_status[1] > 0:
            self.skill_status[1] -= 1
        if self.skill_status[2] > 0:
            self.skill_status[2] -= 1

    def score(self):
        return self.score

    def encounter_ghost(self):
        if self.skill_status[3] > 0:
            self.skill_status[3] -= 1
            return False
        else:
            return True

    def up(self, board):
        if board[self.coord[0] - 1][self.coord[1]] != 0:
            self.coord[0] -= 1
            return True
        else:
            return False

    def down(self, board):
        if board[self.coord[0] + 1][self.coord[1]] != 0:
            self.coord[0] += 1
            return True
        else:
            return False

    def left(self, board):
        if board[self.coord[0]][self.coord[1] - 1] != 0:
            self.coord[1] -= 1
            return True
        else:
            return False

    def right(self, board):
        if board[self.coord[0]][self.coord[1] + 1] != 0:
            self.coord[1] += 1
            return True
        else:
            return False
