import streamlit as st
from openai import OpenAI
from datetime import datetime, date
import json
import os
import hashlib

# ─── 页面配置（只调用一次）────────────────────────────────────────────────────────
st.set_page_config(
    page_title="柴司机 & 耶公主 💕",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 全局样式 ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Lato:wght@300;400;700&family=Noto+Serif+SC:wght@400;700&display=swap');

/* 全局背景 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fff5f5 0%, #fff9f0 50%, #fdf6ff 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffe4e8 0%, #fff0e8 100%);
    border-right: 2px solid #f8c8d0;
}

/* 隐藏默认元素 */
#MainMenu, footer, header { visibility: hidden; }

/* 隐藏侧边栏收起按钮，防止用户意外收起 */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* 美化原生侧边栏收起/展开按钮 */
[data-testid="stSidebarCollapseButton"] button {
    background: linear-gradient(135deg, #e8607a, #c0395a) !important;
    border-radius: 0 16px 16px 0 !important;
    color: white !important;
    width: 28px !important;
    height: 60px !important;
    border: none !important;
    box-shadow: 3px 0 12px rgba(192,57,90,0.3) !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    width: 36px !important;
    box-shadow: 5px 0 20px rgba(192,57,90,0.5) !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: white !important;
}

/* 侧边栏收起时，固定展开按钮始终可见 */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: linear-gradient(135deg, #e8607a, #c0395a) !important;
    border-radius: 0 16px 16px 0 !important;
    box-shadow: 3px 0 12px rgba(192,57,90,0.3) !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    height: 60px !important;
    width: 32px !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="collapsedControl"] svg {
    fill: white !important;
}

/* 标题字体 */
h1 { font-family: 'Pacifico', cursive !important; color: #c0395a !important; }
h2, h3 { font-family: 'Noto Serif SC', serif !important; color: #8b3a52 !important; }

/* 正文 */
body, p, div, span, label {
    font-family: 'Lato', sans-serif !important;
    color: #4a2030 !important;
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
    cursor: pointer;
    margin-bottom: 12px;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(192,57,90,0.18);
    border-color: #e07090;
}
.feature-card h3 { font-size: 1.3rem; margin: 10px 0 6px 0; }
.feature-card p { font-size: 0.9rem; color: #9a6070 !important; margin: 0; }
.feature-emoji { font-size: 2.8rem; }

/* 爱心分隔线 */
.love-divider {
    text-align: center;
    color: #e0889a;
    font-size: 1.2rem;
    letter-spacing: 8px;
    margin: 20px 0;
}

/* 指标卡片 */
.metric-love {
    background: linear-gradient(135deg, #ffe0e8, #fff5e0);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid #f5c0cc;
}
.metric-love .number {
    font-family: 'Pacifico', cursive;
    font-size: 2.4rem;
    color: #c0395a;
}
.metric-love .label {
    font-size: 0.85rem;
    color: #9a6070;
    margin-top: 4px;
}

/* 输入框美化 */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] select {
    border: 1.5px solid #f3b8c4 !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.9) !important;
}

/* 按钮 */
.stButton > button {
    background: linear-gradient(135deg, #e8607a, #c0395a) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 10px 30px !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(192,57,90,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(192,57,90,0.4) !important;
}

/* 小说输出区域 */
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

/* 行程时间轴 */
.timeline-item {
    background: rgba(255,255,255,0.9);
    border-left: 4px solid #e8607a;
    border-radius: 0 16px 16px 0;
    padding: 16px 20px;
    margin: 12px 0;
    box-shadow: 0 2px 12px rgba(192,57,90,0.08);
}
.timeline-time {
    font-weight: 700;
    color: #c0395a !important;
    font-size: 0.9rem;
}

/* dressing code 特殊样式 */
.dressing-code {
    background: linear-gradient(135deg, #fff0f5, #fff8f0);
    border: 1.5px dashed #f3b8c4;
    border-radius: 14px;
    padding: 14px 18px;
    margin-top: 10px;
    font-size: 0.92rem;
}

/* 每日一问 */
.daily-question {
    background: linear-gradient(135deg, #ffe8ee, #fff5e8);
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    border: 2px solid #f3b8c4;
    box-shadow: 0 8px 32px rgba(192,57,90,0.12);
}
.daily-question .question-text {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.5rem;
    color: #8b3a52 !important;
    line-height: 1.8;
}

/* 答案对比 */
.answer-card {
    background: rgba(255,255,255,0.9);
    border-radius: 16px;
    padding: 20px;
    border: 1.5px solid #f3b8c4;
    text-align: center;
}

/* 吃什么卡片 */
.food-card {
    background: linear-gradient(135deg, #fff5f0, #fff0f5);
    border-radius: 20px;
    padding: 24px;
    border: 1.5px solid #f3b8c4;
    text-align: center;
    transition: all 0.3s;
    margin-bottom: 12px;
}
.food-card:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 24px rgba(192,57,90,0.15);
}

/* 侧边栏美化 */
[data-testid="stSidebar"] h1 {
    font-size: 1.4rem !important;
    text-align: center;
}
[data-testid="stSidebar"] .stRadio > div {
    flex-direction: column !important;
    gap: 8px !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(224,112,144,0.1) !important;
}

/* 标签页 */
.stTabs [data-baseweb="tab"] {
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
}

/* 成功/信息框 */
[data-testid="stSuccess"], [data-testid="stInfo"] {
    border-radius: 14px !important;
}

/* 首页功能卡片跳转按钮：透明覆盖，整张卡片可点击 */
div[data-testid="stButton"]:has(button[kind="secondaryFormSubmit"]) { display: none; }
.homepage-card-btn > div > button {
    margin-top: -180px !important;
    height: 180px !important;
    opacity: 0 !important;
    position: relative !important;
    z-index: 10 !important;
    border-radius: 20px !important;
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)


# ─── 工具函数 ────────────────────────────────────────────────────────────────────
def get_client():
    """返回 OpenAI 兼容的 DeepSeek 客户端"""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def chat(client, prompt: str, max_tokens: int = 1000) -> str:
    """非流式调用，返回文本字符串"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def chat_stream(client, prompt: str, max_tokens: int = 2500):
    """流式调用，返回文本块生成器"""
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

def days_together(anniversary: date) -> int:
    return (date.today() - anniversary).days

def load_qa_history():
    if os.path.exists("qa_history.json"):
        with open("qa_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_qa_history(history):
    with open("qa_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_daily_question_seed():
    today_str = date.today().isoformat()
    return int(hashlib.md5(today_str.encode()).hexdigest(), 16) % 10000


# ═══════════════════════════════════════════════════════════════════════════════
# 📌 侧边栏
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<h1 style='text-align:center; font-family:\"Noto Serif SC\", serif !important;'>💕 恋爱小站</h1>", unsafe_allow_html=True)

    # 关于我们
    st.markdown("#### 👫 关于我们")
    name1 = st.text_input("🚗 他的名字", value="柴司机", key="name1")
    name2 = st.text_input("👑 她的名字", value="耶公主", key="name2")

    anniversary = st.date_input(
        "💍 在一起的日子",
        value=date(2023, 9, 26),
        key="anniversary"
    )

    days = days_together(anniversary)
    st.markdown(f"""
    <div class="metric-love" style="margin: 16px 0;">
        <div class="number">+{days}</div>
        <div class="label">在一起的第 {days} 天 🌹</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # API 设置
    st.markdown("#### 🔑 API 设置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="请输入 DeepSeek API Key...",
        key="api_key"
    )
    if api_key:
        st.success("✅ API 已连接")
    else:
        st.warning("⚠️ 请输入 API Key 以使用 AI 功能")

    st.divider()

    # 导航菜单
    st.markdown("#### 🗺️ 导航")
    if "page" not in st.session_state:
        st.session_state.page = "🏠 首页"
    page = st.radio(
        "选择功能",
        ["🏠 首页", "🗺️ 约会计划", "📖 恋爱小说", "🍽️ 今天吃什么", "💬 每日一问"],
        key="page",
        label_visibility="collapsed"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 🏠 首页
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 首页":
    st.markdown(f"<h1 style='text-align:center; font-size:2.8rem;'>💕 {name1} & {name2}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#9a6070; font-size:1.1rem;'>今天是 {date.today().strftime('%Y年%m月%d日')} · 我们在一起第 <b style='color:#c0395a;'>{days}</b> 天</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">✦ ♥ ✦ ♥ ✦</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">🗺️</div>
            <h3>约会计划助手</h3>
            <p>输入你们的心情与偏好，AI 帮你规划完美约会行程，还附上专属 Dressing Code ✨</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✨ 开始规划约会", key="btn_date", use_container_width=True):
            st.session_state.page = "🗺️ 约会计划"
            st.rerun()

        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">🍽️</div>
            <h3>今天吃什么</h3>
            <p>解决情侣永恒难题！AI 根据心情、禁忌和场景，帮你们做出美食决定 🥢</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🥢 帮我决定吃什么", key="btn_food", use_container_width=True):
            st.session_state.page = "🍽️ 今天吃什么"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">📖</div>
            <h3>专属恋爱小说</h3>
            <p>把你们真实的故事交给 AI，生成只属于你们的浪漫小说 💌</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💌 生成我们的故事", key="btn_novel", use_container_width=True):
            st.session_state.page = "📖 恋爱小说"
            st.rerun()

        st.markdown("""
        <div class="feature-card">
            <div class="feature-emoji">💬</div>
            <h3>每日一问</h3>
            <p>每天一个深度问题，让你们更了解彼此，AI 还会分析你们的答案 🌙</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌙 查看今日问题", key="btn_qa", use_container_width=True):
            st.session_state.page = "💬 每日一问"
            st.rerun()

    st.markdown('<div class="love-divider">✦ ♥ ✦ ♥ ✦</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#b07080; font-size:0.95rem;'>从左侧边栏选择功能开始使用 · 记得先输入 DeepSeek API Key 💕</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 🗺️ 约会计划助手
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ 约会计划":
    st.markdown("<h1>🗺️ 约会计划助手</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>告诉 AI 你们的状态，生成专属约会行程 + Dressing Code 💝</p>", unsafe_allow_html=True)
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
            budget = st.selectbox("💰 预算范围", ["低（人均 100 以内）", "中（人均 100-300）", "高（人均 300+）"])
            weather = st.selectbox("🌤️ 当前天气", ["晴天", "多云", "小雨", "寒冷", "炎热"])

        with col2:
            prefs = st.multiselect(
                "🎯 偏好标签",
                ["户外探索", "美食打卡", "文艺展览", "运动健身", "居家休闲", "购物逛街", "电影演出"],
                default=["美食打卡", "文艺展览"]
            )
            mood1 = st.text_area(f"🚗 {name1} 今天的心情", placeholder="例如：有点累，想安静放松一下...", height=100)
            mood2 = st.text_area(f"👑 {name2} 今天的心情", placeholder="例如：很开心，想出去逛逛！", height=100)

        submitted = st.form_submit_button("✨ 生成约会计划", use_container_width=True)

    if submitted:
        client = get_client()
        if not client:
            st.error("请先在左侧边栏输入 DeepSeek API Key！")
        elif not city:
            st.error("请输入城市！")
        else:
            prefs_str = "、".join(prefs) if prefs else "不限"
            prompt = f"""你是一位专业的约会规划师，请为一对情侣规划一个完美的约会行程。

情侣信息：
- 男方名字：{name1}，今日心情：{mood1 or "没有特别说明"}
- 女方名字：{name2}，今日心情：{mood2 or "没有特别说明"}
- 在一起第 {days} 天

约会条件：
- 城市/地区：{city}
- 可用时间：{time_avail}
- 时间段：{"、".join(time_period) if time_period else "不限"}
- 预算：{budget}
- 偏好：{prefs_str}
- 天气：{weather}

请生成一份温馨详细的约会计划，格式如下：

## 💕 今日约会主题
（给这次约会起一个浪漫的主题名）

## 📅 行程安排
（按时间段列出，每个环节包含：时间、活动、地点建议、贴心小提示）

## 👗 Dressing Code
分别给出 {name1} 和 {name2} 的穿搭建议，包括：
- 整体风格
- 单品推荐
- 颜色搭配建议
- 一句贴心提醒

## 💌 写在最后
（一句温暖的结语，提到两人的名字）

请用温暖、浪漫的语气撰写，中文回答。"""

            with st.spinner("💕 AI 正在为你们规划专属约会..."):
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


# ═══════════════════════════════════════════════════════════════════════════════
# 📖 专属恋爱小说
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📖 恋爱小说":
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
                f"👑 {name2} 的感受",
                placeholder="例如：第一眼看到他就觉得他很特别，有点紧张又很期待...",
                height=100
            )
        with col2:
            feeling1 = st.text_area(
                f"🚗 {name1} 的感受",
                placeholder="例如：没想到她会主动来找我说话，心跳漏了一拍...",
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
            st.error("请先在左侧边栏输入 DeepSeek API Key！")
        elif not experience:
            st.error("请描述你们的真实经历！")
        else:
            freedom_map = {
                "低 - 严格还原": "请严格基于以下内容进行文学润色，不要添加任何未提及的情节或细节，保持高度忠实于原始经历。",
                "中 - 适当润色": "可以合理补充对话和细节描写，但核心事件和情感走向保持不变，适度增加文学性。",
                "高 - 大胆创作": "以此为灵感自由创作，可以加入戏剧性转折、环境描写、内心独白，大胆发挥想象力，让故事更加精彩动人。"
            }
            length_map = {
                "短篇（约500字）": "约500字",
                "中篇（约1000字）": "约1000字",
                "长篇（约2000字）": "约2000字"
            }

            prompt = f"""你是一位才华横溢的言情小说作家，请根据以下真实经历为这对情侣创作一篇专属小说。

人物：
- 男主：{name1}
- 女主：{name2}
- 在一起第 {days} 天

真实经历：
{experience}

{name2} 的感受：
{feeling2 or "未填写"}

{name1} 的感受：
{feeling1 or "未填写"}

额外补充：
{extra or "无"}

创作要求：
- 风格：{style}
- 篇幅：{length_map[length]}
- 自由度要求：{freedom_map[freedom]}
- 主角名字请使用 {name1} 和 {name2}
- 融合双方的感受，呈现立体的双视角情感描写
- 语言优美，情感细腻，让他们读完会心跳加速

请直接开始写小说正文，不需要任何说明文字。"""

            st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
            st.markdown(f"**📖 {style} · {length} · 自由度：{freedom}**")

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


# ═══════════════════════════════════════════════════════════════════════════════
# 🍽️ 今天吃什么
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🍽️ 今天吃什么":
    st.markdown("<h1>🍽️ 今天吃什么</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>解决情侣最难的问题，AI 帮你们做决定！🥢</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    with st.form("food_form"):
        col1, col2 = st.columns(2)
        with col1:
            food_city = st.text_input("📍 所在城市", placeholder="例如：上海")
            scene = st.selectbox("🏠 用餐场景", ["出去吃（餐厅）", "点外卖", "在家自己做"])
            food_budget = st.selectbox("💰 今日预算", ["节省（人均 50 以内）", "普通（人均 50-150）", "犒劳自己（人均 150+）"])
            mood_food = st.selectbox("😊 今天的心情", ["开心愉快", "有点疲惫", "想犒劳自己", "平淡普通", "需要安慰"])
        with col2:
            avoid1 = st.text_input(f"🚫 {name1} 不吃的", placeholder="例如：香菜、海鲜")
            avoid2 = st.text_input(f"🚫 {name2} 不吃的", placeholder="例如：辣的、羊肉")
            craving = st.text_area("💭 有什么想吃的方向？", placeholder="例如：想吃点热乎的、想吃甜的...", height=80)

        submitted = st.form_submit_button("🎲 帮我决定！", use_container_width=True)

    if submitted:
        client = get_client()
        if not client:
            st.error("请先在左侧边栏输入 DeepSeek API Key！")
        else:
            prompt = f"""你是一个美食决策专家，请帮这对情侣解决"今天吃什么"的难题。

情侣信息：
- {name1} 不吃：{avoid1 or "无禁忌"}
- {name2} 不吃：{avoid2 or "无禁忌"}
- 城市：{food_city or "不限"}
- 用餐场景：{scene}
- 预算：{food_budget}
- 今日心情：{mood_food}
- 想吃的方向：{craving or "没有特别想法"}

请给出 3 个推荐方案，每个方案包括：
1. 🍜 推荐菜系/餐厅类型（起一个有趣的名字）
2. 推荐理由（结合今日心情和两人情况，说得有温度）
3. 具体推荐菜品 2-3 个
4. 如果是"在家自己做"，附上一个简单食谱思路

格式清晰，语气活泼温暖，用 emoji 点缀，中文回答。"""

            with st.spinner("🍳 AI 正在思考今天吃什么..."):
                try:
                    result = chat(client, prompt, max_tokens=1200)
                    st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="food-card">{result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"调用失败：{e}")

            if st.button("🔄 再换一批"):
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 💬 每日一问
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💬 每日一问":
    st.markdown("<h1>💬 每日一问</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9a6070;'>每天一个深度问题，让你们更了解彼此 🌙</p>", unsafe_allow_html=True)
    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    # 初始化 session state
    if "daily_question" not in st.session_state:
        st.session_state.daily_question = ""
    if "answer1" not in st.session_state:
        st.session_state.answer1 = ""
    if "answer2" not in st.session_state:
        st.session_state.answer2 = ""
    if "show_answers" not in st.session_state:
        st.session_state.show_answers = False
    if "ai_comment" not in st.session_state:
        st.session_state.ai_comment = ""

    client = get_client()

    # 生成每日问题
    if not st.session_state.daily_question:
        if client:
            seed = get_daily_question_seed()
            category = ["了解彼此内心", "关于未来规划", "童年与成长", "价值观与人生观", "趣味脑洞"][seed % 5]
            prompt = f"""请生成一个适合情侣之间的深度问题，类别是"{category}"。

要求：
- 问题要有深度，能引发真实的思考和分享
- 不能太隐私或令人不适
- 语气温柔，富有情感
- 只输出问题本身，不要任何解释或序号
- 今天的随机种子是 {seed}，请基于此生成不同的问题"""

            with st.spinner("💭 正在生成今日问题..."):
                try:
                    st.session_state.daily_question = chat(client, prompt, max_tokens=100).strip()
                except Exception as e:
                    st.session_state.daily_question = "如果可以和我重新认识一次，你希望我们在什么样的场景下相遇？"
        else:
            st.session_state.daily_question = "如果可以和我重新认识一次，你希望我们在什么样的场景下相遇？"

    # 显示今日问题
    today_str = date.today().strftime("%Y年%m月%d日")
    st.markdown(f"""
    <div class="daily-question">
        <p style="color:#c0395a; font-size:0.85rem; margin-bottom:12px;">📅 {today_str} · 今日一问</p>
        <p class="question-text">"{st.session_state.daily_question}"</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="love-divider">♥ ♥ ♥</div>', unsafe_allow_html=True)

    # 回答区域
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### 🚗 {name1} 的回答")
        answer1_input = st.text_area("", placeholder="写下你的想法...", height=140, key="input_a1", label_visibility="collapsed")
        if st.button(f"✅ {name1} 提交回答", key="submit1"):
            st.session_state.answer1 = answer1_input

    with col2:
        st.markdown(f"#### 👑 {name2} 的回答")
        answer2_input = st.text_area("", placeholder="写下你的想法...", height=140, key="input_a2", label_visibility="collapsed")
        if st.button(f"✅ {name2} 提交回答", key="submit2"):
            st.session_state.answer2 = answer2_input

    # 显示已提交状态
    if st.session_state.answer1:
        st.success(f"💌 {name1} 已回答")
    if st.session_state.answer2:
        st.success(f"💌 {name2} 已回答")

    # 两人都回答后，显示对比和 AI 分析
    if st.session_state.answer1 and st.session_state.answer2:
        st.markdown('<div class="love-divider">✦ ♥ ✦</div>', unsafe_allow_html=True)
        st.markdown("### 💕 你们的回答")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"""
            <div class="answer-card">
                <p style="font-weight:700; color:#c0395a;">🚗 {name1}</p>
                <p>{st.session_state.answer1}</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="answer-card">
                <p style="font-weight:700; color:#c0395a;">👑 {name2}</p>
                <p>{st.session_state.answer2}</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🤖 查看 AI 分析", use_container_width=True) or st.session_state.ai_comment:
            if not st.session_state.ai_comment and client:
                prompt = f"""这对情侣 {name1} 和 {name2} 在一起第 {days} 天，他们回答了一个问题。

问题：{st.session_state.daily_question}

{name1} 的回答：{st.session_state.answer1}

{name2} 的回答：{st.session_state.answer2}

请用温暖、有洞察力的语气分析他们的回答：
1. 找出两人答案中有趣的共同点或有意思的差异
2. 给出一个温暖的观察或小建议
3. 用一句浪漫的话结尾

语气要像一个智慧又浪漫的朋友，不要太正式，200字以内。"""
                with st.spinner("💭 AI 正在分析你们的回答..."):
                    try:
                        st.session_state.ai_comment = chat(client, prompt, max_tokens=400)
                    except Exception as e:
                        st.error(f"分析失败：{e}")

            if st.session_state.ai_comment:
                st.markdown(f"""
                <div class="daily-question" style="margin-top:16px;">
                    <p style="color:#c0395a; font-size:0.85rem; margin-bottom:8px;">🤖 AI 的观察</p>
                    <p style="font-size:1rem; color:#6a3040 !important; text-align:left; line-height:1.9;">{st.session_state.ai_comment}</p>
                </div>
                """, unsafe_allow_html=True)

        # 保存历史
        history = load_qa_history()
        today_record = {
            "date": date.today().isoformat(),
            "question": st.session_state.daily_question,
            "answer1": st.session_state.answer1,
            "answer2": st.session_state.answer2,
        }
        if not any(r["date"] == today_record["date"] for r in history):
            history.append(today_record)
            save_qa_history(history)

    # 历史记录
    history = load_qa_history()
    if history:
        with st.expander(f"📚 历史问答记录（共 {len(history)} 条）"):
            for record in reversed(history[-10:]):
                st.markdown(f"**{record['date']}** · {record['question']}")
                st.caption(f"🚗 {name1}：{record['answer1']}")
                st.caption(f"👑 {name2}：{record['answer2']}")
                st.divider()

    # 重置今日
    if st.button("🔄 重置今日问答", help="清空今日回答重新开始"):
        st.session_state.answer1 = ""
        st.session_state.answer2 = ""
        st.session_state.ai_comment = ""
        st.session_state.daily_question = ""
        st.rerun()
