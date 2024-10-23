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
    "player": self._player,
    "ghosts_step_block": self._ghosts_step_block,
    "pacman_step_block": self._pacman_step_block,
    "pacman_skills": self._last_skill_status,
    "round": self._round,
    "score": self._score,
    "level": self._level,
    "StopReason": None,
}
```