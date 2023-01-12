class OpenBliveError(Exception):

    def __init__(self, error_info: dict):
        self.status_code = error_info['code']
        self.describe = error_info['describe']
        self.remarks = error_info['remarks']

    def __str__(self):
        return f'{self.status_code}, {self.describe}, {self.remarks}'


def get_error_info(status_code: str) -> dict:
    """
    获取错误代码对应的表述、备注
    (https://open-live.bilibili.com/document/doc&tool/auth.html#%E5%85%AC%E5%85%B1%E9%94%99%E8%AF%AF%E7%A0%81)

    :param status_code:
    :return: 错误代码及其表述、备注的字典(code, describe, remarks)
    """
    error_code = {
        0: {'describe': '请求成功', 'remarks': 'OK'},
        4000: {'describe': '参数错误', 'remarks': '请检查必填参数，参数大小限制'},
        4001: {'describe': '应用无效', 'remarks': '请检查header的x-bili-accesskeyid是否为空，或者有效'},
        4002: {'describe': '签名异常', 'remarks': '请检查header的Authorization'},
        4003: {'describe': '请求过期', 'remarks': '请检查header的x-bili-timestamp'},
        4004: {'describe': '重复请求', 'remarks': '请检查header的x-bili-nonce'},
        4005: {'describe': '签名method异常', 'remarks': '请检查header的x-bili-signature-method'},
        4006: {'describe': '版本异常', 'remarks': '请检查header的x-bili-version'},
        4007: {'describe': 'IP白名单限制', 'remarks': '请确认请求服务器是否在报备的白名单内'},
        4008: {'describe': '权限异常', 'remarks': '请确认接口权限'},
        4009: {'describe': '接口访问限制', 'remarks': '请确认接口权限及请求频率'},
        4010: {'describe': '接口不存在', 'remarks': '请确认请求接口url/api'},
        4011: {'describe': 'Content-Type不为application/json', 'remarks': '请检查header的Content-Type'},
        4012: {'describe': 'MD5校验失败', 'remarks': '请检查header的x-bili-content-md5'},
        4013: {'describe': 'Accept不为application/json', 'remarks': '请检查header的Accept'},
        5000: {'describe': '服务异常', 'remarks': '请联系B站对接同学'},
        5001: {'describe': '请求超时', 'remarks': '请求超时'},
        5002: {'describe': '内部错误', 'remarks': '请联系B站对接同学'},
        5003: {'describe': '配置错误', 'remarks': '请联系B站对接同学'},
        5004: {'describe': '房间白名单限制', 'remarks': '请联系B站对接同学'},
        5005: {'describe': '房间黑名单限制', 'remarks': '请联系B站对接同学'},
        6000: {'describe': '验证码错误', 'remarks': '验证码校验失败'},
        6001: {'describe': '手机号码错误', 'remarks': '检查手机号码'},
        6002: {'describe': '验证码已过期', 'remarks': '验证码超过规定有效期'},
        6003: {'describe': '验证码频率限制', 'remarks': '检查获取验证码的频率'},
        7000: {'describe': '不在游戏内', 'remarks': '当前房间未进行互动游戏'},
        7001: {'describe': '请求冷却期', 'remarks': '上个游戏正在结算中，建议10秒后进行重试'},
        7002: {'describe': '房间重复游戏', 'remarks': '当前房间正在进行游戏,无法开启下一局互动游戏'},
        7003: {'describe': '心跳过期', 'remarks': '当前game_id错误或互动游戏已关闭'},
        7004: {'describe': '批量心跳超过最大值', 'remarks': '批量心跳单次最大值为200'},
        7005: {'describe': '批量心跳ID重复', 'remarks': '批量心跳game_id存在重复,请检查参数'},
        7007: {'describe': '身份码错误', 'remarks': '请检查身份码是否正确'},
        8002: {'describe': '项目无权限访问', 'remarks': '确认项目ID是否正确'},
    }
    try:
        return {'code': status_code, **error_code[status_code]}
    except KeyError:
        return {'code': status_code, 'describe': '未定义', 'remark': '不在此表内(未知错误码)'}
