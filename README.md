# 开发规范
新建功能 feat:

修复功能 fix:

saiblo: #XX

# 通信
## 用户->逻辑：json转化为的字符串

### 作为吃豆人: 
```json
{
    "role": 0,
    "action": "action"
}
```

### 作为幽灵: 
```json
{
    "role": 1,
    "action": "action1 action2 action3"
}
```
action 为 0/1/2/3/4 表示 不动/上/左/下/右

## 逻辑->用户
三个阶段

阶段一：读入吃豆人发的消息，如果有棋盘更新会发送info
```py
{
    "ghosts_coord": [self._ghosts[0].get_coord(),self._ghosts[1].get_coord(),self._ghosts[2].get_coord()],
    "pacman_coord": self._pacman.get_coord(),
    "score": [self._pacman_score, self._ghosts_score],
    "level": self._level,
    "board": return_board, # 二维数组，棋盘 
    "status": 1,
}
```

阶段二：读入幽灵发的消息

阶段三：进行操作

每局结束发给ai的info
```py
{
    "player": self._player, # ???
    "ghosts_step_block": self._ghosts_step_block, # 幽灵走过路径
    "ghosts_coord": [self._ghosts[0].get_coord(),self._ghosts[1].get_coord(),self._ghosts[2].get_coord()], # 幽灵坐标
    "pacman_step_block": self._pacman_step_block, # 吃豆人路径
    "pacman_coord": self._pacman.get_coord(), # 吃豆人坐标
    "pacman_skills": self._last_skill_status, # 吃豆人技能
    # Note: 播放器需要根据是否有magnet属性确定每次移动的时候需要如何吸取豆子
    "round": self._round, # 轮数
    "score": [self._pacman_score, self._ghosts_score], # 吃豆人、幽灵分数
    "level": self._level, # 关卡数
    "StopReason": None,
    "status": self._status_code.value, # 是否切换新的关卡
}
```