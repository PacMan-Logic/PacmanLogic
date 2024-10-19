import json
import time

import gym
import numpy as np
from gym import spaces
from board import boardgenerator


class PacmanEnv(gym.Env):
    metadata = {"render_modes": ["local", "logic", "ai"]}

    def __init__(
        self,
        render_mode=None,
        size=20,
        operation_num=5,
        categories=9,  # 0:wall 1:empty 2:regular bean 3:bonus bean 4:speed bean 5:magnet bean 6:shield bean 7:*2 bean 8:portal
        max_rounds=3 * 60,  # Fixme: it should be updated
        pacman=0,  # 玩家
        pacmanskill=0,
        ghost=True,
    ):
        assert size >= 3
        self.size = size
        self.categories = categories
        self.operation_num = operation_num

        # Note: use round instead of time to terminate the game
        self._round = 0
        self._max_rounds = max_rounds

        self._board = boardgenerator(size)
        self._score = [0, 0]

        self._pacman = pacman
        self._pacmanskill = pacmanskill

        self._compete = ghost

        self.start_time = None
        self.max_time = 180  # 最长限时3分钟，后续可修改
        
        # store runtime details for rendering
        self._last_operation = []
        self._pacman_step_block = []
        self._ghost_step_block = []

        self.observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * categories
        )  # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值

        self.pacman_action_space = spaces.Discrete(operation_num)
        self.ghost_action_space = spaces.MultiDiscrete(np.ones(3) * operation_num)
        # 这段代码定义了环境的动作空间。在训练过程中，吃豆人和幽灵应该索取不同的动作空间

        self.pacman_coord = [self.size / 2, self.size / 2]
        self.ghost_coord = [[0, 0], [self.size - 1, 0], [0, self.size - 1]]

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    # return the current state of the game
    def render(self):
        # TODO(lxy): 修改墙的显示
        if self.render_mode == "local":
            for i in range(self.size):
                for j in range(self.size):
                    if self._board[i][j] == 0:
                        print("\033[1;41m  \033[0m", end="")  # 墙：红
                    elif self._board[i][j] == 1:
                        print("\033[1;43m  \033[0m", end="")  # 空地：黄
                    elif self._board[i][j] == 2:
                        print("\033[1;44m  \033[0m", end="")  # 普通豆子：蓝
                    elif self._board[i][j] == 3:
                        print("\033[1;42m  \033[0m", end="")  # 奖励豆子：绿
                    elif self._board[i][j] == 4:
                        print("\033[1;47m  \033[0m", end="")  # 速度豆子：白
                    elif self._board[i][j] == 5:
                        print("\033[1;45m  \033[0m", end="")  # 磁铁豆子：紫
                    elif self._board[i][j] == 6:
                        print("\033[1;46m  \033[0m", end="")  # 护盾豆子：青
                    elif self._board[i][j] == 7:
                        print("\033[1;48m  \033[0m", end="")  # *2豆子：灰
                    elif self._board[i][j] == 8:
                        print("\033[48;5;27m  \033[0m", end="")  # 传送门
                print()

        elif self.render_mode == "logic":  # 返回一个字典
            return_dict = {
                "player": self._player,
                "operation": self._last_operation,
                "score": self._score,
                "StopReason": None,
            }
            return return_dict

    def _get_info(self):
        return {"score": self._score}

    # training utils
    def observation_space(self):
        return self.observation_space

    def pacman_action_space(self):
        return self.pacman_action_space

    def ghost_action_space(self):
        return self.ghost_action_space

    def reset(self, seed=None, board=None):
        super().reset(seed=seed)
        self._last_new = [[]]
        self._last_operation = [
            [-1],
            [-1, -1, -1],
        ]  # 分别代表吃豆人的行动操作（第一个数）和三个幽灵的行动操作（后三个数）
        self._score = [0, 0]
        self._player = 0

        if board is not None:
            self._board = board

        if self.render_mode == "logic":  # 在逻辑渲染模式下，更新游戏状态的表示
            for i in range(self.size):
                for j in range(self.size):
                    self._last_new[0].append([i, j, int(self._board[i][j])])

    # step utils
    def check_round_end(self):
        return self._round >= self._max_rounds

    def get_action(self, action):
        assert len(action) == 4
        pacman = [action[0]]
        ghost = action[1:]
        return pacman, ghost

    def num_to_coord(self, num):
        return num // self.size, num % self.size

    def step(self, PacManAction, GhostAction):
        self._last_operation = []
