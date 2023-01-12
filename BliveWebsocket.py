import asyncio
import json
import struct
import zlib

import websockets


def get_operation_info(value):
    info = {
        2: '客户端发送的心跳包',
        3: '服务器收到心跳包的回复',
        5: '服务器推送的弹幕消息包',
        7: '客户端发送的鉴权包(客户端发送的第一个包)',
        8: '服务器收到鉴权包后的回复',
    }

    try:
        return {'info': info[value], 'unpack': value != 3}
    except KeyError:
        return {'info': '未定义', 'unpack': True}


class Proto:
    """
    打包及解包
    (https://open-live.bilibili.com/document/doc&tool/api/websocket.html#_2-%E5%8F%91%E9%80%81%E5%BF%83%E8%B7%B3)
    """

    def __init__(self):
        self.packetLen = 0  # 整个Packet的长度, 包含Header
        self.headerLen = 16  # Header的长度, 固定为16
        self.ver = 0  # 0: 实际发送的数据; 2: 压缩后的数据

        # 消息的类型
        # OP_HEARTBEAT	      2	客户端发送的心跳包(30秒发送一次)
        # OP_AUTH	          7	客户端发送的鉴权包(客户端发送的第一个包)
        self.op = 0

        self.seq = 0  # 保留字段
        self.body = ''  # 接口获取的auth_body字段
        self.maxBody = 2048

    def pack(self):
        self.packetLen = len(self.body) + self.headerLen
        buf = struct.pack('>i', self.packetLen)
        buf += struct.pack('>h', self.headerLen)
        buf += struct.pack('>h', self.ver)
        buf += struct.pack('>i', self.op)
        buf += struct.pack('>i', self.seq)
        buf += self.body.encode()
        return buf

    def unpack(self, buf):
        if len(buf) < self.headerLen:
            print("包头不够")
            return
        return_packetLen = struct.unpack('>i', buf[0:4])[0]
        return_headerLen = struct.unpack('>h', buf[4:6])[0]
        return_ver = struct.unpack('>h', buf[6:8])[0]

        # 消息的类型
        # OP_HEARTBEAT_REPLY  3	服务器收到心跳包的回复
        # OP_SEND_SMS_REPLY	  5	服务器推送的弹幕消息包
        # OP_AUTH_REPLY	      8	服务器收到鉴权包后的回复
        return_op = struct.unpack('>i', buf[8:12])[0]

        return_seq = struct.unpack('>i', buf[12:16])[0]
        if return_packetLen < 0 or return_packetLen > self.maxBody:
            print("包体长不对", "self.packetLen:", return_packetLen,
                  " self.maxBody:", self.maxBody)
            return
        if return_headerLen != return_headerLen:
            print("包头长度不对")
            return
        info = get_operation_info(return_op)
        print(info['info'])
        if info['unpack']:
            bodyLen = return_packetLen - return_headerLen
            return_body = buf[16:return_packetLen]  # 返回的消息
            if bodyLen <= 0:
                return
            if return_ver == 0:
                # 这里做回调
                # print("====> callback:", return_body.decode('utf-8'))
                return return_body.decode('utf-8')
            elif return_ver == 2:
                # 解压
                return_body = zlib.decompress(return_body)
                bodyLen = len(return_body)
                offset = 0
                while offset < bodyLen:
                    cmdSize = struct.unpack('>i', return_body[offset:offset + 4])[0]
                    if offset + cmdSize > bodyLen:
                        return
                    newProto = Proto()
                    newProto.unpack(return_body[offset: offset + cmdSize])
                    offset += cmdSize
            else:
                return


class BliveWebsocket:

    def __init__(self, wss_link, auth_body):
        """
        连接B站弹幕服务器

        :param wss_link: websocket地址
        :param auth_body: app_start里返回的auth_body
        """
        self.wss_link = wss_link
        self.func = None
        self.proto = Proto()
        self.proto.body = auth_body

    async def heartbeat(self, ws) -> None:
        """
        自动弹幕心跳

        :param ws:
        :return:
        """
        while True:
            await asyncio.sleep(20)
            print('发送心跳')
            self.proto.op = 2
            await ws.send(self.proto.pack())

    async def connect(self) -> None:
        """
        连接弹幕服务器

        :return: None
        """
        async with websockets.connect(self.wss_link) as ws:
            self.proto.op = 7
            buf = self.proto.pack()
            await ws.send(buf)
            asyncio.create_task(self.heartbeat(ws))
            while True:
                greeting = await ws.recv()
                msg = self.proto.unpack(greeting)
                # print(f"< {msg}")
                if msg:
                    msg = json.loads(msg)
                    self.func(msg)

    def set_on_message(self, func) -> None:
        """
        设置弹幕回调函数

        :param func: 自己写的函数, func(msg: dict)
        :return: None
        """
        self.func = func


if __name__ == '__main__':
    blive_websocket = BliveWebsocket('wss://broadcastlv.chat.bilibili.com:443/sub',
                                     '{"roomid":24701480,"protover":2,"uid":5247777763813928,"key":"odwDXbFVYR8ubO45WcV4vfQuNpJJABuD1jUdnKk95OPX3IGWg1nqtTHY7WC__S6N-4X68ksmj4S-44Sc_gUirzZTBddvhBzlI7mHKtMV6NKZsE6l4hZcrkp8WHo-maQORuviNn7PumtEgtM3lyl53LJiPOMEuZY=","group":"open"}')
    blive_websocket.set_on_message(lambda x: print(x))
    asyncio.get_event_loop().run_until_complete(blive_websocket.connect())
