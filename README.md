## 用户->逻辑：一个字符串

### 作为吃豆人: "action"

### 作为幽灵: "action1 action2 action3"

action 为 0/1/2/3/4 表示 不动/上/下/左/右

## 逻辑->用户
三个阶段

阶段一：读入吃豆人发的消息，如果有棋盘更新会发送info

阶段二：读入幽灵发的消息

阶段三：进行操作

每局结束发给ai的info
```
{
    "pacman_pos": [x,y],
    "pacman_skill": [double_score,speed_up,magnet,shield], # 一个数组，每一个数表示该技能剩余轮数
    "pacman_score": score # pacman的分数
    "ghost1_pos": [x1,y1],
    "ghost2_pos": [x2,y2],
    "ghost3_pos": [x3,y3],
    "ghost_score": score # ghost的分数
    "board": board # 二维数组棋盘
    "board_round": round # 一个数，表示剩余的轮数
}
```