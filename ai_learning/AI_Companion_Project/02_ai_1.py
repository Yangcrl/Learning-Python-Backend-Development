import streamlit as st
import os
from openai import OpenAI

# 配置页面的默认设置
st.set_page_config(
    # 页面标题
    page_title="AI-伴侣",
    # 图标
    page_icon="👾",
    # 布局
    layout="wide",
    # 侧边栏的初始状态
    initial_sidebar_state="expanded",
    # 菜单
    menu_items={}
)

# 大标题
st.title("AI-伴侣")

# logo
st.logo("resource/logo.png")

# 系统提示词
system_prompt = "你是一名非常可爱的AI助理，你的名字叫小铃，请你使用温柔可爱的语气回答用户的问题。"

# 初始化聊天信息
if 'message' not in st.session_state:
    st.session_state.message = []

# 展示聊天记录
for message in st.session_state.message:
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # else:
    #     st.chat_message("assistant").write(message["content"])

# 消息输入框
prompt = st.chat_input("Say something")
if prompt:
    st.chat_message("user").write(prompt)
    print("-------> 调用AI大模型 提示词：", prompt)
    # 保存用户输入
    st.session_state.message.append({"role":"user", "content":prompt})

    # 调用AI大模型
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    # 输出大模型返回的结果
    print("-------> AI大模型返回结果：", response.choices[0].message.content)
    st.chat_message("assistant").write(response.choices[0].message.content)
    # 保存大模型返回的结果
    st.session_state.message.append({"role":"assistant", "content":response.choices[0].message.content})
