"""
检查秒杀活动状态
"""

from app.core.database import get_db
from app.models import SeckillActivity

# 获取数据库会话
db = next(get_db())
try:
    # 查询所有秒杀活动
    activities = db.query(SeckillActivity).all()
    print('秒杀活动列表:')
    for activity in activities:
        print(f'ID: {activity.id}, 开始时间: {activity.start_time}, 结束时间: {activity.end_time}, 状态: {activity.status}')
finally:
    # 关闭数据库会话
    db.close()
