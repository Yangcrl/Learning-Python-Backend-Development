import grpc
import sys
sys.path.append('proto')
from user_pb2 import GetUserByIdRequest, GetUserByUsernameRequest
from user_pb2_grpc import UserServiceStub

from app.core.config import settings

# 导入Consul服务
try:
    sys.path.append('..')
    from High_concurrency_flash_sale_system.app.core.consul_service import consul_service
except Exception as e:
    print(f"Failed to import Consul service: {e}")
    consul_service = None


class UserServiceClient:
    def __init__(self):
        # 从Consul获取user-service地址
        self.service_address = self._get_service_address()
        self.channel = grpc.insecure_channel(self.service_address)
        self.stub = UserServiceStub(self.channel)
    
    def _get_service_address(self):
        """
        从Consul获取user-service地址
        """
        if consul_service:
            address = consul_service.get_service_address("user-service")
            if address:
                # 假设gRPC服务运行在HTTP服务端口+1的端口
                parts = address.split(':')
                if len(parts) == 2:
                    try:
                        port = int(parts[1]) + 1
                        return f"{parts[0]}:{port}"
                    except:
                        pass
        # 如果Consul不可用，使用配置文件中的地址
        return settings.USER_SERVICE_GRPC_ADDRESS
    
    def get_user_by_id(self, user_id: int):
        request = GetUserByIdRequest(id=user_id)
        try:
            response = self.stub.GetUserById(request)
            return response
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return None
    
    def get_user_by_username(self, username: str):
        request = GetUserByUsernameRequest(username=username)
        try:
            response = self.stub.GetUserByUsername(request)
            return response
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return None
    
    def close(self):
        self.channel.close()


user_service_client = UserServiceClient()
