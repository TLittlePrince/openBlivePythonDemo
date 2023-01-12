import asyncio

from BliveWebsocket import BliveWebsocket
from OpenBlive import OpenBlive


async def heartbeat(open_blive: OpenBlive, game_id: str) -> None:
    """
    单个20s心跳(例子)

    :param open_blive: OpenBlive类
    :param game_id: 场次id
    :return: None
    """
    while True:
        await asyncio.sleep(20)
        open_blive.send_heartbeat(game_id)


def on_msg(msg: dict) -> None:
    """
    收到弹幕回调(例子)

    :param msg: 弹幕消息
    :return: None
    """
    print(msg)


async def main():
    a_key = ""  # 申请的access_key
    a_secret = ""  # 申请的access_secret
    bili_app_id = 1649539569084  # 你的项目id
    user_code = 'BLMNUWXVJWU85'  # 主播的身份码
    open_blive = OpenBlive(a_key, a_secret)
    start_info = open_blive.app_start(bili_app_id, user_code)  # 开启项目
    game_id = start_info['data']['game_info']['game_id']
    websocket_info = start_info['data']['websocket_info']
    auth_body = websocket_info['auth_body']
    wss_link = websocket_info['wss_link'][-1]
    asyncio.create_task(heartbeat(open_blive, game_id))  # 保持项目心跳
    blive_websocket = BliveWebsocket(wss_link, auth_body)
    blive_websocket.set_on_message(on_msg)  # 设置消息回调
    await blive_websocket.connect()  # 保持连接


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
