"""
💕 情侣互动应用 - 双端版本
支持两个用户在不同设备上独立输入，通过云端（GitHub）同步数据
"""

import streamlit as st
from openai import OpenAI
from datetime import datetime, date
import json
import os
import hashlib
import base64
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# 🔑 GitHub 云端存储模块（替代本地 JSON）
# ═══════════════════════════════════════════════════════════════════

class GitHubStorage:
    """使用 GitHub 存储数据，实现多设备同步"""
    
    def __init__(self, token: str, owner: str, repo: str, branch: str = "main"):
        """
        token: GitHub Personal Access Token
        owner: 仓库所有者
        repo: 仓库名称
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def read_file(self, file_path: str) -> dict:
        """从 GitHub 读取文件"""
        try:
            import requests
            url = f"{self.base_url}/{file_path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data['content']).decode('utf-8')
                return {
                    'success': True,
                    'data': json.loads(content),
                    'sha': data['sha']
                }
            elif response.status_code == 404:
                return {'success': True, 'data': [], 'sha': None}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def write_file(self, file_path: str, data: dict, message: str) -> bool:
        """向 GitHub 写入文件"""
        try:
            import requests
            # 先读取现有文件以获取 SHA
            existing = self.read_file(file_path)
            
            url = f"{self.base_url}/{file_path}"
            content = base64.b64encode(
                json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
            ).decode('utf-8')
            
            payload = {
                "message": message,
                "content": content,
                "branch": self.branch
            }
            
            if existing.get('sha'):
                payload['sha'] = existing['sha']
            
            response = requests.put(url, headers=self.headers, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            st.error(f"GitHub 写入失败: {str(e)}")
            return False

# ═══════════════════════════════════════════════════════════════════
# 📄 页面配置
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="💕 我们的故事 - 双端版",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# 🎨 全局样式
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fff5f5 0%, #fff9f0 50%, #fdf6ff 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffe4e8 0%, #fff0e8 100%);
}

h1 { color: #c0395a !important; }
h2, h3 { color: #8b3a52 !important; }

.user-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
    margin: 8px 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.user-badge.active {
    background: linear-gradient(135deg, #e8607a, #c0395a);
    color: white;
    box-shadow: 0 4px 12px rgba(192,57,90,0.3);
}

.user-badge.inactive {
    background: rgba(200,100,120,0.1);
    color: #8b3a52;
    border: 2px solid #f3b8c4;
}

.sync-box {
    background: linear-gradient(135deg, #ffe8ee, #fff5e8);
    border: 2px solid #f3b8c4;
    border-radius: 16px;
    padding: 20px;
    margin: 16px 0;
}

.partner-message {
    background: rgba(255,255,255,0.9);
    border-left: 4px solid #e8607a;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
}

.stButton > button {
    background: linear-gradient(135deg, #e8607a, #c0395a) !important;
    color: white !important;
    border-radius: 25px !important;
}

.info-box {
    background: linear-gradient(135deg, #fff0f5, #fff8f0);
    border: 1.5px dashed #f3b8c4;
    border-radius: 14px;
    padding: 16px;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🔧 工具函数
# ═══════════════════════════════════════════════════════════════════

def get_client():
    """获取 DeepSeek AI 客户端"""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def chat(client, prompt: str, max_tokens: int = 1000) -> str:
    """非流式调用"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def days_together(anniversary: date) -> int:
    """计算在一起多少天"""
    return (date.today() - anniversary).days

def get_github_storage():
    """获取 GitHub 存储实例"""
    if not all([
        st.session_state.get("github_token"),
        st.session_state.get("github_owner"),
        st.session_state.get("github_repo")
    ]):
        return None
    
    return GitHubStorage(
        token=st.session_state.get("github_token"),
        owner=st.session_state.get("github_owner"),
        repo=st.session_state.get("github_repo")
    )

# ═══════════════════════════════════════════════════════════════════
# 📌 侧边栏 - 配置和用户选择
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# 💕 我们的故事")
    
    st.markdown("## 👥 选择你的身份")
    
    # 用户选择（重要：这决定了当前登录的用户）
    current_user = st.radio(
        "你是谁？",
        ["🚗 柴司机", "👑 耶公主"],
        key="current_user",
        label_visibility="collapsed"
    )
    
    # 显示当前用户状态
    if current_user == "🚗 柴司机":
        st.success("✅ 已登录为柴司机")
        st.session_state.current_username = "柴司机"
        st.session_state.partner_username = "耶公主"
    else:
        st.success("✅ 已登录为耶公主")
        st.session_state.current_username = "耶公主"
        st.session_state.partner_username = "柴司机"
    
    st.divider()
    
    st.markdown("## 📅 关于我们")
    anniversary = st.date_input(
        "💍 在一起的日子",
        value=date(2023, 9, 26),
        key="anniversary"
    )
    days = days_together(anniversary)
    
    st.metric("🌹 在一起", f"{days} 天", border=True)
    
    st.divider()
    
    st.markdown("## 🔑 API 配置")
    
    # DeepSeek API Key
    st.markdown("**DeepSeek API**")
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-xxxxx",
        key="api_key",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("## ☁️ GitHub 云端配置")
    st.info("💡 用于多设备数据同步（可选）")
    
    github_token = st.text_input(
        "GitHub Token",
        type="password",
        placeholder="ghp_xxxxx",
        key="github_token",
        help="在 GitHub > Settings > Developer settings > Personal access tokens 创建",
        label_visibility="collapsed"
    )
    
    github_owner = st.text_input(
        "GitHub 用户名/组织",
        placeholder="0753YUDI",
        key="github_owner",
        label_visibility="collapsed"
    )
    
    github_repo = st.text_input(
        "仓库名称",
        placeholder="love-app",
        key="github_repo",
        label_visibility="collapsed"
    )
    
    if github_token and github_owner and github_repo:
        st.success("✅ GitHub 已配置")
    else:
        st.warning("⚠️ GitHub 未配置（本地模式）")

# ═══════════════════════════════════════════════════════════════════
# 🏠 主页面
# ═══════════════════════════════════════════════════════════════════

st.markdown(f"# 💕 {st.session_state.current_username} & {st.session_state.partner_username}")
st.markdown(f"#### 今天是 {date.today().strftime('%Y年%m月%d日')} · 在一起第 **{days}** 天 🌹")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="text-align: center; padding: 16px; background: rgba(200,100,120,0.05); border-radius: 12px;">
    <p style="font-size: 0.9rem; color: #666;">👤 当前用户</p>
    <p style="font-size: 1.3rem; color: #c0395a; font-weight: bold;">{st.session_state.current_username}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: 16px; background: rgba(200,100,120,0.05); border-radius: 12px;">
    <p style="font-size: 0.9rem; color: #666;">💬 对方</p>
    <p style="font-size: 1.3rem; color: #8b3a52; font-weight: bold;">{st.session_state.partner_username}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════════════
# 💬 双向对话区域
# ═══════════════════════════════════════════════════════════════════

st.markdown("## 💌 我想说...")

# 输入框
message_input = st.text_area(
    "输入你的想法、感受、每日碎语...",
    placeholder=f"亲爱的{st.session_state.partner_username}，我想告诉你...",
    height=120,
    key="message_input"
)

col_send, col_sync = st.columns([3, 1])

with col_send:
    if st.button("💌 发送给对方", use_container_width=True):
        if not message_input:
            st.warning("请输入内容再发送")
        else:
            storage = get_github_storage()
            
            if storage:
                # 云端模式：保存到 GitHub
                file_path = "data/messages.json"
                result = storage.read_file(file_path)
                
                if result['success']:
                    messages = result['data']
                else:
                    messages = []
                
                # 添加新消息
                messages.append({
                    "from": st.session_state.current_username,
                    "to": st.session_state.partner_username,
                    "content": message_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 保存到 GitHub
                if storage.write_file(
                    file_path,
                    messages,
                    f"💌 {st.session_state.current_username} 发来一条消息"
                ):
                    st.success("✅ 消息已发送到云端！对方刷新后可以看到")
                    st.session_state.message_input = ""
                    st.rerun()
                else:
                    st.error("❌ 发送失败，请检查 GitHub 配置")
            else:
                # 本地模式：仅保存到 session state
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                
                st.session_state.messages.append({
                    "from": st.session_state.current_username,
                    "to": st.session_state.partner_username,
                    "content": message_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.info("⚠️ 已保存到本地（未同步到云端）\n💡 请配置 GitHub 以启用多设备同步")
                st.session_state.message_input = ""
                st.rerun()

with col_sync:
    if st.button("🔄 刷新", use_container_width=True):
        st.rerun()

st.divider()

# ═══════════════════════════════════════════════════════════════════
# 👀 查看对方的消息
# ═══════════════════════════════════════════════════════════════════

st.markdown("## 💘 对方说...")

storage = get_github_storage()

if storage:
    # 从 GitHub 读取消息
    result = storage.read_file("data/messages.json")
    messages = result['data'] if result['success'] else []
else:
    # 从本地 session state 读取
    messages = st.session_state.get("messages", [])

# 筛选发送给当前用户的消息
partner_messages = [
    msg for msg in messages 
    if msg['to'] == st.session_state.current_username
]

if partner_messages:
    st.success(f"📬 收到 {len(partner_messages)} 条来自 {st.session_state.partner_username} 的消息")
    
    for msg in reversed(partner_messages):  # 倒序显示，最新的在上面
        timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%m-%d %H:%M")
        st.markdown(f"""
        <div class="partner-message">
            <p style="color: #c0395a; font-weight: bold; margin: 0 0 8px 0;">
                💌 {msg['from']} - {timestamp}
            </p>
            <p style="color: #4a2030; margin: 0; line-height: 1.8; font-size: 1.05rem;">
                {msg['content']}
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(f"💭 还没有来自 {st.session_state.partner_username} 的消息\n等待对方的消息吧～")

st.divider()

# ═══════════════════════════════════════════════════════════════════
# 📋 每日一问（共同回答）
# ═══════════════════════════════════════════════════════════════════

st.markdown("## 💬 每日一问")

# 初始化状态
if "daily_q" not in st.session_state:
    st.session_state.daily_q = "如果可以和我重新认识一次，你希望在什么场景下相遇？"
if "daily_answers" not in st.session_state:
    st.session_state.daily_answers = {}

# 显示问题
st.markdown(f"""
<div style="background: linear-gradient(135deg, #ffe8ee, #fff5e8); border-radius: 16px; 
            padding: 24px; border: 2px solid #f3b8c4; text-align: center;">
    <p style="color: #c0395a; font-size: 0.9rem; margin: 0 0 12px 0;">
        📅 {date.today().strftime('%Y年%m月%d日')} · 今日问题
    </p>
    <p style="color: #8b3a52; font-size: 1.3rem; line-height: 1.8; margin: 0;">
        "{st.session_state.daily_q}"
    </p>
</div>
""", unsafe_allow_html=True)

# 输入答案
answer = st.text_area(
    f"🚗 {st.session_state.current_username} 的回答",
    placeholder="输入你对这个问题的想法...",
    height=100,
    key="daily_answer_input",
    label_visibility="collapsed"
)

if st.button("✅ 提交我的答案"):
    if answer:
        st.session_state.daily_answers[st.session_state.current_username] = {
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        st.success("✅ 你的答案已保存")
        st.session_state.daily_answer_input = ""
        st.rerun()
    else:
        st.warning("请输入答案")

# 显示两人的答案对比
st.markdown("### 💕 你们的回答")

col_a1, col_a2 = st.columns(2)

with col_a1:
    if "柴司机" in st.session_state.daily_answers:
        answer_data = st.session_state.daily_answers["柴司机"]
        st.markdown(f"""
        <div class="partner-message">
            <p style="font-weight: bold; color: #c0395a;">🚗 柴司机</p>
            <p>{answer_data['answer']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🚗 柴司机 还未回答...")

with col_a2:
    if "耶公主" in st.session_state.daily_answers:
        answer_data = st.session_state.daily_answers["耶公主"]
        st.markdown(f"""
        <div class="partner-message">
            <p style="font-weight: bold; color: #c0395a;">👑 耶公主</p>
            <p>{answer_data['answer']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👑 耶公主 还未回答...")

# ═══════════════════════════════════════════════════════════════════
# 📝 使用说明
# ═══════════════════════════════════════════════════════════════════

with st.expander("📖 使用说明"):
    st.markdown("""
    ### 💕 这是什么？
    一个为情侣设计的互动应用，支持两个用户在不同设备上独立使用。
    
    ### 🚀 如何使用？
    
    **设置阶段（第一次使用）：**
    1. **侧边栏** → 选择你的身份（柴司机或耶公主）
    2. **API 配置** → 输入 DeepSeek API Key（用于 AI 功能）
    3. **GitHub 配置**（可选但推荐）
       - 创建 GitHub Personal Access Token（有 repo 权限）
       - 输入你的 GitHub 用户名和仓库名
    
    **日常使用：**
    1. **💌 发送消息** → 在输入框中写下想说的话，点击"发送给对方"
    2. **👀 查看消息** → 自动显示对方发来的所有消息
    3. **💬 每日一问** → 回答问题，查看对方的回答
    4. **🔄 刷新** → 获取最新的数据
    
    ### 🔄 数据同步
    
    **有 GitHub 配置：**
    - 消息自动保存到云端
    - 对方刷新页面即可看到新消息
    - 支持跨设备、离线同步
    
    **无 GitHub 配置：**
    - 消息仅保存到浏览器本地
    - 需要在同一设备或同步浏览器数据
    
    ### 🔐 隐私和安全
    - API Key 只存储在你的浏览器，不上传
    - GitHub Token 只用于读写你的仓库
    - 所有数据都在你的控制下
    """)

st.divider()

st.markdown("""
<p style="text-align: center; color: #c0395a; font-weight: bold; margin-top: 32px;">
💕 希望这个应用能让你们更亲近 💕
</p>
""", unsafe_allow_html=True)
