import json
import random
import time

from core.GymEnvironment import PacmanEnv
from logic.utils import *

ERROR_MAP = ["RE", "TLE", "OLE"]
replay_file = None
level = 0

# FIXME: 在reset的时候随机幽灵和吃豆人的位置，这个处于创建环境之后、开始游戏之前

def get_ai_info( player , player_type , another_player_type ):
    '''
    获取ai或播放器用户的操作: 玩家1和玩家2的类型: 1 为 AI, 2 为网页播放器。
    '''
    ai_info = receive_ai_info()
    while ai_info["player"] != -1 and ai_info["player"] != player:
        ai_info = receive_ai_info()
    # 判定交互对象状态
    # 如果交互对象异常则退出
    if ai_info["player"] == -1: # judger 监听列表中的某个 AI 超时或发生错误 -> 终止游戏，返回错误信息
        return_dict = env.render()
        error_info = json.loads(ai_info["content"])
        error_type = error_info['error']
        error_player = error_info['player']
        return_dict["StopReason"] = f"Unexpected behavior of player {error_player}, judger returned error type {ERROR_MAP[error_type]}."

        # 回放文件写入结束信息
        replay_file.write(json.dumps(return_dict, ensure_ascii=False)+"\n")

        if player_type == 2:
            send_to_judger(
                json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), player
            )

        if another_player_type == 2:
            send_to_judger(
                json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), 1 - player
            )

        end_list = ["OK", "OK"]
        end_list[json.loads(ai_info["content"])["player"]] = ERROR_MAP[
            json.loads(ai_info["content"])["error"]
        ]
        end_info = {
            "0": json.loads(ai_info["content"])["player"],
            "1": 1 - json.loads(ai_info["content"])["player"],
        }
        send_game_end_info(json.dumps(end_info), json.dumps(end_list))
        replay_file.close()
        time.sleep(0.5)
        exit(0)
    else:
        try:
            # 获取操作
            action = [int(i) for i in ai_info["content"].split(" ")]

            if player == 0 :
                # 判断是否为加速状态，加速状态传含两个元素的数组，否则传一个元素的数组
                assert(
                    len(action) == 1
                    and action[0] >= 0
                    and action[0] < 5
                )
            else :
                assert(
                    len(action) == 3
                    and action[0] >= 0
                    and action[0] < 5
                    and action[1] >= 0
                    and action[1] < 5
                    and action[2] >= 0
                    and action[2] < 5
                ) 
            return action
        except:
            error = traceback.format_exc()
            return_dict = env.render()
            return_dict["StopReason"] = (
                f"Invalid Operation {ai_info['content']} from player {player}, judger returned error {error}."
            )
            # 回放文件写入结束信息
            replay_file.write(json.dumps(return_dict, ensure_ascii=False)+"\n")

            if player_type == 2:
                send_to_judger(
                    json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), player
                )

            if another_player_type == 2:
                send_to_judger(
                    json.dumps(return_dict, ensure_ascii=False).encode("utf-8"),
                    1 - player,
                )

            end_state = ["OK", "OK"]
            end_state[player] = "IA"
            send_game_end_info(
                json.dumps({"0": player, "1": 1 - player}), json.dumps(end_state)
            )
            replay_file.close()
            time.sleep(0.5)
            exit(0)

def interact(env: PacmanEnv, pacman_action, pacman, ghost_action, ghost, pacman_type, ghost_type):
    '''
    env: 游戏逻辑维护的唯一局面
    pacman_type, ghost_type: 玩家1和玩家2的类型: 1 为 AI, 2 为网页播放器。
    1传str 2传json
    
    执行操作，输出要转发给对方的字符串
    '''
    # 执行两个玩家的操作
    try:
        info , level_change = env.step(pacman_action, pacman, ghost_action, ghost)
    except:
        error = traceback.format_exc()
        return_dict = env.render()
        return_dict["StopReason"] = f"Error in executing actions from players, error: {error}"
        replay_file.write(json.dumps(return_dict, ensure_ascii=False) + "\n")
        replay_file.close()
        time.sleep(0.5)
        exit(0)

    # 更新游戏状态
    new_state = env.render()
    replay_file.write(json.dumps(new_state, ensure_ascii=False) + "\n")

    if pacman_type == 2:
        send_to_judger(json.dumps(new_state, ensure_ascii=False).encode("utf-8"), 0)

    if ghost_type == 2:
        send_to_judger(json.dumps(new_state, ensure_ascii=False).encode("utf-8"), 1)

    # 返回新的状态信息
    if new_state['steps']:
        if pacman_type == 1 and pacman_type == 1:
            return True, str(info), level_change
        elif pacman_type == 2 or pacman_type == 2:
            return True, json.dumps(info, ensure_ascii=False), level_change
    else:
        return False, None, None


if __name__ == "__main__":
    import traceback

    try:
        # 接收judger的初始化信息
        init_info = receive_init_info()
        replay_file = open(init_info["replay"], 'w')
        # 设置随机种子
        try:
            seed = init_info["config"]["random_seed"]
        except:
            seed = random.randint(1, 100000000)

        env = PacmanEnv('logic')
        # 每局游戏唯一的游戏状态类，所有的修改应该在此对象中进行

        player_type = init_info["player_list"] # 0 表示未正常启动，1 表示本地 AI，2 表示网页播放器
        players = [0,1] # 0 为吃豆人，1 为幽灵
        pacman_action = []
        ghost_action = []

        if player_type[0] == 0 or player_type[1] == 0:
            # 状态异常，未正常启动
            end_dict = env.render()
            end_dict["StopReason"] = "player quit unexpectedly"
            end_json = json.dumps(end_dict, ensure_ascii=False)
            replay_file.write(end_json + "\n")

            if player_type[1] == 2:
                send_to_judger(json.dumps(end_dict), 1)

            if player_type[0] == 2:
                send_to_judger(json.dumps(end_dict), 0)

            end_state = json.dumps(
                ["OK" if player_type[0] else "RE",
                    "OK" if player_type[1] else "RE"]
            )
            end_info = {
                "0": 1 if player_type[0] else 0,
                "1": 1 if player_type[1] else 0,
            }
            send_game_end_info(json.dumps(end_info), end_state)
            replay_file.close()
            time.sleep(1)
            exit(0)

        state = 0

        game_continue = True
        level_change = 1
        # 一局中包含三个state 1.接收吃豆人消息 2.接收幽灵消息 3.调用step
        while game_continue:
            # 考察是否需要重新渲染，如果level发生改变，重置环境+获取初始化信息
            if level_change == 1:
                level = level + 1
                env.reset(level)
                init_json = json.dumps(env.get_init_info(), ensure_ascii=False)
                replay_file.write(init_json+'\n')

            if not game_continue:
                break
            
            # 接受吃豆人的消息和幽灵的消息
            for i in range(2) :
                state += 1
                if player_type[players[i]] == 1:
                    send_round_config(1, 1024)
                elif player_type[players[1-i]] == 2:
                    send_round_config(60, 1024)
                
                # level发生改变时将初始化信息发给ai，未改变时发送空串
                if level_change == 0:
                    send_round_info(
                        state,
                        [players[i]],
                        [players[i],players[1-i]],
                        [],
                    )
                else:
                    level_change = 0
                    send_round_info(
                        state,
                        [players[i]],
                        [players[i],players[1-i]],
                        [
                            str(init_json) if player_type[0] == 1 else init_json,
                            str(init_json) if player_type[1] == 1 else init_json,
                        ],
                    )

                if i == 0:
                    pacman_action = get_ai_info(players[i],player_type[i],player_type[1-i])
                else:
                    ghost_action = get_ai_info(players[i],player_type[i],player_type[1-i])
            
            # 调用step
            state += 1
            game_continue, info, level_change = interact(
                env, pacman_action, players[0], ghost_action, players[1], player_type[players[0]], player_type[players[1]]
            )
            send_round_info(
                state,
                [players[i]],
                [players[i],players[1-i]],
                [info,info],
            )
        end_state = json.dumps(
            ["OK", "OK"]
        )

        print("score_pacman: {}".format(env._score[0])) # 根据接口修改
        print("score_ghost: {}".format(env._score[1])) # 根据接口修改

        end_json = env.render()
        end_json["StopReason"] = f"time is up"
        end_info = {
            "score_pacman": env._score[0],
            "score_ghost": env._score[1],
        }

        if player_type[0] == 2:
            send_to_judger(json.dumps(end_json, ensure_ascii=False).encode("utf-8"), 0)
        if player_type[1] == 2:
            send_to_judger(json.dumps(end_json, ensure_ascii=False).encode("utf-8"), 1)

        replay_file.write(json.dumps(end_json, ensure_ascii=False) + "\n")
        send_game_end_info(json.dumps(end_info), end_state)
        replay_file.close()
        time.sleep(1)
        exit(0)

    except Exception as e:
        replay_file.write(traceback.format_exc())
        replay_file.write(str(e))
        replay_file.close()
        quit_running()

    replay_file.close()