import json
import time
from typing import List

import gym
import numpy as np
from gym import spaces
from .board import boardgenerator
from .pacman import Pacman
from .ghost import Ghost

from .gamedata import *
# from ghost import Ghost


class PacmanEnv(gym.Env):
    metadata = {"render_modes": ["local", "logic", "ai"]}

    def __init__(
        self,
        render_mode=None,
        size=20,
    ):
        assert size >= 3
        self.size = size

        # Note: use round instead of time to terminate the game
        self.round = 0

        self.board = [boardgenerator(size)]

        self.pacman = Pacman()
        self.ghosts = [Ghost(), Ghost(), Ghost()]

        self._last_skill_status = [0] * SKILL_NUM

        self.start_time = None
        self.max_time = 180  # 最长限时3分钟，后续可修改

        self._level = 1

        # store runtime details for rendering
        self._last_operation = []
        self._pacman_step_block = []
        self._ghosts_step_block = []

        self.observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * SPACE_CATEGORY
        )  # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值

        self.pacman_action_space = spaces.Discrete(OPERATION_NUM)
        self.ghost_action_space = spaces.MultiDiscrete(np.ones(3) * OPERATION_NUM)
        # 这段代码定义了环境的动作空间。在训练过程中，吃豆人和幽灵应该索取不同的动作空间

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    # return the current state of the game
    def render(self):
        # TODO(lxy): 修改墙的显示
        if self.render_mode == "local":
            for i in range(self.size):
                for j in range(self.size):
                    if self.board[i][j] == 0:
                        print("\033[1;41m  \033[0m", end="")  # 墙：红
                    elif self.board[i][j] == 1:
                        print("\033[1;43m  \033[0m", end="")  # 空地：黄
                    elif self.board[i][j] == 2:
                        print("\033[1;44m  \033[0m", end="")  # 普通豆子：蓝
                    elif self.board[i][j] == 3:
                        print("\033[1;42m  \033[0m", end="")  # 奖励豆子：绿
                    elif self.board[i][j] == 4:
                        print("\033[1;47m  \033[0m", end="")  # 速度豆子：白
                    elif self.board[i][j] == 5:
                        print("\033[1;45m  \033[0m", end="")  # 磁铁豆子：紫
                    elif self.board[i][j] == 6:
                        print("\033[1;46m  \033[0m", end="")  # 护盾豆子：青
                    elif self.board[i][j] == 7:
                        print("\033[1;48m  \033[0m", end="")  # *2豆子：灰
                    elif self.board[i][j] == 8:
                        print("\033[48;5;27m  \033[0m", end="")  # 传送门
                print()

        elif self.render_mode == "logic":  # 返回一个字典
            return_dict = {
                "player": self._player,
                "ghosts_step_block": self._ghosts_step_block,
                "pacman_step_block": self._pacman_step_block,
                "pacman_skills": self._last_skill_status,
                # Note: 播放器需要根据是否有magnet属性确定每次移动的时候需要如何吸取豆子
                "round": self._round,
                "score": self._score,
                "level": self._level,
                "StopReason": None,
            }
            return return_dict

    # training utils
    def observation_space(self):
        return self.observation_space

    def pacman_action_space(self):
        return self.pacman_action_space

    def ghost_action_space(self):
        return self.ghost_action_space

    # TODO: 重写reset函数（lxy）
    def reset(self, seed=None, board=None):
        self.pacman.coord = [0,0]
        self.ghosts[0].coord = [2,2]
        self.ghosts[1].coord = [2,2]
        self.ghosts[2].coord = [2,2] # wxt: 我随便写的，方便调试
        if self._level == 1:  # 如果刚开始玩游戏,那就全要初始化
            self.start_time = time.time()
            self._round = 0
            super().reset(seed=seed)
            self._last_new = [[]]
            self._last_operation = [
                [-1],
                [-1, -1, -1],
            ]  # 分别代表吃豆人的行动操作（第一个数）和三个幽灵的行动操作（后三个数）
            self._score = [0, 0]
            self._player = 0

        if board is not None:
            self.board = board
        else:
            self.board = boardgenerator(self.size)

        if self.render_mode == "logic":  # 在逻辑渲染模式下，更新游戏状态的表示
            for i in range(self.size):
                for j in range(self.size):
                    self._last_new[0].append([i, j, int(self.board[i][j])])

    # step utils
    def check_round_end(self):
        return self._round >= MAX_ROUND

    def get_action(self, action):
        assert len(action) == 4
        pacman = [action[0]]
        ghost = action[1:]
        return pacman, ghost

    def num_to_coord(self, num):
        return num // self.size, num % self.size

    def step(self, pacmanAction: int, ghostAction: List[int]):
        self._last_operation = []
        self._ghosts_step_block = [[], [], []]
        self._pacman_step_block = []

        self._last_skill_status = self.pacman.get_skills_status()
        self._last_operation = [pacmanAction, ghostAction]

        pacman_skills = self.pacman.get_skills_status()
        pacman_coord = self.pacman.get_coord()
        ghost_coords = [ghost.get_coord() for ghost in self.ghosts]

        # pacman move
        # Note: double_score: 0, speed_up: 1, magnet: 2, shield: 3
        self._pacman_step_block.append(pacman_coord)
        for i in range(3):
            self._ghosts_step_block[i].append(ghost_coords[i])

        if pacman_skills[1] > 0:
            if pacmanAction == 0:
                self.pacman.eat_bean(self.board)
            elif pacmanAction == 1:  # 向上移动
                self.pacman.eat_bean(self.board)
                if self.pacman.up(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
                if self.pacman.up(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            elif pacmanAction == 2:  # 向左移动
                self.pacman.eat_bean(self.board)
                if self.pacman.left(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
                if self.pacman.left(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            elif pacmanAction == 3:  # 向下移动
                self.pacman.eat_bean(self.board)
                if self.pacman.down(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
                if self.pacman.down(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            elif pacmanAction == 4:  # 向右移动
                self.pacman.eat_bean(self.board)
                if self.pacman.right(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
                if self.pacman.right(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            else:  # 退出程序
                raise ValueError("Invalid action number of speedy pacman")
        else:
            if pacmanAction == 0:
                self.pacman.eat_bean(self.board)
            elif pacmanAction == 1:
                self.pacman.eat_bean(self.board)
                if self.pacman.up(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            elif pacmanAction == 2:
                self.pacman.eat_bean(self.board)
                if self.pacman.left(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            elif pacmanAction == 3:
                self.pacman.eat_bean(self.board)
                if self.pacman.down(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            elif pacmanAction == 4:
                self.pacman.eat_bean(self.board)
                if self.pacman.right(self.board):
                    self._pacman_step_block.append(self.pacman.coord)
            else:
                raise ValueError("Invalid action number of normal pacman")

        # ghost move
        for i in range(3):
            if ghostAction[i] == 0:
                pass
            elif ghostAction[i] == 1:
                self.ghosts[i].up(self.board)
                self._ghosts_step_block[i].append(self.ghosts[i].coord)
            elif ghostAction[i] == 2:
                self.ghosts[i].left(self.board)
                self._ghosts_step_block[i].append(self.ghosts[i].coord)
            elif ghostAction[i] == 3:
                self.ghosts[i].down(self.board)
                self._ghosts_step_block[i].append(self.ghosts[i].coord)
            elif ghostAction[i] == 4:
                self.ghosts[i].right(self.board)
                self._ghosts_step_block[i].append(self.ghosts[i].coord)
            else:
                raise ValueError("Invalid action of ghost")

        # check if ghosts caught pacman
        # TODO: specialize return value when respawning
        for i in self._pacman_step_block[1:]:
            for j in self._ghosts_step_block:
                if i == j[-1]:
                    if self.pacman.encounter_ghost():
                        self.ghosts[i].update_score(DESTORY_PACMAN_SHIELD) # TODO: update_score
                    else:
                        self.pacman.update_score(EATEN_BY_GHOST)
                        self.ghosts[i].update_score(EAT_PACMAN)
                        self.pacman.set_coord(self.find_distant_emptyspace())

        # notice! its a new round
        self.round += 1
        self.pacman.new_round()

        # check if the game is over
        count_remain_beans = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 2 | 3:
                    count_remain_beans += 1
        if count_remain_beans == 0:
            self.pacman.update_score(
                EAT_ALL_BEANS + (MAX_ROUND - self.round) * ROUND_BONUS_GAMMA
            )
            return (
                self.board,
                [self.pacman_score, self.ghosts_score],
                True,
            )  # true means game over

        if self.round >= MAX_ROUND:
            for i in self.ghosts:
                i.update_score(PREVENT_PACMAN_EAT_ALL_BEANS)
            return self.board, [self.pacman_score, self.ghosts_score], True

        return self.board, [self.pacman_score, self.ghosts_score], False

    def pacman_score(self):
        return self.pacman.score

    def ghosts_score(self):
        ghost_scores = [ghost.score for ghost in self.ghosts]
        return sum(ghost_scores)

    # in case of respawn just beside the ghosts, find a distant empty space
    def find_distant_emptyspace(self):
        coord = []
        max = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 1:
                    sum = 0
                    for i in self.ghosts:
                        sum += abs(i.coord[0] - i) + abs(i.coord[1] - j)
                    if max > sum:
                        max = sum
                        coord = [i, j]
        if coord == []:
            raise ValueError("No empty space found")
        return coord
    
    def next_level(self):
        self._level += 1
        if self._level > MAX_LEVEL:
            return True
        return False