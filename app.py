"""
💕 我们的故事 - 情侣互动 App（双端版）
支持：云端数据同步、信箱、每日一问（身份隔离）、约会计划、恋爱小说、今天吃什么
"""

import streamlit as st
from openai import OpenAI
from datetime import datetime, date
import json
import os
import hashlib
import base64

# ════════════════════════════════════════════════════════════════════
# 💾 本地配置持久化（GitHub Token / API Key 自动记住）
# ════════════════════════════════════════════════════════════════════

CONFIG_FILE = "local_config.json"

def load_local_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_local_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except:
        pass

# ════════════════════════════════════════════════════════════════════
# 📄 页面配置（必须第一行）
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="💕 柴耶大本营",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
# 🎨 全局样式
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Lato:wght@300;400;700&family=Noto+Serif+SC:wght@400;700&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fff5f5 0%, #fff9f0 50%, #fdf6ff 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffe4e8 0%, #fff0e8 100%);
    border-right: 2px solid #f8c8d0;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

h1 { font-family: 'Pacifico', cursive !important; color: #c0395a !important; }
h2, h3 { font-family: 'Noto Serif SC', serif !important; color: #8b3a52 !important; }
body, p, div, span, label {
    font-family: 'Lato', sans-serif !important;
    color: #4a2030 !important;
}

/* 登录页面 */
.login-container {
    max-width: 480px;
    margin: 0 auto;
    padding: 40px 20px;
}
.login-title {
    text-align: center;
    font-family: 'Noto Serif SC', serif !important;
    font-size: 2.6rem;
    color: #c0395a !important;
    margin-bottom: 8px;
}
.love-declaration {
    background: linear-gradient(135deg, #ffe8ee, #fff5f0);
    border: 1.5px solid #f3b8c4;
    border-radius: 20px;
    padding: 20px 28px;
    text-align: center;
    margin: 28px 0 32px 0;
    font-family: 'Noto Serif SC', serif;
    font-size: 1.08rem;
    color: #8b3a52 !important;
    line-height: 1.9;
    box-shadow: 0 4px 20px rgba(192,57,90,0.10);
}
.love-declaration .decl-label {
    font-size: 0.78rem;
    color: #c0395a !important;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

/* 身份选择卡片 */
.identity-card {
    background: rgba(255,255,255,0.85);
    border: 2px solid #f3b8c4;
    border-radius: 18px;
    padding: 22px 18px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 12px;
}
.identity-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(192,57,90,0.18);
    border-color: #e07090;
}
.identity-card.selected {
    background: linear-gradient(135deg, #ffe0e8, #fff0e8);
    border-color: #c0395a;
    box-shadow: 0 6px 20px rgba(192,57,90,0.22);
}

/* 功能卡片 */
.feature-card {
    background: rgba(255,255,255,0.85);
    border: 1.5px solid #f3b8c4;
    border-radius: 20px;
    padding: 28px 24px;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 20px rgba(192,57,90,0.08);
    margin-bottom: 12px;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(192,57,90,0.18);
    border-color: #e07090;
}
.feature-card h3 { font-size: 1.25rem; margin: 10px 0 6px 0; }
.feature-card p { font-size: 0.9rem; color: #9a6070 !important; margin: 0; }
.feature-emoji { font-size: 2.8rem; }

/* 爱心分隔线 */
.love-divider {
    text-align: center;
    color: #e0889a;
    font-size: 1.1rem;
    letter-spacing: 8px;
    margin: 20px 0;
}

/* 按钮 */
.stButton > button {
    background: linear-gradient(135deg, #e8607a, #c0395a) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 10px 30px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(192,57,90,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(192,57,90,0.4) !important;
}

/* 小说输出 */
.novel-output {
    background: rgba(255,255,255,0.95);
    border: 2px solid #f3b8c4;
    border-radius: 20px;
    padding: 32px;
    font-family: 'Noto Serif SC', serif;
    line-height: 2;
    font-size: 1.05rem;
    color: #3a1525 !important;
    box-shadow: inset 0 2px 12px rgba(192,57,90,0.05);
}

/* 时间轴 */
.timeline-item {
    background: rgba(255,255,255,0.9);
    border-left: 4px solid #e8607a;
    border-radius: 0 16px 16px 0;
    padding: 16px 20px;
    margin: 12px 0;
    box-shadow: 0 2px 12px rgba(192,57,90,0.08);
    line-height: 1.9;
    color: #3a1525 !important;
}

/* 每日一问 */
.daily-question {
    background: linear-gradient(135deg, #ffe8ee, #fff5e8);
    border-radius: 24px;
    padding: 36px 40px;
    text-align: center;
    border: 2px solid #f3b8c4;
    box-shadow: 0 8px 32px rgba(192,57,90,0.12);
}
.daily-question .question-text {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.45rem;
    color: #8b3a52 !important;
    line-height: 1.8;
}

/* 答案卡片 */
.answer-card {
    background: rgba(255,255,255,0.9);
    border-radius: 16px;
    padding: 20px;
    border: 1.5px solid #f3b8c4;
    text-align: center;
}

/* 美食卡片 */
.food-card {
    background: linear-gradient(135deg, #fff5f0, #fff0f5);
    border-radius: 20px;
    padding: 24px;
    border: 1.5px solid #f3b8c4;
    line-height: 1.9;
    color: #3a1525 !important;
}

/* 信箱浮窗 */
.mailbox-fab {
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 9999;
}

/* 消息气泡 */
.msg-bubble-me {
    background: linear-gradient(135deg, #e8607a, #c0395a);
    color: white !important;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 60px;
    font-size: 0.97rem;
    line-height: 1.7;
    box-shadow: 0 3px 12px rgba(192,57,90,0.25);
}
.msg-bubble-partner {
    background: rgba(255,255,255,0.95);
    border: 1.5px solid #f3b8c4;
    color: #4a2030 !important;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 60px 8px 0;
    font-size: 0.97rem;
    line-height: 1.7;
    box-shadow: 0 3px 12px rgba(192,57,90,0.08);
}
.msg-meta {
    font-size: 0.75rem;
    color: #b07080 !important;
    margin: 2px 4px;
}

/* 返回按钮特殊样式 */
.back-btn > div > button {
    background: rgba(200,100,120,0.12) !important;
    color: #c0395a !important;
    box-shadow: none !important;
    border: 1.5px solid #f3b8c4 !important;
    padding: 6px 20px !important;
    font-size: 0.9rem !important;
}

/* 指标卡 */
.metric-love {
    background: linear-gradient(135deg, #ffe0e8, #fff5e0);
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    border: 1px solid #f5c0cc;
}
.metric-love .number {
    font-family: 'Pacifico', cursive;
    font-size: 2.2rem;
    color: #c0395a;
}
.metric-love .label {
    font-size: 0.82rem;
    color: #9a6070;
    margin-top: 4px;
}

/* 输入框 */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border: 1.5px solid #f3b8c4 !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.9) !important;
}

/* 状态提示 */
.status-chip {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 4px;
}
.status-done { background: #d4f0d4; color: #2a6a3a !important; }
.status-wait { background: #fde8ec; color: #9a3050 !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# ☁️ GitHub 云端存储
# ════════════════════════════════════════════════════════════════════

class GitHubStorage:
    def __init__(self, token, owner, repo, branch="main"):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def read_file(self, file_path):
        try:
            import requests
            url = f"{self.base_url}/{file_path}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                return {"success": True, "data": json.loads(content), "sha": data["sha"]}
            elif response.status_code == 404:
                return {"success": True, "data": {}, "sha": None}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, file_path, data, message):
        try:
            import requests
            existing = self.read_file(file_path)
            url = f"{self.base_url}/{file_path}"
            content = base64.b64encode(
                json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            ).decode("utf-8")
            payload = {"message": message, "content": content, "branch": self.branch}
            if existing.get("sha"):
                payload["sha"] = existing["sha"]
            response = requests.put(url, headers=self.headers, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            return False


def get_storage():
    t = st.session_state.get("github_token", "")
    o = st.session_state.get("github_owner", "")
    r = st.session_state.get("github_repo", "")
    if t and o and r:
        return GitHubStorage(t, o, r)
    return None


def cloud_read(path, default):
    s = get_storage()
    if s:
        result = s.read_file(path)
        if result["success"] and result["data"]:
            return result["data"]
    # fallback: local file
    if os.path.exists(path.replace("/", "_")):
        with open(path.replace("/", "_"), "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def cloud_write(path, data, msg="update"):
    s = get_storage()
    if s:
        s.write_file(path, data, msg)
    # also save locally as backup
    local_path = path.replace("/", "_")
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ════════════════════════════════════════════════════════════════════
# 🔧 工具函数
# ════════════════════════════════════════════════════════════════════

def get_client():
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def chat(client, prompt, max_tokens=1000):
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def chat_stream(client, prompt, max_tokens=2500):
    stream = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def days_together(anniversary):
    return (date.today() - anniversary).days


# 每天切换的浪漫宣言（用日期哈希决定）
DECLARATIONS = [
    "就算时间再长，你也永远是我每天睁开眼睛的第一个念头。",
    "遇见你之前，我以为平凡就是全部。遇见你之后，我才知道生活可以这么亮。",
    "我不需要全世界，只需要你刚好也在。",
    "爱你，不是因为你完美，而是因为你让我觉得世界是完整的。",
    "有些话藏在心里说不出口，但我的眼睛一直在替我说。",
    "你笑的时候，我才明白什么叫做心动。",
    "如果爱是一场旅行，我希望你永远坐在我身边的那个位置。",
    "喜欢你，像春天喜欢发芽，像夏天喜欢蝉鸣，是藏不住的事。",
    "每一个普通的日子，因为有你，都变成了值得记住的样子。",
    "你是我人生里，最喜欢的那个意外。",
    "不需要轰轰烈烈，只要你在，柴米油盐也是浪漫。",
    "我想和你一起慢慢变老，一起数清彼此脸上每一条细纹。",
    "你说的每一句话，我都悄悄记着，舍不得忘。",
    "愿意为你做很多事，但最想做的，还是陪在你身边什么都不做。",
    "世界很大，但你把它变小了，小到只剩下我们两个人。",
    "爱你，是我做过最对的决定，不需要原因。",
    "你不知道，你随口说的一句话，我能高兴好几天。",
    "就算我们吵架了，我睡着前想的最后一件事，还是你。",
    "感谢你选择了我，也感谢我鼓起勇气选择了你。",
    "有一种幸福，叫做：今天也和你在一起。",
    "你睡着的样子，是我见过最安心的风景。",
    "我不怕未来，因为未来里有你。",
    "爱一个人，就是连他无聊的时候都觉得可爱。",
    "和你在一起，时间过得太快，我总是想要更多。",
    "如果可以选择，我还是会在那一天，选择向你走过去。",
    "你是我所有情绪的出口，快乐想跟你分享，难过也只想找你。",
    "谢谢你让我知道，被人珍惜是什么感觉。",
    "我喜欢你的一切，包括你不喜欢自己的那些部分。",
    "只要和你在一起，哪里都是值得去的地方。",
    "你是我故事里，我最喜欢的那一章。",
    "爱你，是每天都在发生的小事，也是我一生最重要的事。",
]

def get_today_declaration():
    today_str = date.today().isoformat()
    idx = int(hashlib.md5(today_str.encode()).hexdigest(), 16) % len(DECLARATIONS)
    return DECLARATIONS[idx]


def get_daily_question_seed():
    today_str = date.today().isoformat()
    return int(hashlib.md5(today_str.encode()).hexdigest(), 16) % 10000


# 固定的两个角色名
USER_A = "🚗 柴司机"
USER_B = "👑 耶公主"
USER_A_NAME = "柴司机"
USER_B_NAME = "耶公主"

# ════════════════════════════════════════════════════════════════════
# 🔐 Session state 初始化
# ════════════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state.page = "login"
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# 加载本地保存的配置（首次启动时从文件读取）
_cfg = load_local_config()

if "api_key" not in st.session_state:
    st.session_state.api_key = _cfg.get("api_key", "")
if "github_token" not in st.session_state:
    st.session_state.github_token = _cfg.get("github_token", "")
if "github_owner" not in st.session_state:
    st.session_state.github_owner = _cfg.get("github_owner", "")
if "github_repo" not in st.session_state:
    st.session_state.github_repo = _cfg.get("github_repo", "")
if "mailbox_open" not in st.session_state:
    st.session_state.mailbox_open = False
if "daily_question" not in st.session_state:
    st.session_state.daily_question = ""
if "ai_comment" not in st.session_state:
    st.session_state.ai_comment = ""
if "show_partner_answer" not in st.session_state:
    st.session_state.show_partner_answer = False
if "anniversary" not in st.session_state:
    st.session_state.anniversary = date(2023, 9, 26)


def go(page):
    st.session_state.page = page
    st.rerun()


# ════════════════════════════════════════════════════════════════════
# 📬 信箱数据操作
# ════════════════════════════════════════════════════════════════════

def load_messages():
    return cloud_read("data/messages.json", [])


def save_messages(msgs):
    cloud_write("data/messages.json", msgs, "💌 消息更新")


def get_unread_count(for_user):
    msgs = load_messages()
    return sum(1 for m in msgs if m.get("to") == for_user and not m.get("read", False))


def mark_all_read(for_user):
    msgs = load_messages()
    changed = False
    for m in msgs:
        if m.get("to") == for_user and not m.get("read", False):
            m["read"] = True
            changed = True
    if changed:
        save_messages(msgs)


# ════════════════════════════════════════════════════════════════════
# 📝 每日一问数据操作
# ════════════════════════════════════════════════════════════════════

def load_qa_data():
    return cloud_read("data/qa.json", {})


def save_qa_data(data):
    cloud_write("data/qa.json", data, "💬 每日一问更新")


# ════════════════════════════════════════════════════════════════════
# 🔐 登录页面
# ════════════════════════════════════════════════════════════════════

if st.session_state.page == "login":
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    st.markdown("<div class='login-title'>💕 柴耶大本营</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#b07080; font-size:0.95rem; margin-top:-8px;'>专属情侣互动空间</p>", unsafe_allow_html=True)

    # 每日浪漫宣言
    decl = get_today_declaration()
    today_str = date.today().strftime("%Y年%m月%d日")
    st.markdown(f"""
    <div class='love-declaration'>
        <div class='decl-label'>✦ 今日宣言 · {today_str} ✦</div>
        {decl}
    </div>
    """, unsafe_allow_html=True)

    # 身份选择
    st.markdown("<p style='color:#8b3a52; font-weight:600; margin-bottom:10px; text-align:center;'>你是谁？</p>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        selected_a = st.session_state.current_user == USER_A
        card_class = "identity-card selected" if selected_a else "identity-card"
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='font-size:2.4rem;'>🚗</div>
            <div style='font-weight:700; color:#c0395a !important; margin-top:8px; font-size:1.1rem;'>柴司机</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择 柴司机", key="pick_a", use_container_width=True):
            st.session_state.current_user = USER_A
            st.rerun()

    with col_b:
        selected_b = st.session_state.current_user == USER_B
        card_class = "identity-card selected" if selected_b else "identity-card"
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='font-size:2.4rem;'>👑</div>
            <div style='font-weight:700; color:#c0395a !important; margin-top:8px; font-size:1.1rem;'>耶公主</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择 耶公主", key="pick_b", use_container_width=True):
            st.session_state.current_user = USER_B
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # API Key 输入
    st.markdown("<p style='color:#8b3a52; font-weight:600; margin-bottom:6px;'>🔑 DeepSeek API Key</p>", unsafe_allow_html=True)
    api_input = st.text_input("api_key_input", type="password",
                               placeholder="sk-xxxxx（用于AI功能）" if not st.session_state.api_key else "已保存 ✓（如需修改请重新输入）",
                               label_visibility="collapsed", key="api_key_field")

    # GitHub 同步配置（折叠）
    with st.expander("🌥️ 云端同步配置（可选，用于双设备同步）"):
        # 判断是否已有保存的值
        _has_saved = bool(st.session_state.github_token and st.session_state.github_owner and st.session_state.github_repo)
        if _has_saved:
            st.success(f"✅ 已记住配置：{st.session_state.github_owner}/{st.session_state.github_repo}")
        gh_token_in = st.text_input("GitHub Token", type="password",
                                     placeholder="ghp_xxxxx（已保存，留空不修改）" if st.session_state.github_token else "ghp_xxxxx",
                                     key="github_token_input")
        gh_owner_in = st.text_input("GitHub 用户名",
                                     placeholder=st.session_state.github_owner if st.session_state.github_owner else "your-username",
                                     key="github_owner_input")
        gh_repo_in = st.text_input("仓库名称",
                                    placeholder=st.session_state.github_repo if st.session_state.github_repo else "love-app-data",
                                    key="github_repo_input")
        st.caption("💡 在 GitHub > Settings > Developer settings > Personal access tokens 创建 Token，赋予 repo 权限")

    st.markdown("<br>", unsafe_allow_html=True)

    # 进入按钮
    can_enter = st.session_state.current_user is not None
    if can_enter:
        if st.button("💕 进入我们的小窝", use_container_width=True):
            _changed = False
            if api_input:
                st.session_state.api_key = api_input
                _changed = True
            if gh_token_in:
                st.session_state.github_token = gh_token_in
                _changed = True
            if gh_owner_in:
                st.session_state.github_owner = gh_owner_in
                _changed = True
            if gh_repo_in:
                st.session_state.github_repo = gh_repo_in
                _changed = True
            # 保存到本地文件
            save_local_config({
                "api_key": st.session_state.api_key,
                "github_token": st.session_state.github_token,
                "github_owner": st.session_state.github_owner,
                "github_repo": st.session_state.github_repo,
            })
            go("home")
    else:
        st.info("请先选择你的身份，再进入 💕")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ════════════════════════════════════════════════════════════════════
# 辅助：当前用户信息
# ════════════════════════════════════════════════════════════════════

current_user = st.session_state.current_user or USER_A
is_a = current_user == USER_A
current_name = USER_A_NAME if is_a else USER_B_NAME
partner_name = USER_B_NAME if is_a else USER_A_NAME
partner_user = USER_B if is_a else USER_A

anniversary = st.session_state.anniversary
days = days_together(anniversary)


# ════════════════════════════════════════════════════════════════════
# 📬 信箱浮窗（右下角，全局显示）
# ════════════════════════════════════════════════════════════════════

unread = get_unread_count(current_user)

def render_mailbox_fab():
    fab_label = f"💗 New message ({unread})" if unread > 0 else "💌 信箱"
    if st.button(fab_label, key="mailbox_fab"):
        st.session_state.mailbox_open = not st.session_state.mailbox_open
        if st.session_state.mailbox_open:
            mark_all_read(current_user)
        st.rerun()

# 用 columns 把信箱 FAB 推到右侧
if st.session_state.page != "login":
    top_col1, top_col2, top_col3 = st.columns([6, 2, 2])
    with top_col1:
        st.markdown(f"<span style='color:#c0395a; font-size:0.9rem; font-weight:600;'>👤 {current_user}</span>", unsafe_allow_html=True)
    with top_col2:
        if st.button("🔄 切换身份", key="switch_user"):
            st.session_state.page = "login"
            st.session_state.current_user = None
            st.rerun()
    with top_col3:
        render_mailbox_fab()


# ════════════════════════════════════════════════════════════════════
# 💌 信箱详情（展开时显示）
# ════════════════════════════════════════════════════════════════════

if st.session_state.mailbox_open:
    with st.container():
        st.markdown(f"#### 💌 我们的信箱")
        msgs = load_messages()

        # 发消息
        new_msg = st.text_area("给 ta 写点什么...", height=90, key="new_msg_input",
                                placeholder=f"亲爱的{partner_name}，我想告诉你...")
        col_send, col_close = st.columns([3, 1])
        with col_send:
            if st.button("💌 发送", use_container_width=True, key="send_msg"):
                if new_msg.strip():
                    msgs.append({
                        "from": current_user,
                        "to": partner_user,
                        "content": new_msg.strip(),
                        "timestamp": datetime.now().isoformat(),
                        "read": False
                    })
                    save_messages(msgs)
                    st.success("✅ 已发送！")
                    st.rerun()
                else:
                    st.warning("请输入内容")
        with col_close:
            if st.button("关闭", key="close_mailbox"):
                st.session_state.mailbox_open = False
                st.rerun()

        # 展示收到的消息
        received = [m for m in msgs if m.get("to") == current_user]
        sent = [m for m in msgs if m.get("from") == current_user]

        if received or sent:
            st.markdown("---")
            # 合并排序展示对话流
            all_msgs = [(m, "received") for m in received] + [(m, "sent") for m in sent]
            all_msgs.sort(key=lambda x: x[0]["timestamp"])
            for m, mtype in all_msgs:
                ts = datetime.fromisoformat(m["timestamp"]).strftime("%m-%d %H:%M")
                if mtype == "sent":
                    st.markdown(f"""
                    <div class='msg-bubble-me'>{m['content']}</div>
                    <div class='msg-meta' style='text-align:right;'>我 · {ts}</div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='msg-meta'>{partner_name} · {ts}</div>
                    <div class='msg-bubble-partner'>{m['content']}</div>
                    """, unsafe_allow_html=True)
        else:
            st.info("还没有消息，先发一条给 ta 吧 💕")

    st.markdown("---")


# ════════════════════════════════════════════════════════════════════
# 🏠 首页
# ════════════════════════════════════════════════════════════════════

if st.session_state.page == "home":
    st.markdown(f"<h1 style='text-align:center; font-size:2.6rem;'>💕 {USER_A_NAME} & {USER_B_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#9a6070; font-size:1.05rem;'>今天是 {date.today().strftime('%Y年%m月%d日')} · 在一起第 <b style='color:#c0395a;'>{days}</b> 天 🌹</p>", unsafe_allow_html=True)

    # 纪念日设置（小字）
    with st.expander("⚙️ 设置纪念日 / API / 云端同步"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            new_ann = st.date_input("💍 在一起的日子", value=st.session_state.anniversary, key="ann_input")
            if new_ann != st.session_state.anniversary:
                st.session_state.anniversary = new_ann
                st.rerun()
        with col_s2:
            new_key = st.text_input("🔑 DeepSeek API Key", type="password",
                                     placeholder="已保存 ✓" if st.session_state.api_key else "sk-xxxxx",
                                     key="api_key_home")
            if new_key and new_key != st.session_state.api_key:
                st.session_state.api_key = new_key
                save_local_config({
                    "api_key": st.session_state.api_key,
                    "github_token": st.session_state.github_token,
                    "github_owner": st.session_state.github_owner,
                    "github_repo": st.session_state.github_repo,
                })
        col_s3, col_s4, col_s5 = st.columns(3)
        with col_s3:
            _gh_t = st.text_input("GitHub Token", type="password",
                                   placeholder="已保存 ✓" if st.session_state.github_token else "ghp_xxxxx",
                                   key="github_token_home")
            if _gh_t and _gh_t != st.session_state.github_token:
                st.session_state.github_token = _gh_t
                save_local_config({"api_key": st.session_state.api_key, "github_token": st.session_state.github_token, "github_owner": st.session_state.github_owner, "github_repo": st.session_state.github_repo})
        with col_s4:
            _gh_o = st.text_input("GitHub 用户名",
                                   placeholder=st.session_state.github_owner if st.session_state.github_owner else "your-username",
                                   key="github_owner_home")
            if _gh_o and _gh_o != st.session_state.github_owner:
                st.session_state.github_owner = _gh_o
                save_local_config({"api_key": st.session_state.api_key, "github_token": st.session_state.github_token, "github_owner": st.session_state.github_owner, "github_repo": st.session_state.github_repo})
        with col_s5:
            _gh_r = st.text_input("仓库名称",
                                   placeholder=st.session_state.github_repo if st.session_state.github_repo else "love-app-data",
                                   key="github_repo_home")
            if _gh_r and _gh_r != st.session_state.github_repo:
                st.session_state.github_repo = _gh_r
                save_local_config({"api_key": st.session_state.api_key, "github_token": st.session_state.github_token, "github_owner": st.session_state.github_owner, "github_repo": st.session_state.github_repo})

    st.markdown('<div class="love-divider">✦ ♥ ✦ ♥ ✦</div>', unsafe_allow_html=True)

    # 功能卡片 2x2 + 1 (信箱在右下角FAB，不在这里)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">🗺️</div>
            <h3>约会计划助手</h3>
            <p>输入你们的心情与偏好，规划完美约会行程，还附上专属穿搭建议 ✨</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✨ 开始规划约会", key="btn_date", use_container_width=True):
            go("date_plan")

        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">🍽️</div>
            <h3>今天吃什么</h3>
            <p>解决情侣永恒难题！根据心情和禁忌，帮你们做出美食决定 🥢</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🥢 帮我决定吃什么", key="btn_food", use_container_width=True):
            go("food")

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">📖</div>
            <h3>专属恋爱小说</h3>
            <p>把你们真实的故事交给 AI，生成只属于你们的浪漫小说 💌</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💌 生成我们的故事", key="btn_novel", use_container_width=True):
            go("novel")

        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">💬</div>
            <h3>每日一问</h3>
            <p>每天一个深度问题，让你们更了解彼此，AI 深度分析双方心理 🌙</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌙 查看今日问题", key="btn_qa", use_container_width=True):
            go("daily_qa")

    st.markdown('<div class="love-divider">✦ ♥ ✦ ♥ ✦</div>', unsafe_allow_html=True)

    # ── 相框 + 双时区时钟 ──────────────────────────────────────────
    st.markdown("""
    <style>
    .photo-frame-wrap {
        background: rgba(255,255,255,0.92);
        border: 2.5px solid #f3b8c4;
        border-radius: 24px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 6px 24px rgba(192,57,90,0.10);
        margin-bottom: 16px;
    }
    .photo-frame-inner {
        border: 4px dashed #f3b8c4;
        border-radius: 18px;
        min-height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #fff5f8, #fff0f8);
        margin-bottom: 8px;
    }
    .photo-placeholder {
        color: #d4a0b0;
        font-size: 0.95rem;
        line-height: 2;
    }
    .clock-card {
        background: linear-gradient(135deg, #ffe8ee, #fff5f0);
        border: 1.5px solid #f3b8c4;
        border-radius: 18px;
        padding: 18px 14px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(192,57,90,0.08);
    }
    .clock-label {
        font-family: 'Noto Serif SC', serif;
        font-size: 0.82rem;
        color: #c0395a;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    .clock-time {
        font-family: 'Pacifico', cursive;
        font-size: 1.7rem;
        color: #8b3a52;
        margin: 2px 0 4px 0;
    }
    .clock-date {
        font-size: 0.78rem;
        color: #b07080;
        margin-bottom: 8px;
    }
    .clock-status {
        font-family: 'Noto Serif SC', serif;
        font-size: 0.88rem;
        color: #9a6070;
        line-height: 1.7;
        background: rgba(255,255,255,0.7);
        border-radius: 10px;
        padding: 8px 10px;
        margin-top: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    frame_col, clock_col = st.columns([1.2, 1])

    with frame_col:
        st.markdown('<div class="photo-frame-wrap">', unsafe_allow_html=True)
        st.markdown("<p style='color:#c0395a; font-family:\"Noto Serif SC\",serif; font-size:1rem; margin-bottom:12px; font-weight:700;'>📸 我们的合照</p>", unsafe_allow_html=True)
        uploaded_photo = st.file_uploader("上传合影", type=["jpg", "jpeg", "png", "webp"], key="couple_photo", label_visibility="collapsed")
        if uploaded_photo:
            st.image(uploaded_photo, use_container_width=True)
        else:
            st.markdown("""
            <div class="photo-frame-inner">
                <div class="photo-placeholder">
                    📷<br>点击上方上传<br>我们的合照 💕
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with clock_col:
        from datetime import timezone
        try:
            import zoneinfo
            uk_tz = zoneinfo.ZoneInfo("Europe/London")
            hk_tz = zoneinfo.ZoneInfo("Asia/Hong_Kong")
        except Exception:
            try:
                import pytz
                uk_tz = pytz.timezone("Europe/London")
                hk_tz = pytz.timezone("Asia/Hong_Kong")
            except Exception:
                uk_tz = None
                hk_tz = None

        now_utc = datetime.now(timezone.utc)

        if uk_tz and hk_tz:
            uk_now = now_utc.astimezone(uk_tz)
            hk_now = now_utc.astimezone(hk_tz)
        else:
            # fallback: UK = UTC, HK = UTC+8
            from datetime import timedelta
            uk_now = now_utc
            hk_now = now_utc + timedelta(hours=8)

        uk_h = uk_now.hour
        hk_h = hk_now.hour

        def guess_activity(hour, name):
            if 0 <= hour < 6:
                return f"现在是凌晨啦，{name}可能在呼呼大睡哦 🌙"
            elif 6 <= hour < 9:
                return f"{name}可能刚刚起床，迷迷糊糊地洗漱中 ☕"
            elif 9 <= hour < 12:
                return f"{name}应该在认真工作/学习吧，要加油哦 📚"
            elif 12 <= hour < 14:
                return f"午饭时间！{name}在吃好吃的吗 🍱"
            elif 14 <= hour < 17:
                return f"{name}可能正在努力奋斗中，下午茶时间快到啦 ☕"
            elif 17 <= hour < 19:
                return f"下班啦～{name}可能在回家路上 🚗"
            elif 19 <= hour < 22:
                return f"晚上好！{name}可能在放松休息或者想对方 💕"
            else:
                return f"夜深了，{name}还没睡？快去休息吧 😴"

        # 星期几中文
        weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        uk_wd = weekday_cn[uk_now.weekday()]
        hk_wd = weekday_cn[hk_now.weekday()]

        st.markdown(f"""
        <div class="clock-card" style="margin-bottom:14px;">
            <div class="clock-label">🇬🇧 英国时间 · 耶公主</div>
            <div class="clock-time">{uk_now.strftime('%H:%M')}</div>
            <div class="clock-date">{uk_now.strftime('%Y年%m月%d日')} {uk_wd}</div>
            <div class="clock-status">{guess_activity(uk_h, '耶公主')}</div>
        </div>
        <div class="clock-card">
            <div class="clock-label">🇭🇰 香港时间 · 柴司机</div>
            <div class="clock-time">{hk_now.strftime('%H:%M')}</div>
            <div class="clock-date">{hk_now.strftime('%Y年%m月%d日')} {hk_wd}</div>
            <div class="clock-status">{guess_activity(hk_h, '柴司机')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="love-divider">✦ ♥ ✦ ♥ ✦</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 🗺️ 约会计划
# ════════════════════════════════════════════════════════════════════

elif st.session_state.page == "date_plan":
    if st.button("← 返回首页", key="back_date"):
        go("home")

    st.markdown("<h1>🗺️ 约会计划助手</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>告诉我你们的状态，我来帮你们规划一次专属约会 💝</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    with st.form("date_plan_form"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("📍 城市 / 地区", placeholder="例如：上海、北京三里屯")
            time_avail = st.selectbox("⏰ 可用时间", ["半天（3-4小时）", "全天（6-8小时）", "整个周末"])
            time_period = st.multiselect(
                "🕐 时间段（可多选）",
                ["🌅 早晨", "☀️ 下午", "🌆 晚上", "🌙 深夜"],
                default=["☀️ 下午"]
            )
            budget = st.selectbox("💰 预算范围", ["低（人均100以内）", "中（人均100-300）", "高（人均300+）"])
            weather = st.selectbox("🌤️ 当前天气", ["晴天", "多云", "小雨", "寒冷", "炎热"])

        with col2:
            prefs = st.multiselect(
                "🎯 偏好标签",
                ["户外探索", "美食打卡", "文艺展览", "运动健身", "居家休闲", "购物逛街", "电影演出"],
                default=["美食打卡", "文艺展览"]
            )
            mood1 = st.text_area(f"🚗 {USER_A_NAME} 今天的心情", placeholder="例如：有点累，想安静放松一下...", height=95)
            mood2 = st.text_area(f"👑 {USER_B_NAME} 今天的心情", placeholder="例如：很开心，想出去逛逛！", height=95)

        submitted = st.form_submit_button("✨ 生成约会计划", use_container_width=True)

    if submitted:
        client = get_client()
        if not client:
            st.error("请先在设置里填入 DeepSeek API Key！")
        elif not city:
            st.error("请输入城市！")
        else:
            prefs_str = "、".join(prefs) if prefs else "不限"
            prompt = f"""你是一位了解这对情侣的好朋友，请帮他们规划一次约会，用朋友聊天的口吻来写，别用太正式的文档格式，不要用###、**这些 markdown 符号，写得自然一点，像在给朋友发消息。

情侣信息：
- 他：{USER_A_NAME}，今日心情：{mood1 or "没特别说"}
- 她：{USER_B_NAME}，今日心情：{mood2 or "没特别说"}
- 在一起第 {days} 天

约会条件：
- 城市：{city}
- 时间：{time_avail}
- 时间段：{"、".join(time_period) if time_period else "不限"}
- 预算：{budget}
- 偏好：{prefs_str}
- 天气：{weather}

请包含以下内容（但写法要自然，不要像报告）：
1. 给这次约会起个浪漫的主题
2. 按时间段说说去哪、干什么，给几个贴心小提示
3. 分别给{USER_A_NAME}和{USER_B_NAME}的穿搭建议，说说风格和颜色就好
4. 最后用一句温暖的话结尾，提到两人名字

中文回答，语气自然温暖。"""

            with st.spinner("💕 正在帮你们规划约会..."):
                try:
                    result = chat(client, prompt, max_tokens=2000)
                    st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="timeline-item">{result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                    st.download_button(
                        "⬇️ 保存行程",
                        data=result,
                        file_name=f"约会计划_{date.today()}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"调用失败：{e}")


# ════════════════════════════════════════════════════════════════════
# 📖 恋爱小说
# ════════════════════════════════════════════════════════════════════

elif st.session_state.page == "novel":
    if st.button("← 返回首页", key="back_novel"):
        go("home")

    st.markdown("<h1>📖 专属恋爱小说</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>把你们的故事告诉 AI，生成只属于你们的浪漫小说 💌</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    with st.form("novel_form"):
        experience = st.text_area(
            "🌟 真实的经历",
            placeholder="例如：我们在一个朋友的聚会上认识，那天他一直在角落看书，我鼓起勇气去搭话...",
            height=120
        )
        col1, col2 = st.columns(2)
        with col1:
            feeling2 = st.text_area(
                f"👑 {USER_B_NAME} 的感受",
                placeholder="例如：第一眼看到他就觉得他很特别...",
                height=100
            )
        with col2:
            feeling1 = st.text_area(
                f"🚗 {USER_A_NAME} 的感受",
                placeholder="例如：没想到她会主动来找我说话...",
                height=100
            )
        extra = st.text_area(
            "✨ 额外补充",
            placeholder="特别的细节、想加入的元素、某个场景的描述...",
            height=80
        )
        col3, col4, col5 = st.columns(3)
        with col3:
            style = st.selectbox("🎨 小说风格", ["浪漫言情", "治愈温馨", "童话梦幻", "搞笑甜蜜", "古风雅韵"])
        with col4:
            length = st.selectbox("📏 篇幅", ["短篇（约500字）", "中篇（约1000字）", "长篇（约2000字）"])
        with col5:
            freedom = st.selectbox("🎭 AI 自由发挥", ["低 - 严格还原", "中 - 适当润色", "高 - 大胆创作"])

        submitted = st.form_submit_button("✍️ 生成专属小说", use_container_width=True)

    if submitted:
        client = get_client()
        if not client:
            st.error("请先填入 DeepSeek API Key！")
        elif not experience:
            st.error("请描述你们的真实经历！")
        else:
            freedom_map = {
                "低 - 严格还原": "请严格基于以下内容进行文学润色，不要添加未提及的情节，保持高度忠实于原始经历。",
                "中 - 适当润色": "可以合理补充对话和细节描写，但核心事件和情感走向保持不变，适度增加文学性。",
                "高 - 大胆创作": "以此为灵感自由创作，可以加入戏剧性转折、环境描写、内心独白，大胆发挥想象力。"
            }
            length_map = {"短篇（约500字）": "约500字", "中篇（约1000字）": "约1000字", "长篇（约2000字）": "约2000字"}

            prompt = f"""你是一位才华横溢的言情小说作家，请根据以下真实经历为这对情侣创作一篇专属小说。

人物：
- 男主：{USER_A_NAME}
- 女主：{USER_B_NAME}
- 在一起第 {days} 天

真实经历：
{experience}

{USER_B_NAME} 的感受：
{feeling2 or "未填写"}

{USER_A_NAME} 的感受：
{feeling1 or "未填写"}

额外补充：
{extra or "无"}

创作要求：
- 风格：{style}
- 篇幅：{length_map[length]}
- 自由度：{freedom_map[freedom]}
- 主角名字请使用 {USER_A_NAME} 和 {USER_B_NAME}
- 融合双方的感受，呈现立体的双视角情感描写
- 语言优美，情感细腻，让他们读完会心跳加速

请直接开始写小说正文，不需要任何说明文字。"""

            st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
            novel_placeholder = st.empty()
            novel_text = ""

            try:
                for chunk in chat_stream(client, prompt, max_tokens=2500):
                    novel_text += chunk
                    novel_placeholder.markdown(
                        f'<div class="novel-output">{novel_text.replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True
                    )
                st.download_button(
                    "⬇️ 保存小说",
                    data=novel_text,
                    file_name=f"我们的故事_{date.today()}.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"生成失败：{e}")


# ════════════════════════════════════════════════════════════════════
# 🍽️ 今天吃什么
# ════════════════════════════════════════════════════════════════════

elif st.session_state.page == "food":
    if st.button("← 返回首页", key="back_food"):
        go("home")

    st.markdown("<h1>🍽️ 今天吃什么</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>解决情侣最难的问题，帮你们做决定！🥢</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    with st.form("food_form"):
        col1, col2 = st.columns(2)
        with col1:
            food_city = st.text_input("📍 所在城市", placeholder="例如：上海")
            scene = st.selectbox("🏠 用餐场景", ["出去吃（餐厅）", "点外卖", "在家自己做"])
            food_budget = st.selectbox("💰 今日预算", ["节省（人均50以内）", "普通（人均50-150）", "犒劳自己（人均150+）"])
            mood_food = st.selectbox("😊 今天的心情", ["开心愉快", "有点疲惫", "想犒劳自己", "平淡普通", "需要安慰"])
        with col2:
            avoid1 = st.text_input(f"🚫 {USER_A_NAME} 不吃的", placeholder="例如：香菜、海鲜")
            avoid2 = st.text_input(f"🚫 {USER_B_NAME} 不吃的", placeholder="例如：辣的、羊肉")
            craving = st.text_area("💭 想吃什么方向？", placeholder="例如：想吃点热乎的、想吃甜的...", height=80)

        submitted = st.form_submit_button("🎲 帮我决定！", use_container_width=True)

    if submitted:
        client = get_client()
        if not client:
            st.error("请先填入 DeepSeek API Key！")
        else:
            prompt = f"""你是一个美食决策专家，请帮这对情侣解决"今天吃什么"的难题。

情侣信息：
- {USER_A_NAME} 不吃：{avoid1 or "无禁忌"}
- {USER_B_NAME} 不吃：{avoid2 or "无禁忌"}
- 城市：{food_city or "不限"}
- 用餐场景：{scene}
- 预算：{food_budget}
- 今日心情：{mood_food}
- 想吃的方向：{craving or "没有特别想法"}

请给出3个推荐方案，每个方案包括：
1. 推荐菜系或餐厅类型，起一个有趣的名字
2. 推荐理由，结合今日心情和两人情况，说得有温度
3. 具体推荐菜品2-3个
4. 如果是"在家自己做"，附上一个简单食谱思路

格式清晰，语气活泼温暖，用 emoji 点缀，中文回答。"""

            with st.spinner("🍳 帮你们想今天吃什么..."):
                try:
                    result = chat(client, prompt, max_tokens=1200)
                    st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="food-card">{result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"调用失败：{e}")

        if st.button("🔄 再换一批"):
            st.rerun()


# ════════════════════════════════════════════════════════════════════
# 💬 每日一问（身份隔离 + 互看限制）
# ════════════════════════════════════════════════════════════════════

elif st.session_state.page == "daily_qa":
    if st.button("← 返回首页", key="back_qa"):
        go("home")

    st.markdown("<h1>💬 每日一问</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>每天一个深度问题，让你们更了解彼此 🌙</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    client = get_client()
    today_key = date.today().isoformat()

    # 加载今日问答数据
    qa_data = load_qa_data()
    today_qa = qa_data.get(today_key, {"question": "", "answers": {}, "ai_comment": ""})

    # 生成今日问题（如果没有）
    if not today_qa.get("question"):
        if client:
            seed = get_daily_question_seed()
            category = ["了解彼此内心", "关于未来规划", "童年与成长", "价值观与人生观", "趣味脑洞"][seed % 5]
            gen_prompt = f"""请生成一个适合情侣之间的深度问题，类别是"{category}"。
要求：
- 问题要有深度，能引发真实的思考和分享
- 不能太隐私或令人不适
- 语气温柔，富有情感
- 只输出问题本身，不要任何解释或序号
- 今天的随机种子是 {seed}，请基于此生成不同的问题"""
            with st.spinner("💭 正在生成今日问题..."):
                try:
                    q = chat(client, gen_prompt, max_tokens=100).strip()
                    today_qa["question"] = q
                    qa_data[today_key] = today_qa
                    save_qa_data(qa_data)
                except:
                    today_qa["question"] = "如果可以和我重新认识一次，你希望我们在什么样的场景下相遇？"
        else:
            today_qa["question"] = "如果可以和我重新认识一次，你希望我们在什么样的场景下相遇？"

    question = today_qa.get("question", "")
    answers = today_qa.get("answers", {})

    my_answer_key = USER_A_NAME if is_a else USER_B_NAME
    partner_answer_key = USER_B_NAME if is_a else USER_A_NAME

    my_answered = my_answer_key in answers
    partner_answered = partner_answer_key in answers
    both_answered = my_answered and partner_answered

    # 显示问题
    today_str = date.today().strftime("%Y年%m月%d日")
    st.markdown(f"""
    <div class="daily-question">
        <p style="color:#c0395a; font-size:0.85rem; margin-bottom:12px;">📅 {today_str} · 今日一问</p>
        <p class="question-text">"{question}"</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    # 对方状态提示
    if partner_answered:
        st.markdown(f"""<span class='status-chip status-done'>✅ {partner_name} 已回答</span>
        {'&nbsp;&nbsp;<span class="status-chip status-done">🔓 你也回答后可以查看对方答案</span>' if not my_answered else ''}
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='status-chip status-wait'>⏳ 等待 {partner_name} 回答...</span>", unsafe_allow_html=True)

    if my_answered:
        st.markdown(f"<span class='status-chip status-done'>✅ 你已回答</span>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 我的回答区域
    if not my_answered:
        st.markdown(f"#### ✏️ {current_user} 的回答")
        my_input = st.text_area("", placeholder="写下你对这个问题的想法...", height=130,
                                 key="my_qa_input", label_visibility="collapsed")
        if st.button(f"✅ 提交我的回答", use_container_width=True):
            if my_input.strip():
                answers[my_answer_key] = {
                    "content": my_input.strip(),
                    "timestamp": datetime.now().isoformat()
                }
                today_qa["answers"] = answers
                qa_data[today_key] = today_qa
                save_qa_data(qa_data)
                st.success("✅ 回答已提交！")
                st.rerun()
            else:
                st.warning("请输入你的答案再提交")
    else:
        st.markdown(f"""
        <div class="answer-card">
            <p style="font-weight:700; color:#c0395a;">{current_user} 的回答</p>
            <p style="line-height:1.8;">{answers[my_answer_key]['content']}</p>
        </div>
        """, unsafe_allow_html=True)

    # 查看对方答案（必须自己先回答）
    if both_answered:
        st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
        st.markdown("### 💕 你们的回答")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="answer-card">
                <p style="font-weight:700; color:#c0395a;">🚗 {USER_A_NAME}</p>
                <p style="line-height:1.8;">{answers.get(USER_A_NAME, {}).get('content', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="answer-card">
                <p style="font-weight:700; color:#c0395a;">👑 {USER_B_NAME}</p>
                <p style="line-height:1.8;">{answers.get(USER_B_NAME, {}).get('content', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        # AI 分析
        st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)

        existing_comment = today_qa.get("ai_comment", "")
        if existing_comment:
            st.markdown(f"""
            <div class="daily-question" style="margin-top:8px;">
                <p style="color:#c0395a; font-size:0.85rem; margin-bottom:8px;">💭 AI 心理分析</p>
                <p style="font-size:1rem; color:#6a3040 !important; text-align:left; line-height:1.9;">{existing_comment}</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🤖 生成 AI 心理分析", use_container_width=True, key="gen_ai"):
            if not client:
                st.error("请先填入 API Key！")
            else:
                a_ans = answers.get(USER_A_NAME, {}).get("content", "")
                b_ans = answers.get(USER_B_NAME, {}).get("content", "")
                ai_prompt = f"""这对情侣 {USER_A_NAME} 和 {USER_B_NAME} 在一起第 {days} 天，他们回答了一个问题。

问题：{question}

{USER_A_NAME} 的回答：{a_ans}

{USER_B_NAME} 的回答：{b_ans}

请从心理学角度深度分析他们的回答，包含以下内容：

1. 分别分析两人回答背后的心理状态和思考方式
2. 如果双方的回答存在明显差异或冲突，分析原因并给出具体、可操作的沟通建议
3. 如果双方的回答比较一致或互补，指出这体现了什么样的感情基础，并给予真诚的鼓励
4. 最后用一句温暖的话结尾

语气要像一位有洞察力的心理咨询师和好朋友结合的角色，真诚、有深度，不要空洞地夸奖，约300字。"""

                with st.spinner("💭 AI 正在深度分析你们的心理..."):
                    try:
                        comment = chat(client, ai_prompt, max_tokens=600)
                        today_qa["ai_comment"] = comment
                        qa_data[today_key] = today_qa
                        save_qa_data(qa_data)
                        st.rerun()
                    except Exception as e:
                        st.error(f"分析失败：{e}")

    elif my_answered and not partner_answered:
        st.info(f"💕 你已经回答了！等 {partner_name} 也回答之后，你们就可以互相看答案，并让 AI 分析啦～")

    # 历史记录
    history_items = [(k, v) for k, v in qa_data.items() if k != today_key and v.get("question")]
    if history_items:
        history_items.sort(key=lambda x: x[0], reverse=True)
        with st.expander(f"📚 历史问答记录（共 {len(history_items)} 条）"):
            for k, v in history_items[:10]:
                ans_a = v.get("answers", {}).get(USER_A_NAME, {}).get("content", "未回答")
                ans_b = v.get("answers", {}).get(USER_B_NAME, {}).get("content", "未回答")
                st.markdown(f"**{k}** · {v.get('question', '')}")
                st.caption(f"🚗 {USER_A_NAME}：{ans_a}")
                st.caption(f"👑 {USER_B_NAME}：{ans_b}")
                st.divider()

    # 重置
    if st.button("🔄 重置今日问答", help="清空今日回答重新开始"):
        qa_data.pop(today_key, None)
        save_qa_data(qa_data)
        st.session_state.daily_question = ""
        st.rerun()


# ════════════════════════════════════════════════════════════════════
# 底部
# ════════════════════════════════════════════════════════════════════

st.markdown("""
<p style="text-align:center; color:#c0395a; font-size:0.85rem; margin-top:40px;">
💕 每一个普通的日子，因为有你，都变成了值得记住的样子 💕
</p>
""", unsafe_allow_html=True)
