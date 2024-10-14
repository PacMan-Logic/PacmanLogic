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
        operation_num = 5,
        categories = 9, # 1. empty, 2. wall, 3. regular bean, 4. bonus bean, 5. speed bean, 6. magnet bean, 7. *2 bean 8. pacman 9. ghost
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
        self._board = None
        self._score = [0, 0]

        self._pacman = pacman
        self._pacmanskill = pacmanskill

        self._compete = ghost

        self.start_time = None
        self.max_time = 180 # 最长限时3分钟，后续可修改
        
        self.observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * categories
        ) # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值
        
        self.action_space = spaces.Discrete(1000)
        
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        
    def render(self):
    # TODO(lxy): 修改墙的显示
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
        self.start_time = time.time()
        super().reset(seed=seed)
        self._last_new = [[]]
        self._last_operation = [[-1],[-1,-1,-1]] # 分别代表吃豆人的行动操作（第一个数）和三个幽灵的行动操作（后三个数）
        self._score = [0, 0]
        self._player = 0
        
        if board is not None:
            self._board = board
        else:
            self._board = self.np_random.integers(
                0, self.categories, size=(self.size, self.size), dtype=int
            )
            # TODO(lxy): 修改墙生成逻辑 + 豆子的生成逻辑（或许需要考虑豆子生成的概率），幽灵起始位置
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
    
    def num_to_coord(self, role, action): 
        assert role == 0 or role == 1

        if role == 0:
            assert action >= 0 and action < self.operation_num
            return action
        if role == 1:
            c = action % 10
            b = ( action // 10 ) % 10
            a = ( action // 100 ) % 10
            assert a >= 0 and a < self.operation_num and b >= 0 and b < self.operation_num and c >= 0 and c < self.operation_num 
            return [a,b,c]
    
    def coord_to_num(self, role, action):
        assert (
            role == 0 or role == 1
        )
        if role == 0:
            assert (
                len(action) == 1
                and action[0] >= 0
                and action[0] < self.operation_num
            )
            return action[0]
        if role == 1:
            assert (
                len(action) == 3
                and action[0] >= 0
                and action[0] < self.operation_num
                and action[1] >= 0
                and action[1] < self.operation_num
                and action[2] >= 0
                and action[2] < self.operation_num
            )
            return action[0] * 100 + action[1] * 10 + action[2]

    # TODO(zyc): def step(self, action, pacman=0, ghost=0):
    # 先判断是否到限制的时间（调用check_time）
    # 判断吃到豆子的情况，修改棋盘状态，判断幽灵和吃豆人的行动是否合法，计算幽灵和吃豆人位置（注意技能）和幽灵和吃豆人相遇情况，计算得分
            
        