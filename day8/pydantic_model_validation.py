from fastapi import FastAPI
from pydantic import BaseModel, validator, root_validator
import re

app = FastAPI()

# 定义带验证的模型
class UserRegister(BaseModel):
    email: str
    password: str
    confirm_password: str

    # 字段级验证，检查邮箱格式
    @validator('email')
    def check_email_format(cls, v):
        # v是用户输入的邮箱值
        if '@' not in v:
            raise ValueError('邮箱格式错误：必须包含@符号')
        return v

    # 字段级验证，检查密码强度
    @validator('password')
    def check_password_strength(cls, v):
        # 规则1：长度大于等于8
        if len(v) < 8:
            raise ValueError('密码强度不够：长度必须大于等于8')
        # 规则2：必须包含字母（正则表达式[a-zA-Z]）
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError('密码强度不够：必须包含字母')
        # 规则3：必须包含数字（正则表达式[0-9]）
        if not re.search(r"[0-9]", v):
            raise ValueError('密码强度不够：必须包含数字')
        # 密码强度通过验证
        return v

    # 字段级验证，检查密码和确认密码是否一致
    @root_validator(skip_on_failure=True)
    def check_password_match(cls, values):
        # values是一个字典，包含所有字段的值
        password = values.get('password')
        confirm_password = values.get('confirm_password')

        if password != confirm_password:
            raise ValueError('密码和确认密码不一致')

        return values

# 注册接口
@app.post('/register/')
async def register(user: UserRegister):
    # 只有所有验证都通过后才会执行这里
    return {
        "code": 200,
        "msg": "注册成功",
        "data": {"email": user.email}
    }
