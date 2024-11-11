from .gamedata import *


class Pacman:
    def __init__(
        self,
        score=0,
        double_score=0,
        speed_up=0,
        magnet=0,  # Note: the remaining rounds of magnet
        shield=0,  # Note: the number of shield
        x=-1,
        y=-1,
    ):
        self._score = score
        self._skill_status = [double_score, speed_up, magnet, shield]
        self._coord = [x, y]

    def update_score(self, points):
        if self._skill_status[Skill.DOUBLE_SCORE.value] == 0:
            self._score += points
        else:
            self._score += points * 2

    def just_eat(self, board, x, y):
        if board[x][y] == Space.REGULAR_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.update_score(1)

        elif board[x][y] == Space.BONUS_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.update_score(2)

        elif board[x][y] == Space.SPEED_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.SPEED_UP)

        elif board[x][y] == Space.MAGNET_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.MAGNET)

        elif board[x][y] == Space.SHIELD_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.SHIELD)

        elif board[x][y] == Space.DOUBLE_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.DOUBLE_SCORE)

    def eat_bean(self, board):
        x, y = self._coord
        if self._skill_status[Skill.MAGNET.value] == 0:
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

    def get_coord(self):
        return self._coord.copy()

    def set_coord(self, coord):
        self._coord = coord

    def get_skills_status(self):
        return self._skill_status.copy()

    def acquire_skill(self, skill_index: Skill):
        if skill_index == Skill.SHIELD:
            self._skill_status[Skill.SHIELD.value] += 1
        else:
            self._skill_status[skill_index.value] = DEFAULT_SKILL_TIME[
                skill_index.value
            ]

    def new_round(self):  # Note: reset the skill status when a new round starts
        if self._skill_status[Skill.DOUBLE_SCORE.value] > 0:
            self._skill_status[Skill.DOUBLE_SCORE.value] -= 1
        if self._skill_status[Skill.MAGNET.value] > 0:
            self._skill_status[Skill.MAGNET.value] -= 1
        if self._skill_status[Skill.SPEED_UP.value] > 0:
            self._skill_status[Skill.SPEED_UP.value] -= 1

    def get_score(self):
        return self._score

    def encounter_ghost(self):
        if self._skill_status[Skill.SHIELD.value] > 0:
            self._skill_status[Skill.SHIELD.value] -= 1
            return False
        else:
            return True

    def up(self, board):
        if board[self._coord[0] - 1][self._coord[1]] != Space.WALL.value:
            self._coord[0] -= 1
            return True
        else:
            return False

    def down(self, board):
        if board[self._coord[0] + 1][self._coord[1]] != Space.WALL.value:
            self._coord[0] += 1
            return True
        else:
            return False

    def left(self, board):
        if board[self._coord[0]][self._coord[1] - 1] != Space.WALL.value:
            self._coord[1] -= 1
            return True
        else:
            return False

    def right(self, board):
        if board[self._coord[0]][self._coord[1] + 1] != Space.WALL.value:
            self._coord[1] += 1
            return True
        else:
            return False

    def reset(self):
        self._skill_status = [0, 0, 0, 0]
