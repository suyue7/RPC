import argparse
import json
import socket
from typing import Any, Callable, Dict, List
from server import RPCMessage
from server import RPCMessage


class RPCClient:
    def __init__(self, host: str, port: int):
        self.host = host  # 服务器的IP地址
        self.port = port  # 服务器的端口号
        self.timeout = 5
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_client()

    def init_client(self):
        try:
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(self.timeout)
        except socket.error as e:
            print(f"Failed to connect to {self.host}:{self.port} - {e}")
            raise

    def send_request(self, request):
        try:
            # print("request: ", request)
            self.socket.sendall(request.encode())
            response = self.socket.recv(1024)
            # print("response: ", response)
            return response
        except (socket.timeout, socket.error) as e:
            self.init_client()  # 尝试重新连接
            self.socket.sendall(request.encode())
            response = self.socket.recv(1024)
            return response

    def rpc_find(self, service_name):
        # print(1)
        # request = RPCMessage.serialize(RPCMessage('find_service', service_name))
        request = json.dumps({"method": 'find_service', "service_name": service_name, "params": []})
        # print(2)
        try:
            response = self.send_request(request)
            response_data = json.loads(response.decode())
            # print("response_data: ", response_data)
            if response_data:
                return response_data
            else:
                return None
        except Exception as e:
            print(f"查找失败: {e}")
            return None, None

    def rpc_list(self):
        request = RPCMessage.serialize(RPCMessage('list_services',  []))
        try:
            response = self.send_request(request)
            response_data = json.loads(response.decode())
            return response_data
        except Exception as e:
            print(f"查找失败: {e}")
            return []

    def rpc_call(self, service_name, params):
        try:

            # 查找服务
            # find_request = RPCMessage.serialize(RPCMessage('find_service', service_name))
            find_request = json.dumps({"method": 'find_service', "service_name": service_name, "params": []})
            find_response = self.send_request(find_request)
            find_response_data = json.loads(find_response.decode())
            # python server.py -l 127.0.0.1 -p 255print(find_response_data)
            find_response_data = find_response_data[0]
            # print(find_response_data)

            if find_response_data:
                service_addr = find_response_data['service_addr']
                service_port = find_response_data['service_port']
                print("addr: ", service_addr)
                print("port: ", service_port)
                #
                # print("params: ", params)

                # 调用服务
                service_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                service_socket.settimeout(5)
                service_socket.connect((service_addr, service_port))
                call_request = json.dumps({"method": 'call_service', "service_name": service_name, "params": params})
                # print("call_request: ", call_request)
                service_socket.sendall(call_request.encode())
                call_response = service_socket.recv(1024)
                # service_socket.close()
                call_response_data = json.loads(call_response.decode())
                # print("call_response: ", call_response_data)

                if 'result' in call_response_data:
                    return call_response_data['result']
                else:
                    print(f"Error calling service {service_name}")
                    return None

            else:
                print(f"Service {service_name} not found.")
                return None
        except Exception as e:
            print(f"Error during RPC call: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='RPC Client')
    parser.add_argument('-i', type=str, required=True, help='服务端的IP地址')
    parser.add_argument('-p', type=int, required=True, help='服务端的端口号')
    # 111
    # parser.add_argument('--list', action='store_true', help='获取所有可用的服务列表')
    # parser.add_argument('--find', type=str, help='查找特定的服务')
    # parser.add_argument('--call', type=str, help='调用特定的服务')

    args = parser.parse_args()

    # 创建RPC客户端
    rpc_client = RPCClient(args.i, args.p)


    print("\n请输入以下选项来操作：")
    print("1. 输入 '--list' 获取所有服务列表")
    print("2. 输入 '--find' 查找特定服务")
    print("3. 输入 '--call' 调用特定服务")

    user_input = input("请输入选项: ")

    if user_input.lower() == '--list':
        services = rpc_client.rpc_list()
        print("Available services:", services)
    elif user_input.lower().startswith('--find'):
        input_name = input("请输入需要查找的服务名称：")
        response = rpc_client.rpc_find(input_name)
        if response:
            print(response)
        else:
            print(f"Service {input_name.strip()} not found.")
    elif user_input.lower().startswith('--call'):
        input_name = input("请输入需要调用的服务名称：")
        params = input("请输入参数，若有多个请用逗号隔开：").split(',')
        params = [float(param.strip()) for param in params]
        # print("params: ", params)
        result = rpc_client.rpc_call(input_name.strip(), params)
        if result is not None:
            print(f"Result from calling {input_name.strip()}: {result}")
    else:
        print("选项无效，请重新输入。")


if __name__ == "__main__":
    main()
