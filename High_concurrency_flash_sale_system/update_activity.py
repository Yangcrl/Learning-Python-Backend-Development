"""
更新秒杀活动时间
"""

from app.core.database import get_db
from app.models import SeckillActivity
from datetime import datetime, timedelta

# 获取数据库会话
db = next(get_db())
try:
    # 查询ID为1的秒杀活动
    activity = db.query(SeckillActivity).filter(SeckillActivity.id == 1).first()
    if activity:
        # 更新开始时间为当前时间
        activity.start_time = datetime.now()
        # 更新结束时间为当前时间后1小时
        activity.end_time = datetime.now() + timedelta(hours=1)
        # 确保状态为进行中
        activity.status = 2
        # 提交更改
        db.commit()
        print(f'秒杀活动已更新: ID={activity.id}, 开始时间={activity.start_time}, 结束时间={activity.end_time}, 状态={activity.status}')
    else:
        print('未找到ID为1的秒杀活动')
finally:
    # 关闭数据库会话
    db.close()
