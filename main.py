import json
import random
import time
import os

from core.GymEnvironment import PacmanEnv
from logic.utils import *
from core.gamedata import *
# from random_seed import set_seed

ERROR_MAP = ["RE", "TLE", "OLE"]
replay_file = None

class Player():
    def __init__(
        self,
        id,
        type,
    ):
        self.id = id
        self.action = []
        self.type = type
        self.role = 0

# FIXME: 在reset的时候随机幽灵和吃豆人的位置，这个处于创建环境之后、开始游戏之前

def get_ai_info( env: PacmanEnv , playerid , player_type , another_player_type ):
    '''
    获取ai或播放器用户的操作: 玩家1和玩家2的类型: 1 为 AI, 2 为网页播放器。
    '''
    ai_info = receive_ai_info()
    #debug
    replay_file.write(json.dumps(ai_info, ensure_ascii=False)+"\n")

    while ai_info["player"] != -1 and ai_info["player"] != playerid:
        ai_info = receive_ai_info()
    # 判定交互对象状态
    # 如果交互对象异常则退出
    if ai_info["player"] == -1: 
        # judger 监听列表中的某个 AI 超时或发生错误 -> 终止游戏，返回错误信息
        return_dict = env.render()
        error_info = json.loads(ai_info["content"])
        error_type = error_info['error']
        error_player = error_info['player']
        return_dict["StopReason"] = f"Unexpected behavior of player {error_player}, judger returned error type {ERROR_MAP[error_type]}."

        # 回放文件写入结束信息
        replay_file.write(json.dumps(return_dict, ensure_ascii=False)+"\n")

        if player_type == 2:
            send_to_judger(
                json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), playerid
            )

        if another_player_type == 2:
            send_to_judger(
                json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), 1 - playerid
            )

        end_list = ["OK", "OK"]
        end_list[json.loads(ai_info["content"])["player"]] = ERROR_MAP[
            json.loads(ai_info["content"])["error"]
        ]
        pacmanscore = env.get_pacman_score()
        ghostscore = env.get_ghosts_score()
        end_info = {}
        if players[0].role == 0:
            end_info = {
                "0": pacmanscore,
                "1": ghostscore,
            }
        else:
            end_info = {
                "0": ghostscore,
                "1": pacmanscore,
            }
        send_game_end_info(json.dumps(end_info), json.dumps(end_list))
        replay_file.close()
        time.sleep(0.5)
        exit(0)
    else:
        try:
            # 获取操作
            info = json.loads(ai_info["content"])
            role = info["role"]
            action = [int(i) for i in info["action"].split(" ")]

            if role == 0 :
                # 表明玩家是吃豆人
                # 若字符串格式有误则默认不动
                if len(action) != 1 or action[0] < 0 or action[0] >= 5 : 
                    action = [0]
            else :
                # 表明玩家是幽灵
                if len(action) != 3 or action[0] < 0 or action[0] >= 5 or action[1] < 0 or action[1] >= 5 or action[2] < 0 or action[2] >= 5 :
                    action = [0,0,0]
            return role , action
        except:
            error = traceback.format_exc()
            return_dict = env.render()
            return_dict["StopReason"] = (
                f"Invalid Operation {ai_info['content']} from player {playerid}, judger returned error {error}."
            )
            # 回放文件写入结束信息
            replay_file.write(json.dumps(return_dict, ensure_ascii=False)+"\n")

            if player_type == 2:
                send_to_judger(
                    json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), playerid
                )

            if another_player_type == 2:
                send_to_judger(
                    json.dumps(return_dict, ensure_ascii=False).encode("utf-8"),
                    1 - playerid,
                )

            end_state = ["OK", "OK"]
            end_state[playerid] = "IA"

            pacmanscore = env.get_pacman_score()
            ghostscore = env.get_ghosts_score()
            end_info = {}
            if players[0].role == 0:
                end_info = {
                    "0": pacmanscore,
                    "1": ghostscore,
                }
            else:
                end_info = {
                    "0": ghostscore,
                    "1": pacmanscore,
                }

            send_game_end_info(
                json.dumps(end_info, ensure_ascii=False), json.dumps(end_state)
            )
            replay_file.close()
            time.sleep(0.5)
            exit(0)

def interact( env: PacmanEnv, pacman: Player , ghosts: Player ):
    '''
    env: 游戏逻辑维护的唯一局面
    pacman_type, ghost_type: 玩家1和玩家2的类型: 1 为 AI, 2 为网页播放器。
    
    执行操作，输出要转发给对方的字符串

    interact返回四个值: game_continue, info1, info2, level_change  info1和info2分别发给吃豆人和幽灵
    '''
    # 执行两个玩家的操作
    try:
        board , score , level_change = env.step(pacman.action[0], ghosts.action)
    except:
        error = traceback.format_exc()
        return_dict = env.render()
        return_dict["StopReason"] = f"Error in executing actions from players, error: {error}"
        replay_file.write(json.dumps(return_dict, ensure_ascii=False) + "\n")
        if pacman.type == 2:
            send_to_judger(
                json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), pacman.id
            )

        if ghosts.type == 2:
            send_to_judger(
                json.dumps(return_dict, ensure_ascii=False).encode("utf-8"), ghosts.id
            )

        end_state = ["IA", "IA"]

        pacmanscore = env.get_pacman_score()
        ghostscore = env.get_ghosts_score()
        end_info = {}
        if pacman.id == 0:
            end_info = {
                "0": pacmanscore,
                "1": ghostscore,
            }
        else:
            end_info = {
                "0": ghostscore,
                "1": pacmanscore,
            }

        send_game_end_info(
            json.dumps(end_info, ensure_ascii=False), json.dumps(end_state)
        )
        replay_file.close()
        time.sleep(0.5)
        exit(0)

    # 更新游戏状态
    new_state = env.render()
    replay_file.write(json.dumps(new_state, ensure_ascii=False) + "\n")
    if pacman.type == 2:
        send_to_judger(json.dumps(new_state, ensure_ascii=False).encode("utf-8"), pacman.id)

    if ghosts.type == 2:
        send_to_judger(json.dumps(new_state, ensure_ascii=False).encode("utf-8"), ghosts.id)

    # 返回新的状态信息
    game_continue = True
    info1 = None
    info2 = None
    if new_state['level'] != MAX_LEVEL or env.check_round_end() == False:
        # 游戏没有结束
        info1 = json.dumps(new_state, ensure_ascii=False) # 返回给吃豆人的信息
        info2 = json.dumps(new_state, ensure_ascii=False) # 返回给幽灵的信息
    else:
        game_continue = False

    return game_continue , info1 , info2 , level_change


if __name__ == "__main__":
    import traceback
    
    try:
        # 接收judger的初始化信息
        init_info = receive_init_info()
        replay_path = init_info["replay"]
        replay_dir = os.path.dirname(replay_path)
        if not os.path.exists(replay_dir):
            os.makedirs(replay_dir)
        replay_file = open(replay_path, 'w')
        # 设置随机种子
        try:
            seed = init_info["config"]["random_seed"]
        except:
            seed = random.randint(1, 100000000)

        env = PacmanEnv('logic')
        # 每局游戏唯一的游戏状态类，所有的修改应该在此对象中进行

        # playertype 0 表示未正常启动，1 表示本地 AI，2 表示网页播放器
        players = [Player(0,init_info["player_list"][0]),Player(1,init_info["player_list"][1])]

        if players[0].type == 0 or players[1].type == 0:
            # 状态异常，未正常启动
            end_dict = env.render()
            end_dict["StopReason"] = "player quit unexpectedly"
            end_json = json.dumps(end_dict, ensure_ascii=False)
            replay_file.write(end_json + "\n")

            if players[0].type == 2:
                send_to_judger(json.dumps(end_dict), 0)

            if players[1].type == 2:
                send_to_judger(json.dumps(end_dict), 1)

            end_state = json.dumps(
                ["OK" if players[0].type else "RE",
                    "OK" if players[1].type else "RE"]
            )
            # 若初始化异常则都为0分
            end_info = {
                "0": 0,
                "1": 0,
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
                init_json = json.dumps(env.reset(), ensure_ascii=False)
                replay_file.write(init_json+'\n')

            if not game_continue:
                break
            
            # 接受吃豆人的消息和幽灵的消息
            for i in range(2) :
                state += 1
                if players[i].type == 1:
                    send_round_config(MAX_AI_TIME, MAX_LENGTH)
                elif players[1-i].type == 2:
                    send_round_config(MAX_PLAYER_TIME, MAX_LENGTH)
                
                # level发生改变时将初始化信息发给ai，未改变时发送空串
                if level_change == 0:
                    send_round_info(
                        state,
                        [players[i].id],
                        [players[i].id,players[1-i].id],
                        [],
                    )
                    
                else:
                    level_change = 0
                    send_round_info(
                        state,
                        [players[i].id],
                        [players[i].id,players[1-i].id],
                        [init_json,init_json],
                    )

                players[i].role , players[i].action = get_ai_info(env,players[i].id,players[i].type,players[1-i].type)
                
            # 调用step
            state += 1
            send_round_config(MAX_AI_TIME, MAX_LENGTH)
            quit_running()
            if players[0].role == 0 :
                # 0号玩家是吃豆人
                game_continue , info1 , info2 , level_change = interact(
                    env, players[0] , players[1]
                )
                send_round_info(
                    state,
                    [],
                    [players[0].id,players[1].id],
                    [info1,info2],
                )
                
                
            else :
                # 1号玩家是吃豆人
                game_continue , info1 , info2 , level_change = interact(
                    env, players[1] , players[0]
                )
                send_round_info(
                    state,
                    [],
                    [players[1].id,players[0].id],
                    [info1,info2],
                )
                
            
        end_state = json.dumps(
            ["OK", "OK"]
        )
        pacmanscore = env.get_pacman_score()
        ghostscore = env.get_ghosts_score()
        print("score_pacman: {}".format(pacmanscore)) 
        print("score_ghost: {}".format(ghostscore)) 

        end_json = env.render()
        end_json["StopReason"] = f"time is up"
        end_info = {}
        if players[0].role == 0:
            end_info = {
                "0": pacmanscore,
                "1": ghostscore,
            }
        else:
            end_info = {
                "0": ghostscore,
                "1": pacmanscore,
            }
        if players[0].type == 2:
            send_to_judger(json.dumps(end_json, ensure_ascii=False).encode("utf-8"), 0)
        if players[1].type == 2:
            send_to_judger(json.dumps(end_json, ensure_ascii=False).encode("utf-8"), 1)

        replay_file.write(json.dumps(end_json, ensure_ascii=False) + "\n")
        send_game_end_info(json.dumps(end_info, ensure_ascii=False), end_state)
        replay_file.close()
        time.sleep(1)
        exit(0)

    except Exception as e:
        replay_file.write(traceback.format_exc())
        replay_file.write(str(e))
        replay_file.close()
        quit_running()

    replay_file.close()