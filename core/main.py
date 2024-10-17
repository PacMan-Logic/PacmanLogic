from GymEnvironment import PacmanEnv

def main():
    # 创建Pacman环境实例
    env = PacmanEnv(render_mode="local")

    # 初始化游戏环境并打印初始棋盘
    initial_state, info = env.reset()
    print("Initial game board:")
    env.render()


if __name__ == "__main__":
    main()