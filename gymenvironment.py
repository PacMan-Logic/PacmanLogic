import json
import time

import gym
import numpy as np
from gym import spaces

class PacmanEnv(gym.Env):
    metadata = {"render_modes": ["local", "logic", "ai"]}
    
    def __init__(
        self,
        render_mode = None,
        size = 40,
        categories = 9, # 1. empty, 2. wall, 3. regular bean, 4. bonus bean, 5. speed bean, 6. magnet bean, 7. *2 bean 8. pacman 9. ghost
        max_time = 3*60,
        player = 0, # 玩家
        compete = True, # 两个玩家将交替进行游戏，每个玩家的得分将被单独计算。如果为False，那么只有一个玩家进行游戏。默认值为True。       
	):
        assert size >= 3
        self.size = size
        self.categories = categories
        self._last_operation = []
        self._time = max_time
        self._board = None
        self._score = [0, 0]
        self._player = player
        self._compete = compete
        
        self.observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * categories
        ) # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值
        
        self.action_space = spaces.Discrete(5) # W S A D 和不动
        
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        
    def render(self):
        if self.render_mode == "local":
            for i in range(self.size):
                for j in range(self.size):
                    if self._board[i][j] == 0:
                        print("\033[1;41m  \033[0m", end="")
                    elif self._board[i][j] == 1:
                        print("\033[1;43m  \033[0m", end="")
                    elif self._board[i][j] == 2:
                        print("\033[1;44m  \033[0m", end="")
                    elif self._board[i][j] == 3:
                        print("\033[1;42m  \033[0m", end="")
                    elif self._board[i][j] == 4:
                        print("\033[1;47m  \033[0m", end="")
                    elif self._board[i][j] == 5:
                        print("\033[1;45m  \033[0m", end="")
                    elif self._board[i][j] == 6:
                        print("\033[1;46m  \033[0m", end="")
                    elif self._board[i][j] == 7:
                        print("\033[1;48m  \033[0m", end="")
                    elif self._board[i][j] == 8:
                        print("\033[1;49m  \033[0m", end="")
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
        super().reset(seed=seed)
        self._last_new = [[]]
        self._last_operation = [-1, -1] # 初始
        self._score = [0, 0]
        self._player = 0
        
        if board is not None:
            self._board = board
        else:
            self._board = self.np_random.integers(
                0, self.categories, size=(self.size, self.size), dtype=int
            )
            
            k = self.size
            for i in range(): # 生成墙
                self._board[i][0] = 2
                self._board[0][i] = 2
                self._board[i][k-1] = 2
                self._board[k-1][i] = 2
            
        if self.render_mode == "logic": # 在逻辑渲染模式下，更新游戏状态的表示
            for i in range(self.size):
                for j in range(self.size):
                    self._last_new[0].append([i, j, int(self._board[i][j])])
        
        return self._board, self._get_info()
            
        