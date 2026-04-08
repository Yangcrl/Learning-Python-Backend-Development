"""
Locust压测脚本
用于测试秒杀接口的性能
"""

from locust import HttpUser, task, between
import random


class SeckillUser(HttpUser):
    """
    秒杀用户类
    """
    # 等待时间（1-3秒）
    wait_time = between(1, 3)
    
    @task
    def test_seckill(self):
        """
        测试秒杀接口
        """
        # 活动ID（根据实际情况修改）
        activity_id = 1
        
        # 发送秒杀请求
        response = self.client.post(
            f"/api/seckill/{activity_id}",
            headers={"Content-Type": "application/json"},
            json={}
        )
        
        # 检查响应状态
        if response.status_code == 200:
            print(f"秒杀成功: {response.json()}")
        else:
            print(f"秒杀失败: {response.status_code}, {response.text}")


if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py --host=http://localhost")
