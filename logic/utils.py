import json
import struct
import sys


# 发送数据包给 Judger
def send_to_judger(data, target=-1):
    length = len(data)
    header = struct.pack(">Ii", length, target)
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(data)
    sys.stdout.flush()


# 接收judger发来的数据包
def receive_from_judger():
    header = sys.stdin.buffer.read(4)
    length = struct.unpack(">I", header)[0]
    data = sys.stdin.buffer.read(length)
    sys.stdin.buffer.flush()
    return data


# judger 向逻辑发送初始化信息
def receive_init_info():
    # 接收来自 Judger 的字节流数据
    init_info_bytes = receive_from_judger()
    # 将字节流解码成字符串
    init_info_str = init_info_bytes.decode("utf-8")
    # 将JSON格式的字符串解析为 python 数据类型
    init_info = json.loads(init_info_str)
    return init_info


# 逻辑向judger发送回合配置信息
def send_round_config(time: int, length: int):
    round_config = {"state": 0, "time": time, "length": length}
    round_config_str = json.dumps(round_config)
    round_config_bytes = round_config_str.encode("utf-8")
    send_to_judger(round_config_bytes)


# 逻辑向 judger 发送正常回合消息
def send_round_info(state: int, listen: list[int], send: list[int], content: list[str]):
    round_info = {
        "state": state,
        "listen": listen,
        "player": send,
        "content": content,
    }

    round_info_bytes = json.dumps(round_info).encode("utf-8")
    send_to_judger(round_info_bytes)


# 逻辑向 judger 发送观战消息
def send_watch_info(watch: str):
    watch_info = {"watch": watch}
    watch_info_bytes = json.dumps(watch_info).encode("utf-8")
    send_to_judger(watch_info_bytes)


# judger 向逻辑发送 AI 正常或异常消息
def receive_ai_info():
    ai_info_bytes = receive_from_judger()
    ai_info_str = ai_info_bytes.decode("utf-8")
    ai_info = json.loads(ai_info_str)
    return ai_info


# 逻辑表示对局已结束，向 judger 请求 AI 结束状态
def request_ai_end_state():
    request_end = {"action": "request_end_state"}
    request_end_bytes = json.dumps(request_end).encode("utf-8")
    send_to_judger(request_end_bytes)


# judger 向逻辑回复 AI 结束状态
def receive_ai_end_state():
    ai_end_state_bytes = receive_from_judger()
    ai_end_state_str = ai_end_state_bytes.decode("utf-8")
    ai_end_state = json.loads(ai_end_state_str)
    return ai_end_state


# 逻辑向judger发送游戏结束信息
def send_game_end_info(end_info, end_state):
    game_end_info = {"state": -1, "end_info": end_info, "end_state": end_state}
    game_end_info_bytes = json.dumps(game_end_info).encode("utf-8")
    send_to_judger(game_end_info_bytes)

def quit_running():
    end_state = json.dumps(["RE", "RE"])
    end_info = {"0": 0, "1": 0}
    send_game_end_info(json.dumps(end_info), end_state)


def write_debug_into_replay(replay_file, message):
    with open(replay_file, "a") as f:
        f.write(message + "\n")
    f.close()


def write_end_info(replay_file, env, message, score_ghost , score_pacman):
    return_dict = {
        "round": env._round,
        "steps": env._max_round - env._round,
        "player": 0,
        "operation": env._last_operation,
        "score": [env._score, 0],
        "ManyTimesEliminateBlocks": env._last_elimination,
        "ManyTimesNewBlocks": env._last_new,
        "stop": None
    }
    with open(replay_file, "a") as f:
        f.write(
            json.dumps(
                {
                    "Round": round,
                    "Score": [score_ghost,score_pacman],
                    "Action": [9],
                    "Content": message,
                }, ensure_ascii=False
            )
            + "\n"
        )
    f.close()
