import numpy as np
import random

def boardgenerator(size):
    # 创建20x20的二维数组，所有元素初始化为2（普通豆子）
    board = np.full((size, size), 2)

    # 生成墙壁
    for i in range(2, size - 2, ((size - 4) // 2) + 1):
        for j in range(2, size - 2, ((size - 2) // 2) ):
            number = random.choice([1, 2, 3, 4, 5])
            if number == 1:
                board = l_wall_generator(board, ((size - 4) // 2), min(i + ((size - 4) // 2), size - 3) - 1 , j )
            elif number == 2:
                board = opposite_l_wall_generator(board, (size - 4) // 2, i, min(j + ((size - 4) // 2), size - 3) - 1)
            elif number == 3:
                board = cross_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 4:
                board = c_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 5:
                board = opposite_c_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            
	
	# 生成不同种类的豆子
    for i in range(1, size - 2):
        for j in range(1, size - 2):
            if board[i][j] == 2:
                number = random.randint(0, 100)
                if number < 5:
                    board[i][j] = 3
                elif number < 10:
                    board[i][j] = 4
                elif number < 15:
                    board[i][j] = 5
                elif number < 20:
                    board[i][j] = 6
                elif number < 25:
                    board[i][j] = 7
     
    # 在地图的边缘添加墙壁，并预留两个出口
    board[0, :] = board[-1, :] = board[:, 0] = board[:, -1] = 0
    exit1, exit2 = random.sample(range(1, size-1), 2)
    board[0, exit1] = board[-1, exit2] = 8
    
    return board

def l_wall_generator(board, size, x, y):
    # 生成L形墙
    board[x][y] = 0
    for i in range(1, size - 2):
        board[x - i][y] = 0
        board[x][y + i] = 0
    cnt = (size // 3) + 1
    while cnt > 0:
        a = random.randint(x - size + 3,  x - 1)
        b = random.randint(y + 1,  y + size - 3)
        if board[a][b] == 2:
            board[a][b] = 0
            cnt -= 1
    return board

def opposite_l_wall_generator(board, size, x, y):
    # 生成反L形墙
    board[x][y] = 0
    for i in range(1, size - 2):
        board[x + i][y] = 0
        board[x][y - i] = 0
    cnt = (size // 3) + 1
    while cnt > 0:
        a = random.randint(x + 1, x + size - 3)
        b = random.randint(y - size + 3,  y - 1)
        if board[a][b] == 2:
            board[a][b] = 0
            cnt -= 1
    return board
    
def cross_wall_generator(board, size, x, y):
    # 生成十字墙
    len = size // 2 
    board[x][y] = 0
    for i in range(1, len):
        board[x - i][y] = 0
        board[x + i][y] = 0
        board[x][y - i] = 0
        board[x][y + i] = 0
    return board

def c_wall_generator(board, size, x, y):
    # 生成C形墙
    len = (size // 2) - 1
    board[x][y] = 0
    for i in range(0, len + 1):
        board[x - i][y + len] = 0
        board[x + i][y + len] = 0
        board[x - len][y + i] = 0
        board[x - len][y - i] = 0
        board[x + len][y + i] = 0
        board[x + len][y - i] = 0
        board[x - i][y - len] = 0
        board[x + i][y - len] = 0
    board[x][y + len] = 3
    board[x][y - len] = 3
    return board

def opposite_c_wall_generator(board, size, x, y):
    # 生成反C形墙
    len = (size // 2) - 1
    board[x][y] = 0
    for i in range(0, len + 1):
        board[x - i][y - len] = 0
        board[x + i][y - len] = 0
        board[x - len][y + i] = 0
        board[x - len][y - i] = 0
        board[x + len][y + i] = 0
        board[x + len][y - i] = 0
        board[x - i][y + len] = 0
        board[x + i][y + len] = 0
    board[x][y - len] = 3
    board[x - len][y] = 3
    
    return board