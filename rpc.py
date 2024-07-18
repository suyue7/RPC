import json
import socket
import threading
from typing import Any, Callable, Dict, List


# 服务注册中心，用于服务的注册和发现
class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}

    # 注册服务，service_name为服务名，service_address为服务地址，service_port为服务端口
    def register(self, service_name: str, service_func, service_address: str, service_port: int):
        self.services[service_name] = {
            'func': service_func,
            'address': service_address,
            'port': service_port
        }

    # 发现服务，根据服务名返回服务的地址和端口
    def discover(self, service_name: str) -> Dict[str, Any]:
        return self.services.get(service_name)

    def unregister(self, service_name):  # 注销服务
        if service_name in self.services:
            del self.services[service_name]

    def list(self):  # 列出所有注册的服务
        return list(self.services.keys())

