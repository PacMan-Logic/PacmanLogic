import threading
import random

class Pacman:
    def __init__(self, id=0, score=0, double_score=False, speed_up=False, magnet=False, shield=False, x = 1, y = 1):
        self.id = id
        self.score = score
        self.double_score = double_score
        self.speed_up = speed_up
        self.magnet = magnet
        self.shield = shield
        self.x = x
        self.y = y
    
    def update_score(self, points):
        if self.double_score:
            self.score += points * 2
        else:
            self.score += points

    def just_eat(self, board, x, y):
        if board[x][y] ==2:
            self.update_score(1)
            board[x][y] = 1
        elif board[self.x][self.y] ==3:
            self.update_score(2)
            board[x][y] = 1
        elif board[x][y] ==4:
            self.activate_speed_up()
            board[x][y] = 1
        elif board[x][y] ==5:
            self.activate_magnet()
            board[x][y] = 1
        elif board[x][y] ==6:
            self.activate_shield()
            board[x][y] = 1
        elif board[x][y] ==7:
            self.activate_double_score()
            board[x][y] = 1
            
    def eat_bean(self, board, x, y):
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
    
    # 移动函数集成了加分和更新状态的功能
    def W(self, board):
        if self.speed_up:
            self.x -= 1
            self.eat_bean(board)
            self.x -= 1
            self.eat_bean(board)
        else:
            self.x -= 1
            self.eat_bean(board)
    
    def A(self, board):
        if self.speed_up:
            self.y -= 1
            self.eat_bean(board)
            self.y -= 1
            self.eat_bean(board)
        else:
            self.y -= 1
            self.eat_bean(board)
    
    def S(self, board):
        if self.speed_up:
            self.x += 1
            self.eat_bean(board)
            self.x += 1
            self.eat_bean(board)
        else:
            self.x += 1
            self.eat_bean(board)
    
    def D(self, board):
        if self.speed_up:
            self.y += 1
            self.eat_bean(board)
            self.y += 1
            self.eat_bean(board)
        else:
            self.y += 1
            self.eat_bean(board)
    
    def activate_double_score(self, duration=10):
        self.double_score = True
        # 创建一个计时器，当时间到达时，护盾将被停用
        timer = threading.Timer(duration, self.deactivate_double_score)
        # 启动计时器
        timer.start()
    
    def deactivate_double_score(self):
        self.double_score = False

    def activate_speed_up(self, duration=10):
        self.speed_up = True
        timer = threading.Timer(duration, self.deactivate_speed_up)
        timer.start()
        
    def deactivate_speed_up(self):
        self.speed_up = False
    
    def activate_magnet(self, duration=10):
        self.magnet = True
        timer = threading.Timer(duration, self.deactivate_magnet)
        timer.start()
    
    def deactivate_magnet(self):
        self.magnet = False
    
    def activate_shield(self, duration=10):
        self.shield = True
        timer = threading.Timer(duration, self.deactivate_shield)
        timer.start()

    def deactivate_shield(self):
        self.shield = False
    
    # 判断pacman是否撞墙，是否与ghost相遇的部分应该放在main函数中实现
    
    def encounter_ghost(self, board):
        if self.shield:
            self.shield = False
            return
        else:
            self.score -= 100
            self.respawn_at_non_zero(board)
            
    def respawn_at_non_zero(self, board):
    # 找到所有元素不为0的位置，忽略最外面一圈
        non_zero_positions = [(i, j) for i, row in enumerate(board[1:-1]) for j, element in enumerate(row[1:-1]) if element != 0]
    # 随机选择一个位置
        new_position = random.choice(non_zero_positions)
    # 更新 Pacman 的位置
        self.x, self.y = new_position
        
    # （lxy）我认为传送点应该用一个不同于空地的类型来表示，因为如果不是这样的话，在磁铁状态下，下标的访问会越界
    