import streamlit as st
import os
import json
from openai import OpenAI
from datetime import datetime

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

# 保存会话信息的函数
def save_session():
    if st.session_state.session_id:
        # 构建新的会话对象
        session_data = {
            "nickname": st.session_state.nickname,
            "character": st.session_state.character,
            "session_id": st.session_state.session_id,
            "message": st.session_state.message
        }

        # 如果sessions目录不存在，则创建一个
        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 生成会话标识函数
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载session目录下的文件
    if os.path.exists("sessions"):
        for filename in os.listdir("sessions"):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True) # 排序, 从新到旧
    return session_list

# 加载指定的会话信息
def load_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            # 读取会话数据
            with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.nickname = session_data["nickname"]
                st.session_state.character = session_data["character"]
                st.session_state.session_id = session_id
                st.session_state.message = session_data["message"]
    except Exception:
        st.error("加载会话数据失败！")

# 删除会话信息函数
def delete_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            os.remove(f"sessions/{session_id}.json") # 删除文件
            # 如果删除的是当前会话，则更新消息列表
            if session_id == st.session_state.session_id:
                st.session_state.message = []
                st.session_state.session_id = generate_session_id()
    except Exception:
        st.error("删除会话数据失败！")

# 大标题
st.title("AI-伴侣")

# logo
st.logo("resource/logo.png")

# 系统提示词
system_prompt = """
    你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。
    规则：
        1.每次只回1条消息
        2.禁止任何场景或状态描述性文字
        3.匹配用户的语言
        4.回复简短，像微信聊天一样
        5.有需要的话可以用👽️🤖等emoji表情
        6.用符合伴侣性格的方式对话
        7.回复的内容，要充分体现伴侣的性格特征
    伴侣性格：
        - %s
    你必须严格遵守上述规则来回复用户。
"""

# 初始化聊天信息
if 'message' not in st.session_state:
    st.session_state.message = []
# 昵称
if 'nickname' not in st.session_state:
    st.session_state.nickname = "小铃"
# 性格
if 'character' not in st.session_state:
    st.session_state.character = "活泼开朗的海南姑娘"
# 会话标识
if 'session_id' not in st.session_state:
    st.session_state.session_id = generate_session_id()

# 展示聊天记录
st.caption(f"会话名称：{st.session_state.session_id}")
for message in st.session_state.message:
    st.chat_message(message["role"]).write(message["content"])


# 左侧的侧边栏
with st.sidebar:
    # 会话信息
    st.sidebar.title("AI控制面板")

    # 新建会话
    if st.button("新建会话", width = "stretch", icon = "✏️"):
        # 1.保存当前的会话信息
        save_session()

        # 2.创建新的会话
        if st.session_state.message: # 如果聊天信息不为空， True，否则， False
            st.session_state.message = []
            st.session_state.session_id = generate_session_id()
            save_session()
            st.rerun() # 重新运行当前页面

    # 会话历史
    st.sidebar.text("历史会话")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 加载会话信息
            if st.button(session, width = "stretch", icon = "📄", type="primary" if session == st.session_state.session_id else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            # 删除会话信息
            if st.button("", width = "stretch", icon = "❌️", key = f"delete_{session}"):
                delete_session(session)
                st.rerun()

    # 分割线
    st.sidebar.divider()

    # 伴侣信息
    st.sidebar.title("伴侣信息")
    # 昵称输入框
    nickname = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nickname)
    if nickname:
        st.session_state.nickname = nickname
    # 性格输入框
    character = st.text_area("性格", placeholder="请输入伴侣性格", value=st.session_state.character)
    if character:
        st.session_state.character = character


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
            {"role": "system", "content": system_prompt % (st.session_state.nickname, st.session_state.character)},
            *st.session_state.message
        ],
        stream=True
    )

    # 输出大模型返回的结果(非流式输出的解析方式)
    # print("-------> AI大模型返回结果：", response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 输出大模型返回的结果(流式输出的解析方式)
    response_message = st.empty() # 创建一个空的组件，用于显示大模型返回的结果

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            response_message.chat_message("assitent").write(full_response)

    # 保存大模型返回的结果
    st.session_state.message.append({"role":"assistant", "content":full_response})

    # 保存会话信息
    save_session()