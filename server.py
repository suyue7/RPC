import json
import threading
import argparse
import socket

from rpc import ServiceRegistry
from typing import Any, Callable, Dict, List


# RPC消息类，用于封装RPC请求和响应
class RPCMessage:
    def __init__(self, method: str, params: List[Any]):
        self.method = method  # 请求的方法名
        self.params = params  # 方法的参数列表

    # 序列化，将消息转换为JSON字符串
    def serialize(self) -> str:
        return json.dumps({
            'method': self.method,
            'params': self.params
        })

    # 反序列化，将JSON字符串转换为RPCMessage对象
    @staticmethod
    def deserialize(message: str) -> 'RPCMessage':
        data = json.loads(message)

        return RPCMessage(data['method'], data['params'])


# RPC服务端基类，负责注册和获取服务
class RPCServer:
    def __init__(self):
        self.services: Dict[str, Callable] = {}  # 存储服务的字典

    # 注册服务，name为服务名，func为服务对应的函数
    def register_service(self, name: str, func: Callable):
        self.services[name] = func

    # 获取服务，根据服务名返回对应的函数
    def get_service(self, name: str) -> Callable:
        return self.services.get(name)


# RPC服务端处理程序，负责处理客户端请求
class RPCServerHandler:
    def __init__(self, rpc_server: RPCServer, host: str, port: int):
        self.registry = ServiceRegistry()
        self.registry.__dict__=registry.__dict__
        # print("services: ", self.registry.services)
        self.rpc_server = rpc_server
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))  # 绑定IP地址和端口号
        # self.socket.listen(10)
        self.socket.listen()  # 开始监听

    # 处理单个客户端连接
    def handle_client(self, conn):
        # print(6)
        with conn:
            try:
                # 此处折叠实现代码

                data = conn.recv(1024)  # 接收客户端数据
                # print(8)
                # print("data: ", data)
                if data:
                    response = []
                    message = json.loads(data.decode())
                    # print("message: ", message)
                    # message = RPCMessage.deserialize(data.decode())  # 反序列化请求消息
                    # print(222)
                    # request = self.rpc_server.get_service(message.method)  # 获取服务
                    request = message['method']
                    # print("request: ", request)
                    # 111
                    if request == 'list_services':
                        # 如果客户端请求列出所有服务
                        # print(333)
                        services = self.registry.list()
                        # print("services: ", services)
                        response = [{'services': services}]
                    elif request == 'find_service':
                        # 如果客户端请求查找特定服务
                        service_name = message['service_name']  # 假设客户端在参数列表中传递了服务名
                        # print("message.params[0]: ", service_name)
                        if not service_name:
                            response = [{'error': '请给出服务名称'}]
                        else:
                            service_info = self.registry.discover(str(service_name))
                            # print("service_info: ", service_info)
                            if service_info:
                                response = [{'service_addr': service_info['address'], 'service_port': service_info['port']}]
                                # print("response: ", response)
                            else:
                                response = [{'error': '该服务不存在'}]
                    elif request == 'call_service':
                        # 如果客户端请求调用特定服务
                        service_name = message['service_name']
                        params = message['params']
                        # print("service_name: ", service_name)
                        # print("params: ", params)
                        if not service_name:
                            response = {'error': '请给出服务名称'}
                        else:
                            service_info = self.registry.discover(service_name)
                        if service_info:
                            service_func = service_info['func']
                            try:
                                result = service_func(*params)
                                response = {'result': result}
                            except Exception as e:
                                response = [{'error': str(e)}]
                        else:
                            response = [{'error': '该服务不存在'}]

                    # 发送响应给客户端
                    response_message = json.dumps(response)
                    conn.sendall(response_message.encode())
            except socket.timeout:
                print("处理客户端请求超时")
            except Exception as e:
                print(f"处理客户端请求异常：{e}")

    # 启动服务器，监听客户端连接
    def start(self):
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        while True:
            print(f"服务器监听在 {self.host}:{self.port}")
            conn, _ = self.socket.accept()  # 接受客户端连接
            # print(10)
            threading.Thread(target=self.handle_client, args=(conn,)).start()  # 启动新线程处理客户端请求


# def get_registry():
#     if not hasattr(get_registry, "registry"):
#         get_registry.registry = ServiceRegistry()
#     return get_registry.registry


# 示例服务函数，计算两个数的和
def add(x, y):
    return x + y


# 示例服务函数，计算两个数的积
def multiply(x, y):
    return x * y


# 示例服务函数，计算两个数的差
def subtract(x, y):
    return x - y


# 示例服务函数，计算两个数的商
def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y


def find_max(x, y):
    return max(x, y)


def find_min(x, y):
    return min(x, y)


def increase(x):
    return x+1


def decrease(x):
    return x-1


def square(x):
    return x*x


def cube(x):
    return x*x*x


# 创建RPC服务器
rpc_server = RPCServer()

# rpc_server.register_service('add', add)
# rpc_server.register_service('multiply', multiply)
# rpc_server.register_service('subtract', subtract)
# rpc_server.register_service('divide', divide)
# rpc_server.register_service('find_max', find_max)
# rpc_server.register_service('find_min', find_min)
# rpc_server.register_service('increase', increase)
# rpc_server.register_service('decrease', decrease)
# rpc_server.register_service('square', square)
# rpc_server.register_service('cube', cube)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RPC Server')
    parser.add_argument('-l', type=str, default='0.0.0.0', help='服务端监听的IP地址')
    parser.add_argument('-p', type=int, required=True, help='服务端监听的端口号')
    args = parser.parse_args()

    # 创建服务注册中心并注册服务
    registry = ServiceRegistry()
    registry.register('add', add, args.l, args.p)
    registry.register('multiply', multiply, args.l, args.p)
    registry.register('subtract', subtract, args.l, args.p)
    registry.register('divide', divide, args.l, args.p)
    registry.register('find_max', find_max, args.l, args.p)
    registry.register('find_min', find_min, args.l, args.p)
    registry.register('increase', increase, args.l, args.p)
    registry.register('decrease', decrease, args.l, args.p)
    registry.register('square', square, args.l, args.p)
    registry.register('cube', cube, args.l, args.p)
    # print(registry.services)

    # 启动RPC服务器
    rpc_server_handler = RPCServerHandler(rpc_server, args.l, args.p)
    threading.Thread(target=rpc_server_handler.start).start()
