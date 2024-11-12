import json
import time
from typing import List
import random
import gym
import numpy as np
from gym import spaces
from .board import *
from .pacman import Pacman
from .ghost import Ghost
from .gamedata import *


import os


def opposite_direction(x, y):  # dont need this now
    if x == 0 or y == 0:
        return True
    if (x == 1 and y == 3) or (x == 3 and y == 1):
        return True
    if (x == 2 and y == 4) or (x == 4 and y == 2):
        return True
    return False


def have_same_element(a, b):  # dont need this now
    for i in a:
        if i in b:
            return True
    else:
        return False


class PacmanEnv(gym.Env):
    metadata = {"render_modes": ["local", "logic", "ai"]}

    def __init__(
        self,
        render_mode=None,
        size=INITIAL_BOARD_SIZE,  # this will subtract 20 in the reset function every time
    ):
        assert size >= 3
        self._size = size
        self._player = 0

        # Note: use round instead of time to terminate the game
        self._round = 0
        self._boardlist = []
        self._pacman = Pacman()
        self._ghosts = [Ghost(), Ghost(), Ghost()]

        self._event_list = []

        self._last_skill_status = [0] * SKILL_NUM

        self._level = 0  # Note: this will plus 1 in the reset function every time

        # store runtime details for rendering
        self._last_operation = []
        self._pacman_step_block = []
        self._ghosts_step_block = [[], [], []]
        self._pacman_score = 0
        self._ghosts_score = 0

        self.observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * SPACE_CATEGORY
        )  # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值

        self._pacman_action_space = spaces.Discrete(OPERATION_NUM)
        self._ghost_action_space = spaces.MultiDiscrete(np.ones(3) * OPERATION_NUM)
        # 这段代码定义了环境的动作空间。在训练过程中，吃豆人和幽灵应该索取不同的动作空间

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    # return the current state of the game
    # FIXME: 有测试更改
    def render(self, mode="logic"):
        if mode == "local":
            # os.system("clear")
            for i in range(self._size):
                for j in range(self._size):
                    if self._pacman.get_coord() == [i, j]:
                        print("\033[1;40m  \033[0m", end="")
                        continue
                    if [i, j] in [ghost.get_coord() for ghost in self._ghosts]:
                        print("\033[1;40m  \033[0m", end="")
                        continue
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
                        print("\033[1;48;5;208m  \033[0m", end="")  # *2豆子：橘
                print()

        elif mode == "logic":  # 返回一个字典
            return_dict = {
                "ghosts_step_block": self._ghosts_step_block,
                "ghosts_coord": [
                    self._ghosts[0].get_coord(),
                    self._ghosts[1].get_coord(),
                    self._ghosts[2].get_coord(),
                ],
                "pacman_step_block": self._pacman_step_block,
                "pacman_coord": self._pacman.get_coord(),
                "pacman_skills": self._last_skill_status,
                # Note: 播放器需要根据是否有magnet属性确定每次移动的时候需要如何吸取豆子
                "round": self._round,
                "score": [self._pacman_score, self._ghosts_score],
                "level": self._level,
                "events": [i.value for i in self._event_list],
                "StopReason": None,
            }
            return return_dict

    # training utils
    def observation_space(self):
        return self.observation_space

    def pacman_action_space(self):
        return self._pacman_action_space

    def ghost_action_space(self):
        return self._ghost_action_space

    def reset(self):
        self._size -= 20  # 80 60 40 20
        self._level += 1  # 0 1 2 3

        # regenerate at the corner
        coords = [
            [1, 1],
            [1, self._size - 2],
            [self._size - 2, 1],
            [self._size - 2, self._size - 2],
        ]

        # shuffle the coords
        random.shuffle(coords)

        # distribute the coords
        self._pacman.set_coord(coords[0])
        self._ghosts[0].set_coord(coords[1])
        self._ghosts[1].set_coord(coords[2])
        self._ghosts[2].set_coord(coords[3])

        self._board = final_boardgenerator(self._size)

        self._boardlist.append(self._board)  # Note: store the board for rendering

        self._round = 0

        return_board = self._board.tolist()

        return_dict = {
            "ghosts_coord": [
                self._ghosts[0].get_coord(),
                self._ghosts[1].get_coord(),
                self._ghosts[2].get_coord(),
            ],
            "pacman_coord": self._pacman.get_coord(),
            "score": [self._pacman_score, self._ghosts_score],
            "level": self._level,
            "board": return_board,
            "status": 1,  # ???
        }
        return return_dict

    def get_level(self):
        return self._level

    # step utils
    def check_round_end(self):
        return self._round >= MAX_ROUND[self._level]

    def update_all_score(self):
        self._pacman_score = self.get_pacman_score()
        self._ghosts_score = self.get_ghosts_score()

    # Note: 如果pacman撞墙(x,y), step(x-100, y-100); 如果ghost撞墙(x,y), step(x-200, y-200)
    def step(self, pacmanAction: int, ghostAction: List[int]):

        self._round += 1

        # 重置事件列表（本轮）
        self._event_list = []

        self._last_operation = []
        self._ghosts_step_block = [[], [], []]
        self._pacman_step_block = []

        self._last_skill_status = self._pacman.get_skills_status()
        self._last_operation = [pacmanAction, ghostAction]

        pacman_coord = self._pacman.get_coord()
        ghost_coords = [ghost.get_coord() for ghost in self._ghosts]

        # pacman move
        # Note: double_score: 0, speed_up: 1, magnet: 2, shield: 3
        self._pacman_step_block.append(pacman_coord)
        for i in range(3):
            self._ghosts_step_block[i].append(ghost_coords[i])

        self._pacman.eat_bean(self._board)  # 吃掉此处的豆子
        pacman_skills = self._pacman.get_skills_status()  # 更新状态
        # Note: 向下和向上的位置对调
        if pacman_skills[Skill.SPEED_UP.value] > 0:
            if pacmanAction == 0:
                self._pacman_step_block.append(self._pacman.get_coord())
                self._pacman_step_block.append(self._pacman.get_coord())
            elif pacmanAction == 3:  # 向下移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.up(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100 - 1,
                        self._pacman.get_coord()[1] - 100,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.up(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100 - 1,
                        self._pacman.get_coord()[1] - 100,
                    ]
                )
            elif pacmanAction == 2:  # 向左移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.left(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100,
                        self._pacman.get_coord()[1] - 100 - 1,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.left(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100,
                        self._pacman.get_coord()[1] - 100 - 1,
                    ]
                )
            elif pacmanAction == 1:  # 向上移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.down(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100 + 1,
                        self._pacman.get_coord()[1] - 100,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.down(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100 + 1,
                        self._pacman.get_coord()[1] - 100,
                    ]
                )
            elif pacmanAction == 4:  # 向右移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.right(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100,
                        self._pacman.get_coord()[1] - 100 + 1,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.right(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100,
                        self._pacman.get_coord()[1] - 100 + 1,
                    ]
                )
            else:  # 退出程序
                raise ValueError("Invalid action number of speedy pacman")
        else:
            if pacmanAction == 0:
                self._pacman_step_block.append(self._pacman.get_coord())
            elif pacmanAction == 3:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.up(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100 - 1,
                        self._pacman.get_coord()[1] - 100,
                    ]
                )
            elif pacmanAction == 2:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.left(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100,
                        self._pacman.get_coord()[1] - 100 - 1,
                    ]
                )
            elif pacmanAction == 1:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.down(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100 + 1,
                        self._pacman.get_coord()[1] - 100,
                    ]
                )
            elif pacmanAction == 4:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.right(self._board)
                    else [
                        self._pacman.get_coord()[0] - 100,
                        self._pacman.get_coord()[1] - 100 + 1,
                    ]
                )
            else:
                raise ValueError("Invalid action number of normal pacman")
        self.update_all_score()
        # ghost move
        for i in range(3):
            if ghostAction[i] == 0:
                self._ghosts_step_block[i].append(self._ghosts[i].get_coord())
                pass
            elif ghostAction[i] == 3:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].up(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] - 200 - 1,
                        self._ghosts[i].get_coord()[1] - 200,
                    ]
                )
            elif ghostAction[i] == 2:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].left(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] - 200,
                        self._ghosts[i].get_coord()[1] - 200 - 1,
                    ]
                )
            elif ghostAction[i] == 1:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].down(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] - 200 + 1,
                        self._ghosts[i].get_coord()[1] - 200,
                    ]
                )
            elif ghostAction[i] == 4:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].right(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] - 200,
                        self._ghosts[i].get_coord()[1] - 200 + 1,
                    ]
                )
            else:
                raise ValueError("Invalid action of ghost")
        self.update_all_score()

        # check if ghosts caught pacman
        flag = False
        for i in range(3):
            if pacman_skills[Skill.SPEED_UP.value] > 0:

                # NOTE: debugging start
                assert len(self._pacman_step_block) > 2
                for g in self._ghosts_step_block:
                    assert len(g) > 1
                # NOTE: debugging end

                if self._pacman_step_block[-2] == self._ghosts_step_block[i][-1]:
                    flag = True
            if self._pacman_step_block[-1] == self._ghosts_step_block[i][-1]:
                flag = True

        if flag:
            if not self._pacman.encounter_ghost():
                self._ghosts[i].update_score(DESTORY_PACMAN_SHIELD)
                self.update_all_score()
                self._event_list.append(Event.SHEILD_DESTROYED)
            else:
                self._pacman.update_score(EATEN_BY_GHOST)
                self._ghosts[i].update_score(EAT_PACMAN)
                self.update_all_score()
                self._pacman.set_coord(self.find_distant_emptyspace())
                # Note: if caught, the respawning coord will be stored at the last position of the list"pacman_step_block"
                self._pacman_step_block.append(self._pacman.get_coord())
                self._event_list.append(Event.EATEN_BY_GHOST)

        # diminish the skill time
        self._pacman.new_round()
        # 避免出现最后一轮明明达到了最后一个豆子，但是还是会被判定为超时的问题
        try:
            self._pacman.eat_bean(self._board)
        except:
            print("Pacman eat bean error")
            exit(1)

        # check if the game is over
        count_remain_beans = 0
        for i in range(self._size):
            for j in range(self._size):
                if self._board[i][j] == 2 | 3:
                    count_remain_beans += 1

        # 通关
        if count_remain_beans == 0:
            self._pacman.update_score(
                EAT_ALL_BEANS
                + (MAX_ROUND[self._level] - self._round) * ROUND_BONUS_GAMMA
            )
            self.update_all_score()
            self._pacman.reset()
            self._event_list.append(Event.FINISH_LEVEL)
            # return true means game over
            return (self._board, [self._pacman_score, self._ghosts_score], True)

        # 超时
        if self._round >= MAX_ROUND[self._level]:
            for i in self._ghosts:
                i.update_score(PREVENT_PACMAN_EAT_ALL_BEANS)
            self.update_all_score()
            self._pacman.reset()
            self._event_list.append(Event.TIMEOUT)
            return (self._board, [self._pacman_score, self._ghosts_score], True)

        # 正常
        return self._board, [self._pacman_score, self._ghosts_score], False

    def get_pacman_score(self):
        return self._pacman.get_score()

    def get_ghosts_score(self):
        ghost_scores = [ghost.get_score() for ghost in self._ghosts]
        return sum(ghost_scores)

    # in case of respawn just beside the ghosts, find a distant empty space
    def find_distant_emptyspace(self):
        coord = []
        max = 0
        for i in range(self._size):
            for j in range(self._size):
                if self._board[i][j] == Space.EMPTY.value:
                    sum = 0
                    for k in self._ghosts:
                        sum += abs(k.get_coord()[0] - i) + abs(k.get_coord()[1] - j)
                    if sum > max:
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

    def events(self):
        return self._event_list
