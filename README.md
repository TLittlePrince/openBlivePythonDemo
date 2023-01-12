# openBlivePythonDemo
简单的BiliBili直播开放平台Python Demo
- 可设置新弹幕、新礼物、新舰长、新SC 和 SC撤回事件调用
## 调用流程 (实现在demo.py)
1.实例化OpenBlive类，填入access_key和access_secret

2.调用实例app_start方法，填入app_id和主播身份码

3.保持20s在OpenBlive调用一次心跳

4.实例化BliveWebsocket类，填入从app_start方法得到的wss_link和auth_body

5.调用实例BliveWebsocket里的方法设置消息回调函数 (on_message, on_gift, on_SC, on_SC_del, on_guard)

6.调用实例BliveWebsocket.connect()