# 开发规范
| | |
| -------- | -------- |
| 新建功能 | feat: |
| 修复功能 | fix: |
| 更新文档 | docs: |
| 修改格式 | style: |
| 代码优化 | perf: |
| 测试功能 | test: |
| saiblo上更新逻辑版本 | saiblo: #XX |

# 通信
## 用户->逻辑：json转化为的字符串

### 作为卷王: 
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
action 为 0/1/2/3/4 分别表示 不动/上/左/下/右

## 逻辑->用户

<b>后端逻辑中的一轮（round）对应与judger通信中的三个回合（state）</b>

第0回合（state）发送座位信息：向0号玩家发送字符串```"0"```，向1号玩家发送字符串```"1"```

每轮（round）开始时，若改变棋盘则向0号玩家和1号玩家发送初始化信息：
```py
{
    "ghosts_coord": [ghost.get_coord() for ghost in self._ghosts], # 幽灵坐标
    "pacman_coord": self._pacman.get_coord(), # 卷王坐标
    "score": [self._pacman_score, self._ghosts_score], # 双方得分
    "level": self._level, # 关卡号
    "board": self._board.tolist(), # 棋盘，为一个二维数组
    "beannumber": beannum, # 豆子总数
    "portal_coord": self._portal_coord, # 传送门位置
}
```

每一轮（round）分为三个阶段，对应三个回合（state）

阶段一：读入0号玩家发送的消息，并给1号玩家发送信息```"player 0 send info"```

阶段二：读入1号玩家发送的消息，并给0号玩家发送信息```"player 1 send info"```

阶段三：调用step函数，执行操作

每局结束发给ai的信息为操作信息
```py
{
    "pacman_action" : pacman.action[0], # 一个数，为卷王的操作
    "ghosts_action" : ghosts.action # 一个含三个元素的数组，为三个幽灵的操作
}
```

每局结束发给播放器的信息为增量信息
```py
{
    "round": self._round, # 当前回合的轮数
    "level": self._level, # 当前回合数
    "pacman_step_block": self._pacman_step_block, # 卷王走过的路径
    "pacman_coord": self._pacman.get_coord(), # 卷王坐标
    "pacman_skills": self._last_skill_status, # 卷王技能
    "ghosts_step_block": self._ghosts_step_block, # 幽灵走过的路径
    "ghosts_coord": [ghost.get_coord() for ghost in self._ghosts], # 幽灵坐标
    "score": [self._pacman_score, self._ghosts_score], # 卷王和幽灵的得分
    "events": [i.value for i in self._event_list], # 事件
    "portal_available": self._portal_available, # 传送门是否已经开启
    "StopReason": None,
}
```
event_list中数与事件的对应如下：
```py
class Event(enum.Enum):
    # 0 and 1 should not occur simutaneously
    EATEN_BY_GHOST = 0 # when eaten by ghost, there are two events to be rendered. first, there should be a animation of pacman being caught by ghost. then, the game should pause for a while, and display a respawning animaiton after receiving next coord infomation.
    SHEILD_DESTROYED = 1 
    # 2 and 3 should not occur simutaneously
    FINISH_LEVEL= 2
    TIMEOUT = 3
```

游戏结束时，会再发送一次信息，其格式与增量信息的格式相同，不过"StopReason"对应的值不为空。

# 更新core中的内容
```
git submodule update --remote core
```