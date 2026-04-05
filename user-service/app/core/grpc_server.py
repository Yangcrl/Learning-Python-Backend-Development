"""
gRPC服务端实现
"""

import grpc
from concurrent import futures
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.user_service import UserService
import sys
sys.path.append('proto')
import user_pb2, user_pb2_grpc


class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    """
    用户服务gRPC实现
    """
    
    def GetUserById(self, request, context):
        """
        根据ID获取用户
        """
        db = SessionLocal()
        try:
            user = UserService.get_user_by_id(db, request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with ID {request.id} not found")
                return user_pb2.GetUserByIdResponse()
            
            # 构建用户响应
            user_message = user_pb2.User(
                id=user.id,
                username=user.username,
                email="",
                created_time=str(user.created_time)
            )
            return user_pb2.GetUserByIdResponse(user=user_message)
        finally:
            db.close()
    
    def GetUserByUsername(self, request, context):
        """
        根据用户名获取用户
        """
        db = SessionLocal()
        try:
            user = UserService.get_user_by_username(db, request.username)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with username {request.username} not found")
                return user_pb2.GetUserByUsernameResponse()
            
            # 构建用户响应
            user_message = user_pb2.User(
                id=user.id,
                username=user.username,
                email="",
                created_time=str(user.created_time)
            )
            return user_pb2.GetUserByUsernameResponse(user=user_message)
        finally:
            db.close()
    
    def CreateUser(self, request, context):
        """
        创建用户
        """
        from app.schemas.user import UserCreate
        
        db = SessionLocal()
        try:
            # 创建用户
            user_create = UserCreate(
                username=request.username,
                password=request.password
            )
            user = UserService.create_user(db, user_create)
            
            # 构建用户响应
            user_message = user_pb2.User(
                id=user.id,
                username=user.username,
                email="",
                created_time=str(user.created_time)
            )
            return user_pb2.CreateUserResponse(user=user_message)
        except ValueError as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return user_pb2.CreateUserResponse()
        finally:
            db.close()


def start_grpc_server():
    """
    启动gRPC服务
    """
    # 创建gRPC服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 注册服务
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    
    # 绑定端口
    server.add_insecure_port(f"{settings.GRPC_HOST}:{settings.GRPC_PORT}")
    
    # 启动服务
    server.start()
    print(f"gRPC server started on {settings.GRPC_HOST}:{settings.GRPC_PORT}")
    
    return server
