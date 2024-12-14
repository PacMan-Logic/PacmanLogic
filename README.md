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

若改变棋盘则发送初始化信息
```py
{
    "ghosts_coord": [ghost.get_coord() for ghost in self._ghosts],
    "pacman_coord": self._pacman.get_coord(),
    "score": [self._pacman_score, self._ghosts_score],
    "level": self._level,
    "board": self._board.tolist(),
    "events": [],
    "beannumber": beannum, # 豆子总数
    "portal_coord": self._portal_coord, # 传送门位置
}
```

三个阶段

阶段一：读入吃豆人发的消息

阶段二：读入幽灵发的消息

阶段三：进行操作

每局结束发给ai的info
```py
{
    "pacman_action" : pacman.action[0],
    "ghosts_action" : ghosts.action
}
```

每局结束发给播放器的info
```py
{
    "round": self._round, 
    "level": self._level, 
    "pacman_step_block": self._pacman_step_block, 
    "pacman_coord": self._pacman.get_coord(), 
    "pacman_skills": self._last_skill_status, 
    "ghosts_step_block": self._ghosts_step_block, 
    "ghosts_coord": [
        self._ghosts[0].get_coord(),
        self._ghosts[1].get_coord(),
        self._ghosts[2].get_coord(),
    ], 
    "score": [self._pacman_score, self._ghosts_score], 
    "events": [i.value for i in self._event_list], 
    "StopReason": None,
}
{
    "round": self._round, # 当前回合的轮数
    "level": self._level, # 当前回合数
    "pacman_step_block": self._pacman_step_block, # 吃豆人走过的路径
    "pacman_coord": self._pacman.get_coord(), # 吃豆人坐标
    "pacman_skills": self._last_skill_status, # 吃豆人技能
    "ghosts_step_block": self._ghosts_step_block, # 幽灵走过的路径
    "ghosts_coord": [ghost.get_coord() for ghost in self._ghosts], # 幽灵坐标
    "score": [self._pacman_score, self._ghosts_score], # 吃豆人和幽灵的得分
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

# 更新core中的内容
```
git submodule update --remote core
```