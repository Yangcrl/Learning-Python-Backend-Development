"""
Consul服务注册与发现模块
"""

import consul
import time
from typing import Optional, Dict, Any


class ConsulService:
    """
    Consul服务管理类
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8500):
        """
        初始化Consul客户端
        
        Args:
            host: Consul主机地址
            port: Consul端口
        """
        self.host = host
        self.port = port
        self.client = consul.Consul(host=host, port=port)
    
    def register_service(self, service_name: str, service_id: str, address: str, 
                        port: int, tags: list = None, check: dict = None):
        """
        注册服务到Consul
        
        Args:
            service_name: 服务名称
            service_id: 服务ID
            address: 服务地址
            port: 服务端口
            tags: 服务标签
            check: 健康检查配置
        """
        if tags is None:
            tags = []
        
        if check is None:
            # 默认健康检查配置
            check = {
                'HTTP': f'http://{address}:{port}/health',
                'Interval': '10s',
                'Timeout': '5s'
            }
        
        try:
            self.client.agent.service.register(
                name=service_name,
                id=service_id,
                address=address,
                port=port,
                tags=tags,
                check=check
            )
            print(f"Service {service_name} registered successfully")
        except Exception as e:
            print(f"Failed to register service: {e}")
    
    def deregister_service(self, service_id: str):
        """
        从Consul注销服务
        
        Args:
            service_id: 服务ID
        """
        try:
            self.client.agent.service.deregister(service_id)
            print(f"Service {service_id} deregistered successfully")
        except Exception as e:
            print(f"Failed to deregister service: {e}")
    
    def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        获取服务信息
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务信息字典，包含地址和端口
        """
        try:
            services = self.client.catalog.service(service_name)[1]
            if services:
                return services[0]
            return None
        except Exception as e:
            print(f"Failed to get service: {e}")
            return None
    
    def get_service_address(self, service_name: str) -> Optional[str]:
        """
        获取服务地址
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务地址字符串，格式为 "address:port"
        """
        service = self.get_service(service_name)
        if service:
            return f"{service['ServiceAddress']}:{service['ServicePort']}"
        return None


# 创建Consul服务实例
consul_service = ConsulService()
