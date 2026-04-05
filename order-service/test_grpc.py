import sys
sys.path.append('proto')
import grpc
from user_pb2 import GetUserByIdRequest, CreateUserRequest
from user_pb2_grpc import UserServiceStub


def test_grpc_client():
    # 创建gRPC通道
    channel = grpc.insecure_channel('localhost:50051')
    # 创建服务存根
    stub = UserServiceStub(channel)
    
    # 测试获取用户
    print("Getting user...")
    get_request = GetUserByIdRequest(id=6)
    try:
        get_response = stub.GetUserById(get_request)
        print(f"User retrieved successfully: {get_response.user}")
        print("gRPC服务间通信测试成功！")
    except grpc.RpcError as e:
        print(f"Error getting user: {e}")
    
    # 关闭通道
    channel.close()


if __name__ == "__main__":
    test_grpc_client()
