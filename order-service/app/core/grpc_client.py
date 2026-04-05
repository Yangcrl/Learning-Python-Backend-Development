import grpc
import sys
sys.path.append('proto')
from user_pb2 import GetUserByIdRequest, GetUserByUsernameRequest
from user_pb2_grpc import UserServiceStub

from app.core.config import settings


class UserServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(settings.USER_SERVICE_GRPC_ADDRESS)
        self.stub = UserServiceStub(self.channel)
    
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
