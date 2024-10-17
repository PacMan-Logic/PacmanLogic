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
        render_mode = None,
        size = 20,
        operation_num = 5,
        categories = 8, # 0:wall 1:empty 2:regular bean 3:bonus bean 4:speed bean 5:magnet bean 6:shield bean 7:*2 bean
        max_time = 3*60,
        pacman = 0, # 玩家
        pacmanskill = 0,
        ghost = True, 
	):
        assert size >= 3
        self.size = size
        self.categories = categories
        self.operation_num = operation_num
        self._last_operation = []
        self._time = max_time
        self._board = boardgenerator(size)
        self._score = [0, 0]

        self._pacman = pacman
        self._pacmanskill = pacmanskill

        self._compete = ghost

        self.start_time = None
        self.max_time = 180 # 最长限时3分钟，后续可修改
        
        self.observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * categories
        ) # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值
        
        self.action_space = spaces.MultiDiscrete([5, 5, 5, 5])
        
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        
    def render(self):
    # TODO(lxy): 修改墙的显示
        if self.render_mode == "local":
            for i in range(self.size):
                for j in range(self.size):
                    if self._board[i][j] == 0:
                        print("\033[1;41m  \033[0m", end="") # 墙：红
                    elif self._board[i][j] == 1:
                        print("\033[1;43m  \033[0m", end="") # 空地：黄
                    elif self._board[i][j] == 2:
                        print("\033[1;44m  \033[0m", end="") # 普通豆子：蓝
                    elif self._board[i][j] == 3:
                        print("\033[1;42m  \033[0m", end="") # 奖励豆子：绿
                    elif self._board[i][j] == 4:
                        print("\033[1;47m  \033[0m", end="") # 速度豆子：白
                    elif self._board[i][j] == 5:
                        print("\033[1;45m  \033[0m", end="") # 磁铁豆子：紫
                    elif self._board[i][j] == 6:
                        print("\033[1;46m  \033[0m", end="") # 护盾豆子：青
                    elif self._board[i][j] == 7:
                        print("\033[1;48m  \033[0m", end="") # *2豆子：灰
                print()
                
        elif self.render_mode == 'logic': # 返回一个字典
            return_dict = {
                "player": self._player,
                "operation": self._last_operation,
                "score": self._score,
                "StopReason": None,
            }
            return return_dict
        
    def _get_info(self):
        return {"score": self._score}
    
    def reset(self, seed=None, board=None):
        self.start_time = time.time()
        super().reset(seed=seed)
        self._last_new = [[]]
        self._last_operation = [[-1],[-1,-1,-1]] # 分别代表吃豆人的行动操作（第一个数）和三个幽灵的行动操作（后三个数）
        self._score = [0, 0]
        self._player = 0
        
        if board is not None:
            self._board = board
            
        if self.render_mode == "logic": # 在逻辑渲染模式下，更新游戏状态的表示
            for i in range(self.size):
                for j in range(self.size):
                    self._last_new[0].append([i, j, int(self._board[i][j])])

    
    def check_time(self):
        current_time = time.time()
        if current_time - self.start_time >= self.max_time:
            return True  # 游戏结束
        else:
            return False

    def observation_space(self):
        return self.observation_space

    def action_space(self):
        return self.action_space
    
    def get_action(self, action): 
        assert len(action) == 4
        pacman = [action[0]]
        ghost = action[1:]
        return pacman, ghost

    # TODO(zyc): def step(self, action, pacman=0, ghost=0):
    # 先判断是否到限制的时间（调用check_time）
    # 判断吃到豆子的情况，修改棋盘状态，判断幽灵和吃豆人的行动是否合法，计算幽灵和吃豆人位置（注意技能）和幽灵和吃豆人相遇情况，计算得分
            
        