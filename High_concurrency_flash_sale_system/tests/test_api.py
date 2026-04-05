"""
API接口单元测试
使用pytest框架测试用户注册、商品查询、秒杀接口
"""

import pytest
import requests
import json
from fastapi.testclient import TestClient
from app.main import app

# 创建测试客户端
client = TestClient(app)

class TestAPI:
    """API接口测试类"""
    
    def test_user_register(self):
        """测试用户注册接口"""
        # 测试数据，使用一个随机的短用户名
        import random
        import string
        # 生成一个6位的随机用户名
        random_username = ''.join(random.choices(string.ascii_lowercase, k=6))
        test_data = {
            "username": random_username,
            "password": "password123",
            "email": f"{random_username}@example.com"
        }
        
        # 发送请求
        response = client.post("/api/auth/register", json=test_data)
        
        # 断言
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == test_data["username"]
    
    def test_user_login(self):
        """测试用户登录接口"""
        # 测试数据
        test_data = {
            "username": "test_user",
            "password": "password123"
        }
        
        # 发送请求
        response = client.post("/api/auth/login", json=test_data)
        
        # 断言
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_get_product(self):
        """测试商品查询接口"""
        # 发送请求
        response = client.get("/api/products/1")
        
        # 断言
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data
        assert "price" in data
        assert "stock" in data
    
    def test_seckill(self):
        """测试秒杀接口"""
        # 发送请求
        response = client.post("/seckill/1")
        
        # 断言
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert "remaining_stock" in data
        assert "message" in data
        assert data["message"] == "秒杀成功"

if __name__ == "__main__":
    pytest.main([__file__])
