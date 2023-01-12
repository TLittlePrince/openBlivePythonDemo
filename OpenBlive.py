import hashlib
import hmac
import json
import random
import time

import requests

from OpenBliveError import get_error_info, OpenBliveError


class OpenBlive:
    base_url = f"https://live-open.biliapi.com/"

    def __init__(self, access_key: str, access_secret: str) -> None:
        self.access_key = access_key  # 申请的access_key
        self.access_secret = access_secret  # 申请的access_secret

    def app_start(self, app_id: [str, int], code: str) -> dict:
        """
        项目开启

        :param app_id: 项目id
        :param code: 用户身份码
        :return: 长连信息、场次信息和主播信息字典
        """
        return self.post_request(api='v2/app/start', params={'code': code, 'app_id': app_id})

    def app_end(self, app_id: [str, int], game_id: str) -> dict:
        """
        项目关闭

        :param app_id: 项目id
        :param game_id: 场次id
        :return: 请求结果
        """
        return self.post_request(api='v2/app/end', params={'app_id': app_id, 'game_id': game_id})

    def send_heartbeat(self, game_id: str) -> dict:
        """
        项目心跳

        :param game_id: 场次id
        :return: 请求结果
        """
        return self.post_request(api='v2/app/heartbeat', params={'game_id': game_id})

    def send_batch_heartbeat(self, game_ids: list) -> dict:
        """
        项目批量心跳

        :param game_ids: 场次id
        :return: 请求结果
        """
        return self.post_request(api='v2/app/batchHeartbeat', params={'game_ids': game_ids})

    def post_request(self, api: str, params: dict) -> dict:
        """
        使用B站官方接口获取数据(https://open-live.bilibili.com/document/doc&tool/auth.html#%E5%8F%82%E8%80%83demo-python3)

        :params: url: 域名之后的链接
        :params: params: 要post的数据, 需包含app_id
        :return: 服务器返回内容
        """
        params = json.dumps(params)
        print(f'传入的params: {params}')

        md5 = hashlib.md5()
        md5.update(params.encode())
        ts = time.time()
        nonce = random.randint(1, 100000) + time.time()
        md5data = md5.hexdigest()
        header_map = {
            "x-bili-timestamp": str(int(ts)),
            "x-bili-signature-method": "HMAC-SHA256",
            "x-bili-signature-nonce": str(nonce),
            "x-bili-accesskeyid": self.access_key,
            "x-bili-signature-version": "1.0",
            "x-bili-content-md5": md5data,
        }
        header_list = sorted(header_map)
        header_str = ''
        for key in header_list:
            header_str = "{0}{1}:{2}\n".format(header_str, key, str(header_map[key]))
        header_str = header_str.rstrip("\n")

        app_secret = self.access_secret.encode()
        data = header_str.encode()
        signature = hmac.new(app_secret, data, digestmod=hashlib.sha256).hexdigest()
        header_map["Authorization"] = signature
        header_map["Content-Type"] = "application/json"
        header_map["Accept"] = "application/json"
        r = requests.post(url=f'{self.base_url}{api}', headers=header_map, data=params, verify=False)
        request_status_code = r.status_code  # 请求状态(网络) 200 ok
        content = json.loads(r.content.decode())
        real_status_code = content['code']  # 真实请求状态(服务器) 0 ok
        print(f'网络请求状态码: {request_status_code}, 服务器返回状态码: {real_status_code}, 返回内容: {content}')
        info = get_error_info(real_status_code)
        if info['code']:
            raise OpenBliveError(info)
        return content


if __name__ == '__main__':
    a_key = ""
    a_secret = ""
    openBlive = OpenBlive(a_key, a_secret)
    openBlive.post_request('v2/app/start', {"code": "BLMNUWXVJWU85", "app_id": 1649539569084})
