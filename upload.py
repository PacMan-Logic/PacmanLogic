import argparse
import asyncio
import json
import os
import tempfile
from enum import Enum
from pathlib import Path
from zipfile import ZipFile

import requests
import websockets


class Language(Enum):
    python_zip = "python_zip"
    cpp_zip = "cpp_zip"
    auto = "auto"

    def __str__(self):
        return self.value


if "AUTH_TOKEN" not in os.environ:
    print(f"错误：请设置环境变量 AUTH_TOKEN，内容为您的 Saiblo 登录口令。")
    exit(1)

AUTH = f"Token {os.environ['AUTH_TOKEN']}"
headers = {"Authorization": AUTH}


def file_filter(p):
    for part in p.parts:
        if part != "." and part != ".." and part.startswith("."):
            return False
    return True


def upload():
    parser = argparse.ArgumentParser(
        prog="saiblo-upload", description="Saiblo AI 代码上传脚本"
    )
    parser.add_argument("--game", type=str, required=True, help="游戏名")
    parser.add_argument("--name", type=str, required=True, help="AI 名称")
    parser.add_argument("--repo", type=str, required=True, help="AI 仓库 url")
    parser.add_argument("--commit", type=str, required=True, help="AI 提交哈希")
    parser.add_argument(
        "--lang", type=Language, choices=list(Language), required=True, help="AI 语言"
    )
    parser.add_argument("--path", type=str, required=True, help="代码目录")
    parser.add_argument(
        "--dev", action="store_true", default=False, help="是否提交到 dev 站"
    )
    parser.add_argument(
        "--logic", action="store_true", default=False, help="是否为逻辑代码"
    )
    args = parser.parse_args()

    api_base = (
        "https://api.dev.saiblo.net/api/" if args.dev else "https://api.saiblo.net/api/"
    )
    ws_base = "wss://api.dev.saiblo.net/ws/" if args.dev else "wss://api.saiblo.net/ws/"

    src_path = Path(args.path)
    if not src_path.is_dir():
        print(f"错误：{args.path} 不是路径！")
        parser.print_help()
        exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:

        # 构建压缩包
        zip_path = Path(temp_dir) / "source.zip"

        with ZipFile(zip_path, "w") as f:
            for p in src_path.glob("**/*"):
                if file_filter(p):
                    f.write(p)

        # 查找游戏
        games = requests.get(f"{api_base}games/").json()
        for game in games:
            if game["name"] == args.game:
                game_id = game["id"]
                break
        else:
            print(f"错误：游戏 {args.game} 未找到！")
            exit(1)

        # 获取用户名
        username = requests.get(f"{api_base}profile", headers=headers).json()["user"][
            "username"
        ]
        if args.logic:
            if username != "admin":
                print(f"错误：逻辑代码只能由管理员上传。")
                exit(1)
            else:
                args.name = "Logic Entity"

        # 查找 AI
        entities = requests.get(
            f"{api_base}users/{username}/games/{game_id}/entities", headers=headers
        ).json()["entities"]
        for e in entities:
            if e["name"] == args.name:
                if e["language"] != str(args.lang):
                    print(f"错误：AI 语言不一致。")
                    exit(1)
                if not args.logic:
                    if e["repo"] != args.repo:
                        print(f"错误：AI 仓库地址不一致。当前AI仓库地址为" + str(e["repo"]))
                        exit(1)
                entity = e
                break
        else:
            entity = requests.post(
                f"{api_base}users/{username}/games/{game_id}/entities/",
                headers=headers,
                json={
                    "language": str(args.lang),
                    "name": args.name,
                    "repo": args.repo,
                },
            ).json()
        entity_id = entity["id"]

        # 添加代码
        async def add_ai_code():
            async with websockets.connect(
                f"{ws_base}ai?token={AUTH.replace(' ', '%20')}", extra_headers=headers
            ) as ws:
                await ws.send(json.dumps({"entity": entity_id}))

                with open(zip_path, "rb") as f:
                    code = requests.post(
                        f"{api_base}entities/{entity_id}/codes/",
                        headers=headers,
                        data={"commit_id": args.commit},
                        files={"file": f},
                    ).json()
                    version = code["version"]

                recv = None
                while (
                    recv is None
                    or recv["version"] != version
                    or (
                        recv["compile_status"] != "编译成功"
                        and recv["compile_status"] != "编译失败"
                    )
                ):
                    recv = json.loads(await ws.recv())

                if recv["compile_status"] == "编译失败":
                    message = recv["compile_message"]
                    print(f"错误：编译失败！失败原因：\n{message}")
                    exit(1)
                token = recv["id"]
                print(f"上传并编译成功！AI 的 token 为：\n{token}")

        asyncio.get_event_loop().run_until_complete(add_ai_code())


if __name__ == "__main__":
    upload()
