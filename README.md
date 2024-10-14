## 用户->逻辑：一个字符串

### 作为吃豆人: "action"

### 作为幽灵: "action1 action2 action3"

action 为 0/1/2/3/4 表示 不动/上/下/左/右

p.s.注意在调用coord_to_num和num_to_coord时传入role(0/1代表吃豆人/幽灵)

main函数中可以直接调用coord_to_num进行编码，step中可以直接调用num_to_coord进行解码
