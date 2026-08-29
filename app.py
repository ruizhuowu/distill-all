"""
一切皆蒸馏 - 主应用（湖经考霸版）
面向大学生的知识蒸馏备考平台 + 社区功能
"""

import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
import sys

# 确保能导入同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (
    extract_text, distill, distill_with_llm, distill_custom, METHODS,
    split_into_sections, extract_key_sentences
)
from knowledge_base import get_courses, render_course, render_chapter
import mock_data

# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="一切皆蒸馏",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化 session state（修复首次加载 ValueError）
if "page" not in st.session_state:
    st.session_state.page = "首页"

# ============================================================
# 全局样式（渐变科技风）
# ============================================================

st.markdown("""
<style>
    /* ========== 全局基础 ========== */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    .main .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* ========== 渐变文字 ========== */
    .gradient-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }

    /* ========== 按钮渐变 ========== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
    }
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #f0f0ff !important;
    }

    /* ========== 卡片通用 ========== */
    .card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #eef0f6;
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.12);
        border-color: #667eea;
    }

    /* ========== 蒸馏方式卡片 ========== */
    .method-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid #eef0f6;
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .method-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
        transform: translateY(-4px);
    }
    .method-card .icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .method-card .name { font-weight: 700; font-size: 1.05rem; color: #1a1a2e; margin-bottom: 0.3rem; }
    .method-card .desc { font-size: 0.85rem; color: #888; }

    /* ========== 步骤引导 ========== */
    .step-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #eef0f6;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px; height: 36px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 50%;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
    }

    /* ========== 侧边栏 ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 4px;
    }
    section[data-testid="stSidebar"] .stRadio > div > div {
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label span,
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] label div {
        color: #e8ecf4 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 0.8rem !important;
        border-radius: 8px !important;
        transition: all 0.2s !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] label:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] input:checked + label,
    section[data-testid="stSidebar"] label:has(input:checked) {
        background: rgba(102, 126, 234, 0.25) !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* ========== 标签 ========== */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .tag-primary {
        background: linear-gradient(135deg, #667eea22, #764ba222);
        color: #667eea;
    }

    /* ========== 结果卡片 ========== */
    .result-card {
        background: white;
        border-radius: 14px;
        padding: 2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        border: 1px solid #eef0f6;
    }

    /* ========== 输入框 ========== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 1.5px solid #e0e4f0 !important;
        transition: border-color 0.2s !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* ========== 通用 ========== */
    .stAlert { margin-top: 0.5rem; border-radius: 10px !important; }
    div[data-testid="stSidebar"] { min-width: 240px; }
    hr { border-color: #eef0f6 !important; }

    /* ========== 资料卡片 ========== */
    .resource-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #eef0f6;
        transition: all 0.2s ease;
    }
    .resource-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
    }

    /* ========== 帖子卡片 ========== */
    .post-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }

    /* ========== 排行榜 ========== */
    .rank-item {
        display: flex;
        align-items: center;
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        margin-bottom: 0.4rem;
        background: white;
        border: 1px solid #eef0f6;
    }
    .rank-item:hover {
        background: #f8f9ff;
    }
    .rank-num {
        width: 28px; height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.8rem;
    }
    .rank-1 .rank-num { background: linear-gradient(135deg, #FFD700, #FFA500); color: white; }
    .rank-2 .rank-num { background: linear-gradient(135deg, #C0C0C0, #A0A0A0); color: white; }
    .rank-3 .rank-num { background: linear-gradient(135deg, #CD7F32, #B8860B); color: white; }
    .rank-other .rank-num { background: #eef0f6; color: #888; }

    /* ========== 头像 ========== */
    .avatar {
        width: 36px; height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        color: white;
        margin-right: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Session State 初始化
# ============================================================

defaults = {
    "page": "首页",
    "distill_result": None,
    "distill_method": None,
    "distill_title": None,
    "edited_result": None,
    "api_key": "",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen-plus",
    "model_type": "text",  # math / text
    "custom_model_name": "",
    "chosen_method": "outline",  # 默认提纲式
    "llm_error": None,
    "api_preset": "阿里云 DashScope（通义千问）",
    "api_model_name": "qwen-plus",
    "smtp_host": "smtp.qq.com",
    "smtp_port": 465,
    "smtp_email": "2687033737@qq.com",
    "smtp_auth_code": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# 侧边栏导航
# ============================================================

with st.sidebar:
    # Logo 区域
    st.markdown(
        "<div style='text-align:center; padding: 1.5rem 0 1rem;'>"
        "<div style='font-size:2.2rem; margin-bottom:0.3rem;'>🧪</div>"
        "<div style='color:#ffffff; font-size:1.5rem; margin-bottom:0.3rem; font-weight:800;'>一切皆蒸馏</div>"
        "<div style='color:#c8d0e8; font-size:0.85rem;'>把任何学习材料变成你的备考系统</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # 导航（新增资料库和社区）
    page_labels = ["🏠 首页", "🧪 开始蒸馏", "📚 知识骨架", "📁 资料库", "💬 社区", "⚙️ 模型设置", "💬 反馈"]
    page_keys = ["首页", "开始蒸馏", "知识骨架", "资料库", "社区", "模型设置", "反馈"]
    default_idx = page_keys.index(st.session_state.page) if st.session_state.page in page_keys else 0

    page = st.radio(
        "导航",
        page_labels,
        index=default_idx,
        label_visibility="collapsed",
    )

    page_map = {
        "🏠 首页": "首页",
        "🧪 开始蒸馏": "开始蒸馏",
        "📚 知识骨架": "知识骨架",
        "📁 资料库": "资料库",
        "💬 社区": "社区",
        "⚙️ 模型设置": "模型设置",
        "💬 反馈": "反馈",
    }
    current_page = page_map.get(page, "首页")
    st.session_state.page = current_page

    st.markdown("---")

    # 全站统计
    stats = mock_data.SITE_STATS
    st.markdown(
        f"<div style='text-align:center; padding:0.5rem 0; color:#c8d0e8; font-size:0.78rem;'>"
        f"📊 {stats['total_students']} 位同学 · {stats['total_materials']} 份资料 · {stats['total_posts']} 条讨论"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#8892b0; font-size:0.75rem; padding: 0.5rem 0;'>"
        "v1.0 · 一切皆蒸馏</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# 首页（Landing Page 风格）- 增强版
# ============================================================

if current_page == "首页":

    # Hero 区
    st.markdown(
        "<div style='text-align:center; padding: 3rem 0 1.5rem;'>"
        "<div style='font-size:3.5rem; margin-bottom:0.5rem;'>🧪</div>"
        "<h1 class='gradient-title' style='font-size:2.8rem; margin-bottom:0.5rem;'>"
        "一切皆蒸馏</h1>"
        "<p style='color:#8892b0; font-size:1.2rem; max-width:600px; margin:0 auto 1.5rem;'>"
        "把任何学习材料变成你自己的备考系统</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # CTA 按钮
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("🚀 立即开始蒸馏", use_container_width=True, type="primary"):
            st.session_state.page = "开始蒸馏"
            st.rerun()
    st.markdown(
        "<div style='text-align:center; margin-bottom:2rem;'>"
        "<span style='color:#8892b0; font-size:0.9rem;'>"
        "支持 PDF / TXT / MD 格式上传，也可以从预建知识骨架中选择</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 三步引导
    st.markdown(
        "<div style='text-align:center; margin-bottom:1.5rem;'>"
        "<h2 style='font-weight:700; color:#1a1a2e;'>三步完成知识蒸馏</h2>"
        "</div>",
        unsafe_allow_html=True,
    )

    step1, step2, step3 = st.columns(3)
    with step1:
        st.markdown(
            "<div class='step-card'>"
            "<div class='step-num'>1</div>"
            "<div style='font-size:2rem; margin-bottom:0.5rem;'>📤</div>"
            "<div style='font-weight:700; font-size:1.05rem; margin-bottom:0.3rem;'>上传材料</div>"
            "<div style='color:#888; font-size:0.85rem;'>PDF课件、笔记、习题集——任何学习材料都能导入</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with step2:
        st.markdown(
            "<div class='step-card'>"
            "<div class='step-num'>2</div>"
            "<div style='font-size:2rem; margin-bottom:0.5rem;'>🧪</div>"
            "<div style='font-weight:700; font-size:1.05rem; margin-bottom:0.3rem;'>选择蒸馏方式</div>"
            "<div style='color:#888; font-size:0.85rem;'>6种标准化蒸馏方式，从提纲到费曼到Cornell笔记</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with step3:
        st.markdown(
            "<div class='step-card'>"
            "<div class='step-num'>3</div>"
            "<div style='font-size:2rem; margin-bottom:0.5rem;'>📝</div>"
            "<div style='font-weight:700; font-size:1.05rem; margin-bottom:0.3rem;'>获得备考系统</div>"
            "<div style='color:#888; font-size:0.85rem;'>结构化笔记 + 自测题 + 可编辑，变成你的复习体系</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 六种蒸馏方式卡片
    st.markdown(
        "<div style='text-align:center; margin-bottom:1.5rem;'>"
        "<h2 style='font-weight:700; color:#1a1a2e;'>六种蒸馏方式</h2>"
        "<p style='color:#8892b0; font-size:0.95rem;'>每一种都是经过设计的知识内化方法</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    method_items = list(METHODS.items())
    row1 = st.columns(3)
    row2 = st.columns(3)
    for i, (key, info) in enumerate(method_items):
        col = row1[i % 3] if i < 3 else row2[i % 3]
        with col:
            st.markdown(
                f"<div class='method-card'>"
                f"<div class='icon'>{info['icon']}</div>"
                f"<div class='name'>{info['name']}</div>"
                f"<div class='desc'>{info['desc']}</div>"
                f"<div style='display:inline-block; margin-top:0.5rem; padding:0.15rem 0.7rem; "
                f"border-radius:20px; background:#667eea15; color:#667eea; "
                f"font-size:0.75rem; font-weight:600;'>🎯 {info['phase']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 热门课程展示
    st.markdown(
        "<div style='text-align:center; margin-bottom:1.5rem;'>"
        "<h2 style='font-weight:700; color:#1a1a2e;'>热门课程</h2>"
        "</div>",
        unsafe_allow_html=True,
    )

    course_cols = st.columns(3)
    for i, c in enumerate(mock_data.COURSES[:6]):
        with course_cols[i % 3]:
            tags_html = " ".join([f"<span class='tag tag-primary' style='font-size:0.72rem;padding:0.15rem 0.5rem;'>{t}</span>" for t in c["tags"][:2]])
            st.markdown(
                f"<div class='card' style='cursor:pointer;' onclick=\"void(0)\">"
                f"<div style='display:flex;align-items:center;margin-bottom:0.5rem;'>"
                f"<div style='background:linear-gradient(135deg,#667eea,#764ba2);width:40px;height:40px;"
                f"border-radius:10px;display:flex;align-items:center;justify-content:center;"
                f"color:white;font-weight:700;font-size:0.85rem;margin-right:0.8rem;'>{c['code'][:2]}</div>"
                f"<div><div style='font-weight:700;font-size:0.95rem;color:#1a1a2e;'>{c['name']}</div>"
                f"<div style='color:#888;font-size:0.8rem;'>{c['category']} · {c['department']}</div></div></div>"
                f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;'>{tags_html}</div>"
                f"<div style='margin-top:0.6rem;display:flex;justify-content:space-between;color:#888;font-size:0.8rem;'>"
                f"<span>📄 {c['stats']['total_materials']}份资料</span>"
                f"<span>⭐ {c['stats']['avg_rating']}</span>"
                f"<span>👥 {c['stats']['active_students']}人学习</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 底部快捷入口
    quick_cols = st.columns(4)
    with quick_cols[0]:
        if st.button("📁 浏览资料库", use_container_width=True):
            st.session_state.page = "资料库"
            st.rerun()
    with quick_cols[1]:
        if st.button("💬 进入社区", use_container_width=True):
            st.session_state.page = "社区"
            st.rerun()
    with quick_cols[2]:
        if st.button("📚 浏览知识骨架", use_container_width=True):
            st.session_state.page = "知识骨架"
            st.rerun()
    with quick_cols[3]:
        if st.button("⚙️ 配置模型", use_container_width=True):
            st.session_state.page = "模型设置"
            st.rerun()


# ============================================================
# 开始蒸馏
# ============================================================

elif current_page == "开始蒸馏":

    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h1 style='font-weight:700; color:#1a1a2e; margin-bottom:0.3rem;'>"
        "🧪 开始蒸馏</h1>"
        "<p style='color:#8892b0;'>上传材料→ 选择方式→ 获取你的备考笔记</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # 检查是否有已蒸馏的结果
    if st.session_state.distill_result is not None:
        result = st.session_state.edited_result or st.session_state.distill_result

        # 成功横幅 + 元信息卡片
        st.markdown(
            "<div style='background: linear-gradient(135deg, #667eea11, #764ba211); "
            "border-radius:14px; padding:1.5rem 2rem; margin-bottom:1.5rem; "
            "border:1px solid #667eea33;'>"
            "<div style='font-size:1.3rem; font-weight:700; color:#1a1a2e; margin-bottom:0.5rem;'>"
            "✅ 蒸馏完成！</div>"
            f"<span class='tag tag-primary'>{st.session_state.distill_method}</span>"
            f"&nbsp;&nbsp;<span class='tag' style='background:#f0f0f0; color:#555;'>"
            f"{st.session_state.distill_title}</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        # 如果LLM调用失败，显示警告
        if st.session_state.get("llm_error"):
            st.warning(f"⚠️ {st.session_state.llm_error}")
            st.info("👇 以下为模板模式生成的结果，配置有效 API Key 后可获得更高质量的 LLM 蒸馏。")

        # 结果卡片
        st.markdown(
            "<div class='result-card'>"
            "<div style='font-weight:600; color:#667eea; font-size:0.9rem; margin-bottom:1rem;'>"
            "📄 蒸馏结果预览</div>",
            unsafe_allow_html=True,
        )
        st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)

        # 编辑模式
        with st.expander("📝 编辑蒸馏结果", expanded=False):
            edited = st.text_area(
                "直接编辑Markdown内容",
                value=st.session_state.edited_result or st.session_state.distill_result,
                height=300,
                key="edit_area"
            )
            ec1, ec2 = st.columns(2)
            with ec1:
                if st.button("保存修改", key="save_edit"):
                    st.session_state.edited_result = edited
                    st.rerun()
            with ec2:
                if st.button("放弃修改", key="discard_edit"):
                    st.session_state.edited_result = None
                    st.rerun()

        # 导出按钮
        st.markdown("")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.download_button(
                "📥 下载 Markdown",
                data=result,
                file_name=f"{st.session_state.distill_title}_蒸馏结果.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_e2:
            if st.button("🔄 蒸馏新材料", use_container_width=True):
                st.session_state.distill_result = None
                st.session_state.edited_result = None
                st.session_state.uploaded_file_bytes = None
                st.session_state.uploaded_file_name = None
                st.session_state.source_type = None
                st.rerun()

    else:
        # 蒸馏输入界面
        st.markdown("### 第一步：选择内容来源")

        source_tab1, source_tab2 = st.tabs([" 上传文件", "📚 从知识骨架选择"])

        with source_tab1:
            uploaded_file = st.file_uploader(
                "上传学习材料（支持 PDF、TXT、MD）",
                type=["pdf", "txt", "md"],
                help="上传你的课件、笔记、习题集等学习材料"
            )
            if uploaded_file:
                file_bytes = uploaded_file.read()
                st.session_state["uploaded_file_bytes"] = file_bytes
                st.session_state["uploaded_file_name"] = uploaded_file.name
                st.session_state["source_type"] = "upload"
                st.success(f"已上传：{uploaded_file.name}（{uploaded_file.size/1024:.1f} KB）")

        with source_tab2:
            courses = get_courses()
            course_names = [f"{c['icon']} {c['name']}" for c in courses]
            selected_course = st.selectbox("选择课程", course_names)
            selected_idx = course_names.index(selected_course)
            course = courses[selected_idx]

            chapter_names = [ch["title"] for ch in course["chapters"]]
            selected_chapters = st.multiselect(
                "选择章节（可多选）",
                chapter_names,
                default=chapter_names[:2],
            )

            if selected_chapters:
                combined = []
                for ch in course["chapters"]:
                    if ch["title"] in selected_chapters:
                        combined.append(render_chapter(ch))
                skeleton_text = "\n---\n".join(combined)
                st.session_state["skeleton_text"] = skeleton_text
                st.session_state["skeleton_source_type"] = "skeleton"
                st.session_state["skeleton_title"] = f"{course['name']} - {' + '.join(selected_chapters)}"
                st.info(f"已选择 {len(selected_chapters)} 个章节的知识骨架内容")

        st.markdown("---")
        st.markdown("### 第二步：选择蒸馏方式（或直接提要求）")

        # 核心逻辑提示条
        st.markdown(
            "<div style='background:#f6f7ff; border:1px solid #667eea33; border-radius:10px; "
            "padding:0.7rem 1rem; margin-bottom:1rem; color:#4a4a7a; font-size:0.9rem;'>"
            "💡 <b>核心逻辑</b>：无论选哪种方式，材料都会先被拆成"
            "<b>知识骨架</b>（概念/公式/方法/易错点 + 考点强度 ★★★），"
            "你选的只是这份骨架的<b>呈现方式</b>。先想清楚：你现在想干嘛？"
            "</div>",
            unsafe_allow_html=True,
        )

        # 用卡片式布局展示蒸馏方式
        method_keys_list = list(METHODS.keys())
        method_cols = st.columns(3)
        for i, key in enumerate(method_keys_list):
            info = METHODS[key]
            with method_cols[i % 3]:
                is_chosen = (st.session_state.get("chosen_method") == key)
                border_color = "#667eea" if is_chosen else "#e0e0e0"
                bg_color = "#f0f0ff" if is_chosen else "white"
                st.markdown(
                    f"""<div style="padding:1rem; border:2px solid {border_color}; border-radius:8px;
                        background:{bg_color}; text-align:center; cursor:pointer; min-height:110px;">
                        <div style="font-size:1.5rem;">{info['icon']}</div>
                        <div style="font-weight:bold; margin:0.3rem 0;">{info['name']}</div>
                        <div style="font-size:0.85rem; color:#666;">{info['desc']}</div>
                        <div style="display:inline-block; margin-top:0.4rem; padding:0.1rem 0.6rem;
                            border-radius:20px; background:#667eea15; color:#667eea;
                            font-size:0.72rem; font-weight:600;">🎯 {info['phase']}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )
                if st.button(f"选择 {info['name']}", key=f"select_{key}", use_container_width=True,
                             type="primary" if is_chosen else "secondary"):
                    st.session_state["chosen_method"] = key
                    st.rerun()

        # 自定义要求入口
        is_custom = st.session_state.get("chosen_method") == "custom"
        _custom_card_style = (
            "border:2px solid #667eea;" if is_custom
            else "border:1.5px dashed #667eea44;"
        )
        _custom_bg = "#eef1ff;" if is_custom else "#fafbff;"
        st.markdown(
            f"<div style='margin-top:0.8rem; padding:1rem; border-radius:12px; "
            f"background:{_custom_bg}; {_custom_card_style}'>"
            f"<div style='font-weight:700; color:#1a1a2e; font-size:1.05rem;'>✍️ 自定义要求</div>"
            f"<div style='color:#8892b0; font-size:0.85rem; margin-bottom:0.6rem;'>"
            f"用自然语言告诉 AI 你的复习目标</div>",
            unsafe_allow_html=True,
        )
        custom_requirement = st.text_area(
            "你的复习要求",
            value=st.session_state.get("custom_requirement", ""),
            placeholder="例如：只看第一章和第三章，去掉公式，重点讲物质观相关的概念；只要概念和易错点；把每一条都给出考法...",
            height=90,
            key="custom_req_input",
        )
        col_confirm, col_tip = st.columns([1, 3])
        with col_confirm:
            if st.button("✅ 使用此要求", use_container_width=True, type="primary",
                         key="btn_custom_confirm"):
                st.session_state["chosen_method"] = "custom"
                st.session_state["custom_requirement"] = custom_requirement.strip()
                st.rerun()
        with col_tip:
            if not st.session_state.get("api_key"):
                st.caption("💡 未配 API Key 时仅支持简单指令；配置后可完整理解自然语言")
        st.markdown("</div>", unsafe_allow_html=True)

        chosen_method = st.session_state.get("chosen_method", method_keys_list[0])

        st.markdown("---")
        st.markdown("### 第三步：开始蒸馏")

        title_input = st.text_input(
            "给这份蒸馏结果起个名字",
            value="我的蒸馏笔记",
            placeholder="例如：高数第三章复习、大物力学期末速通..."
        )

        if st.button("🧪 开始蒸馏！", use_container_width=True, type="primary"):
            source_text = ""
            source_title = title_input

            if st.session_state.get("source_type") == "upload":
                file_bytes = st.session_state.get("uploaded_file_bytes")
                file_name = st.session_state.get("uploaded_file_name", "")
                if file_bytes:
                    source_text = extract_text(file_bytes, file_name)
                    source_title = title_input or file_name.rsplit(".", 1)[0]
                else:
                    st.error("请先上传文件")
                    st.stop()
            elif st.session_state.get("source_type") == "skeleton":
                source_text = st.session_state.get("skeleton_text", "")
                source_title = title_input or st.session_state.get("skeleton_title", "知识骨架")
            else:
                st.error("请先选择内容来源（上传文件或从知识骨架选择）")
                st.stop()

            if not source_text.strip():
                st.error("内容为空，请检查上传的文件或选择的章节")
                st.stop()

            # 执行蒸馏
            with st.spinner("蒸馏中..."):
                api_key = st.session_state.get("api_key", "")
                llm_error = None
                method_display = METHODS.get(chosen_method, {}).get("name", "自定义要求")
                base_url = st.session_state.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
                model = st.session_state.get("model_name", "qwen-plus")

                if chosen_method == "custom":
                    custom_req = st.session_state.get("custom_requirement", "").strip()
                    if not custom_req:
                        st.error("请先描述你的自定义要求，再开始蒸馏")
                        st.stop()
                    method_display = "✍️ 自定义要求"
                    if api_key:
                        try:
                            result = distill_with_llm(source_text, "outline", source_title,
                                                      api_key, base_url, model, requirement=custom_req)
                        except RuntimeError as e:
                            llm_error = str(e)
                            st.warning(f"⚠️ {llm_error}，已自动切换为模板模式")
                            result = distill_custom(source_text, custom_req, source_title)
                    else:
                        result = distill_custom(source_text, custom_req, source_title)
                elif api_key:
                    try:
                        result = distill_with_llm(source_text, chosen_method, source_title,
                                                  api_key, base_url, model)
                    except RuntimeError as e:
                        llm_error = str(e)
                        st.warning(f"⚠️ {llm_error}，已自动切换为模板模式")
                        result = distill(source_text, chosen_method, source_title)
                else:
                    result = distill(source_text, chosen_method, source_title)

            st.session_state.distill_result = result
            st.session_state.distill_method = method_display
            st.session_state.distill_title = source_title
            st.session_state.edited_result = None
            st.session_state.llm_error = llm_error
            st.rerun()


# ============================================================
# 知识骨架浏览
# ============================================================

elif current_page == "知识骨架":
    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h1 style='font-weight:700; color:#1a1a2e; margin-bottom:0.3rem;'>"
        "📚 知识骨架</h1>"
        "<p style='color:#8892b0;'>平台预建的知识框架，覆盖高频考试科目</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    courses = get_courses()

    # 课程卡片展示
    st.markdown(
        "<div style='font-weight:600; color:#1a1a2e; margin-bottom:0.8rem;'>"
        "🎓 选择课程</div>",
        unsafe_allow_html=True,
    )
    course_cols = st.columns(min(len(courses), 3))
    for i, c in enumerate(courses):
        with course_cols[i % len(course_cols)]:
            st.markdown(
                f"<div class='card' style='text-align:center; cursor:pointer;'>"
                f"<div style='font-size:2rem;'>{c['icon']}</div>"
                f"<div style='font-weight:700; margin:0.3rem 0;'>{c['name']}</div>"
                f"<div style='color:#888; font-size:0.85rem;'>{c['desc']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    course_names = [f"{c['icon']} {c['name']}" for c in courses]
    selected = st.selectbox("选择课程", course_names)
    idx = course_names.index(selected)
    course = courses[idx]

    st.markdown("")

    # 章节导航
    st.markdown(
        f"<div style='font-weight:600; color:#1a1a2e; margin-bottom:0.5rem;'>"
        f"📖 {course['name']} - 章节选择</div>",
        unsafe_allow_html=True,
    )
    chapter_names = [ch["title"] for ch in course["chapters"]]
    selected_ch = st.selectbox("选择章节", chapter_names)
    ch_idx = chapter_names.index(selected_ch)
    chapter = course["chapters"][ch_idx]

    st.markdown("")
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown(render_chapter(chapter))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    if st.button(f"🧪 基于「{course['name']}」开始蒸馏", use_container_width=True, type="primary"):
        st.session_state.page = "开始蒸馏"
        full_text = "\n---\n".join(render_chapter(ch) for ch in course["chapters"])
        st.session_state["skeleton_text"] = full_text
        st.session_state["source_type"] = "skeleton"
        st.session_state["skeleton_title"] = course["name"]
        st.rerun()


# ============================================================
# 资料库（新增）
# ============================================================

elif current_page == "资料库":
    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h1 style='font-weight:700; color:#1a1a2e; margin-bottom:0.3rem;'>"
        "📁 资料库</h1>"
        "<p style='color:#8892b0;'>学长学姐整理的高质量复习资料，可直接下载或用于蒸馏</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # 课程筛选
    course_options = ["全部课程"] + [f"{c['code']} {c['name']}" for c in mock_data.COURSES]
    selected_filter = st.selectbox("按课程筛选", course_options)

    # 获取筛选后的资料
    if selected_filter == "全部课程":
        resources = mock_data.RESOURCES
    else:
        course_code = selected_filter.split()[0]
        resources = mock_data.get_resources_by_course(course_code)

    # 统计信息
    st.markdown(
        f"<div style='display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;'>"
        f"<div style='background:#f0f0ff;border-radius:10px;padding:0.8rem 1.2rem;text-align:center;'>"
        f"<div style='font-size:1.5rem;font-weight:700;color:#667eea;'>{len(resources)}</div>"
        f"<div style='color:#888;font-size:0.85rem;'>份资料</div></div>"
        f"<div style='background:#fff5f0;border-radius:10px;padding:0.8rem 1.2rem;text-align:center;'>"
        f"<div style='font-size:1.5rem;font-weight:700;color:#ff6b6b;'>{sum(r['downloads'] for r in resources)}</div>"
        f"<div style='color:#888;font-size:0.85rem;'>次下载</div></div>"
        f"<div style='background:#f0fff4;border-radius:10px;padding:0.8rem 1.2rem;text-align:center;'>"
        f"<div style='font-size:1.5rem;font-weight:700;color:#51cf66;'>{sum(r['likes'] for r in resources)}</div>"
        f"<div style='color:#888;font-size:0.85rem;'>个赞</div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # 资料列表
    for res in resources:
        verified_badge = "✅ 已认证" if res["is_verified"] else ""
        tags_html = " ".join([f"<span class='tag tag-primary' style='font-size:0.75rem;padding:0.12rem 0.5rem;'>{t}</span>" for t in res["tags"][:3]])

        with st.expander(f"{res['type_label']} **{res['title']}** {verified_badge}", expanded=False):
            st.markdown(
                f"<div style='margin-bottom:1rem;'>"
                f"<div style='display:flex;align-items:center;margin-bottom:0.6rem;'>"
                f"<div class='avatar' style='background:linear-gradient(135deg,#667eea,#764ba2);'>{res['avatar']}</div>"
                f"<div><span style='font-weight:600;color:#1a1a2e;'>{res['uploader']}</span>"
                f"<span style='color:#888;font-size:0.85rem;margin-left:0.5rem;'>{res['upload_time']}</span></div></div>"
                f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;margin-bottom:0.8rem;'>{tags_html}</div>"
                f"<div style='display:flex;gap:1.5rem;color:#888;font-size:0.85rem;margin-bottom:0.8rem;'>"
                f"<span>📥 {res['downloads']}下载</span>"
                f"<span>❤️ {res['likes']}</span>"
                f"<span>⭐ {res['rating']}</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # 蒸馏预览
            st.markdown("**📋 蒸馏预览**")
            st.markdown(res["distilled_preview"])

            # 操作按钮
            rcol1, rcol2, rcol3 = st.columns(3)
            with rcol1:
                st.download_button(
                    "📥 下载原文",
                    data=res["distilled_preview"],
                    file_name=f"{res['title']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with rcol2:
                if st.button(f"🧪 用此资料蒸馏", key=f"distill_{res['id']}", use_container_width=True):
                    st.session_state.page = "开始蒸馏"
                    st.session_state["skeleton_text"] = res["distilled_preview"]
                    st.session_state["source_type"] = "skeleton"
                    st.session_state["skeleton_title"] = res["title"]
                    st.rerun()
            with rcol3:
                st.button("❤️ 点赞", key=f"like_{res['id']}", use_container_width=True)


# ============================================================
# 社区（含发帖功能 + 动态数据）
# ============================================================

elif current_page == "社区":
    import random

    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h1 style='font-weight:700; color:#1a1a2e; margin-bottom:0.3rem;'>"
        "💬 学习社区</h1>"
        "<p style='color:#8892b0;'>和同学交流经验、分享心得、互助答疑</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ========== 发帖功能 ==========
    with st.expander("✍️ 发布新帖子", expanded=False):
        with st.form("new_post_form"):
            pcol1, pcol2 = st.columns([2, 1])
            with pcol1:
                post_title = st.text_input("帖子标题 *", placeholder="例如：马原期末复习怎么安排？")
            with pcol2:
                post_type = st.selectbox("帖子类型 *", [
                    ("💬 讨论", "discussion"),
                    ("❓ 求助", "help"),
                    ("💡 经验分享", "experience"),
                    ("⚠️ 避坑提醒", "pitfall"),
                    ("📝 分享资料", "share"),
                    ("❓ 提问", "question"),
                ], format_func=lambda x: x[0])

            course_options = ["不关联课程"] + [f"{c['code']} {c['name']}" for c in mock_data.COURSES]
            post_course = st.selectbox("关联课程（选填）", course_options)

            post_content = st.text_area(
                "帖子内容 *",
                placeholder="详细描述你的问题或想分享的内容...",
                height=120,
            )

            post_tags = st.text_input("标签（用空格分隔）", placeholder="例如：马原 期末 复习")

            submitted = st.form_submit_button("📤 发布帖子", use_container_width=True, type="primary")

            if submitted and post_title.strip() and post_content.strip():
                if "user_posts" not in st.session_state:
                    st.session_state.user_posts = []

                new_post = {
                    "id": f"user_{len(st.session_state.user_posts)+1}",
                    "title": post_title.strip(),
                    "author": "我（当前用户）",
                    "avatar": "我",
                    "course_id": post_course.split()[0] if post_course != "不关联课程" else None,
                    "course_name": post_course.split(" ", 1)[1] if post_course != "不关联课程" else "",
                    "type": post_type[1],
                    "type_label": post_type[0],
                    "content": post_content.strip(),
                    "replies": 0,
                    "likes": 0,
                    "views": random.randint(5, 20),
                    "created_at": "刚刚",
                    "is_hot": False,
                    "is_solved": False,
                    "tags": post_tags.split() if post_tags else [],
                    "best_answer": None,
                }
                st.session_state.user_posts.insert(0, new_post)
                st.success("✅ 帖子发布成功！")
                st.rerun()
            elif submitted:
                st.warning("请填写标题和内容后再发布")

    # ========== 资料分享功能 ==========
    st.markdown("---")
    st.markdown(
        "<div style='background:linear-gradient(135deg,#fff8e1,#fff3c4);border:1px solid #ffc107;"
        "border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem;'>"
        "<div style='display:flex;align-items:center;margin-bottom:0.5rem;'>"
        "<span style='font-size:1.3rem;margin-right:0.5rem;'>📤</span>"
        "<span style='font-weight:700;color:#1a1a2e;font-size:1.05rem;'>资料共享区</span>"
        "</div>"
        "<div style='color:#666;font-size:0.9rem;'>分享你的复习资料、笔记或整理好的知识点，帮助更多同学！</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("📁 分享我的资料", expanded=False):
        # ⚠️ 重要提示
        st.markdown(
            "<div style='background:#fff3cd;border:1px solid #ffc107;border-radius:8px;"
            "padding:0.7rem 1rem;margin-bottom:1rem;display:flex;align-items:start;'>"
            "<span style='font-size:1.2rem;margin-right:0.6rem;'>⚠️</span>"
            "<div><span style='font-weight:700;color:#856404;'>发布前请注意：</span>"
            "<span style='color:#856404;font-size:0.9rem;'>"
            "用户分享的资料未经官方审核，可能存在错误或不准确的内容。"
            "请在使用时仔细核对，如有疑问请查阅教材或咨询任课老师。"
            "如发现严重错误可点击举报。</span></div></div>",
            unsafe_allow_html=True,
        )

        with st.form("share_resource_form"):
            rcol1, rcol2 = st.columns([2, 1])
            with rcol1:
                res_title = st.text_input("资料标题 *", placeholder="例如：马原第三章思维导图")
            with rcol2:
                res_course = st.selectbox("所属课程 *", [f"{c['code']} {c['name']}" for c in mock_data.COURSES])

            res_type = st.selectbox("资料类型", [
                ("📝 笔记/总结", "notes"),
                ("🗺️ 思维导图", "mindmap"),
                ("📋 答题模板", "template"),
                ("⚠️ 易错点整理", "pitfalls"),
                ("📊 公式/考点速查", "cheatsheet"),
                ("📝 其他", "other"),
            ], format_func=lambda x: x[0])

            res_desc = st.text_area(
                "资料简介 *",
                placeholder="简要描述这份资料的内容和适用场景...",
                height=80,
            )

            # 资料内容输入
            content_method = st.radio("输入方式", ["直接粘贴文本内容", "上传文件"], horizontal=True)

            if content_method == "直接粘贴文本内容":
                res_content = st.text_area(
                    "资料内容 *",
                    placeholder="在这里粘贴你的笔记、总结或知识点...",
                    height=200,
                )
            else:
                uploaded_res_file = st.file_uploader(
                    "上传文件（支持 TXT、MD）",
                    type=["txt", "md"],
                    help="上传后会自动提取文本内容"
                )
                if uploaded_res_file:
                    res_content = uploaded_res_file.read().decode("utf-8")
                    st.success(f"已读取：{uploaded_res_file.name}（{len(res_content)}字）")
                else:
                    res_content = ""

            res_tags = st.text_input("标签（用空格分隔）", placeholder="例如：重点 期末 必背")

            # 声明确认
            confirm_share = st.checkbox(
                "我确认这份资料是我自己整理的，内容真实有效",
                value=False,
            )

            share_submitted = st.form_submit_button("📤 发布资料", use_container_width=True, type="primary")

            if share_submitted:
                if not res_title.strip() or not res_desc.strip():
                    st.warning("请填写资料标题和简介")
                elif not res_content.strip():
                    st.warning("请提供资料内容")
                elif not confirm_share:
                    st.warning("请勾选确认声明后再发布")
                else:
                    if "user_resources" not in st.session_state:
                        st.session_state.user_resources = []

                    new_res = {
                        "id": f"ures_{len(st.session_state.user_resources)+1}",
                        "title": res_title.strip(),
                        "course_id": res_course.split()[0],
                        "course_name": res_course.split(" ", 1)[1],
                        "type": res_type[1],
                        "type_label": res_type[0],
                        "uploader": "我（当前用户）",
                        "avatar": "我",
                        "upload_time": "刚刚",
                        "downloads": 0,
                        "likes": 0,
                        "rating": 0,
                        "tags": res_tags.split() if res_tags else [],
                        "is_verified": False,  # 用户分享的默认未认证
                        "distilled_preview": res_content.strip()[:1500],
                        "description": res_desc.strip(),
                    }
                    st.session_state.user_resources.insert(0, new_res)
                    st.success("✅ 资料发布成功！其他同学可以看到并下载了。")
                    st.info("💡 提示：你的资料显示为「待审核」状态，管理员审核后可获得认证标识。")
                    st.rerun()

    # ========== 显示用户分享的资料 ==========
    if "user_resources" in st.session_state and st.session_state.user_resources:
        st.markdown("---")
        st.markdown(
            "<div style='font-weight:700;color:#1a1a2e;margin-bottom:1rem;'>"
            "📋 我分享的资料</div>",
            unsafe_allow_html=True,
        )

        for res in st.session_state.user_resources:
            verified_badge = "✅ 已认证" if res["is_verified"] else "⏳ 待审核"
            badge_color = "#51cf66" if res["is_verified"] else "#ffc107"

            st.markdown(
                f"<div class='resource-card' style='border-left:4px solid {badge_color};'>"
                f"<div style='display:flex;align-items:center;margin-bottom:0.5rem;'>"
                f"<span style='margin-right:0.5rem;'>{res['type_label']}</span>"
                f"<span style='font-weight:700;color:#1a1a2e;'>{res['title']}</span>"
                f"<span style='margin-left:auto;background:{badge_color};color:white;"
                f"padding:0.15rem 0.6rem;border-radius:10px;font-size:0.75rem;'>{verified_badge}</span></div>"
                f"<div style='color:#555;font-size:0.9rem;margin-bottom:0.5rem;'>{res['description']}</div>"
                f"<div style='display:flex;gap:1rem;color:#888;font-size:0.82rem;flex-wrap:wrap;'>"
                f"<span>📚 {res['course_name']}</span>"
                f"<span>👁️ {res['downloads']}次下载</span>"
                f"<span>❤️ {res['likes']}</span>"
                f"<span>🕐 {res['upload_time']}</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            with st.expander("查看资料详情 👇", expanded=False):
                st.markdown(res["distilled_preview"])
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        "📥 下载",
                        data=res["distilled_preview"],
                        file_name=f"{res['title']}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                with c2:
                    st.button("❤️ 点赞", key=f"res_like_{res['id']}", use_container_width=True)

            st.markdown("")

    st.markdown("---")

    # 左右布局：帖子列表 + 排行榜
    post_col, rank_col = st.columns([3, 1])

    with post_col:
        # 帖子筛选
        post_filter = st.selectbox(
            "筛选帖子",
            ["全部帖子", "🔥 热门讨论", "❓ 求助问答", "💡 经验分享", "⚠️ 避坑提醒"],
        )

        # 合并预设帖子和用户帖子
        all_posts = list(mock_data.POSTS)
        if "user_posts" in st.session_state:
            all_posts = st.session_state.user_posts + all_posts

        # 根据筛选显示帖子
        if post_filter == "🔥 热门讨论":
            posts = [p for p in all_posts if p.get("is_hot")]
        elif post_filter == "❓ 求助问答":
            posts = [p for p in all_posts if p["type"] in ["help", "question"]]
        elif post_filter == "💡 经验分享":
            posts = [p for p in all_posts if p["type"] in ["experience", "share"]]
        elif post_filter == "⚠️ 避坑提醒":
            posts = [p for p in all_posts if p["type"] == "pitfall"]
        else:
            posts = all_posts

        # 显示帖子（带动态数据 + 实时提示）
        for post in posts:
            hot_tag = "🔥" if post.get("is_hot") else ""
            solved_tag = "✅ 已解决" if post.get("is_solved") else ""
            is_user_post = post["id"].startswith("user_")

            # 动态化数据：基础值 + 随机波动（模拟实时更新）
            dynamic_likes = post["likes"] + random.randint(0, max(1, post["likes"]//10))
            dynamic_views = post["views"] + random.randint(0, max(5, post["views"]//5))

            border_color = "#51cf66" if is_user_post else "#667eea"

            st.markdown(
                f"<div class='post-card' style='border-left-color:{border_color};'>"
                f"<div style='display:flex;align-items:center;margin-bottom:0.5rem;'>"
                f"<div class='avatar' style='background:linear-gradient(135deg,#667eea,{['#764ba2','#51cf66','#ff6b6b','#ffd43b','#74c0fc'][hash(post['author'])%5]});'>"
                f"{post['avatar']}</div>"
                f"<div><span style='font-weight:600;color:#1a1a2e;'>{post['author']}</span>"
                f"<span style='color:#888;font-size:0.8rem;margin-left:0.5rem;'>{post['created_at']}</span></div>"
                f"<div style='margin-left:auto;display:flex;gap:0.4rem;align-items:center;'>"
                f"<span style='font-size:0.8rem;'>{hot_tag}{solved_tag}</span>"
                f"{'<span style=\"background:#51cf66;color:white;padding:0.15rem 0.5rem;border-radius:10px;font-size:0.7rem;\">我的帖子</span>' if is_user_post else ''}"
                f"</div></div>"
                f"<div style='font-weight:700;color:#1a1a2e;font-size:1.05rem;margin-bottom:0.4rem;'>{post['title']}</div>"
                f"<div style='color:#555;font-size:0.9rem;line-height:1.6;margin-bottom:0.6rem;'>{post['content'][:250]}{'...' if len(post['content'])>250 else ''}</div>"
                f"<div style='display:flex;gap:1rem;color:#888;font-size:0.82rem;flex-wrap:wrap;'>"
                f"<span>{post['type_label']}</span>"
                f"<span>💬 {post['replies']}回复</span>"
                f"<span>❤️ {dynamic_likes}</span>"
                f"<span>👁️ {dynamic_views}浏览</span></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # 最佳答案
            if post.get("best_answer"):
                with st.expander("查看最佳答案 👇", expanded=False):
                    st.info(post["best_answer"])

            # 互动按钮
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                st.button(f"👍 点赞 ({dynamic_likes})", key=f"like_{post['id']}")
            with btn_col2:
                st.button(f"💬 回复 ({post['replies']})", key=f"reply_{post['id']}")
            with btn_col3:
                if is_user_post and not post.get("is_solved"):
                    if st.button(f"✅ 标记已解决", key=f"solve_{post['id']}"):
                        for up in st.session_state.user_posts:
                            if up["id"] == post["id"]:
                                up["is_solved"] = True
                                break
                        st.rerun()

            st.markdown("")

    with rank_col:
        # 排行榜
        st.markdown(
            "<div style='background:white;border-radius:12px;padding:1rem;border:1px solid #eef0f6;'>"
            "<div style='font-weight:700;color:#1a1a2e;margin-bottom:1rem;text-align:center;'>🏆 贡献榜</div>"
            "<div style='text-align:center;color:#888;font-size:0.75rem;margin-bottom:0.8rem;'>实时更新中...</div>",
            unsafe_allow_html=True,
        )

        for item in mock_data.LEADERBOARD:
            rank_class = "rank-1" if item["rank"]==1 else ("rank-2" if item["rank"]==2 else ("rank-3" if item["rank"]==3 else "rank-other"))
            colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#667eea", "#764ba2", "#51cf66", "#ff6b6b", "#ffd43b"]

            # 动态分数
            dynamic_points = item["points"] + random.randint(-5, 15)

            st.markdown(
                f"<div class='rank-item {rank_class}'>"
                f"<div class='rank-num'>{item['rank']}</div>"
                f"<div class='avatar' style='background:{colors[item['rank']-1]};width:30px;height:30px;font-size:0.75rem;'>"
                f"{item['avatar']}</div>"
                f"<div style='flex:1;'>"
                f"<div style='font-weight:600;font-size:0.85rem;color:#1a1a2e;'>{item['name']}</div>"
                f"<div style='color:#888;font-size:0.75rem;'>{dynamic_points}分 · {item['contributions']}贡献</div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 模型设置
# ============================================================

elif current_page == "模型设置":
    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h1 style='font-weight:700; color:#1a1a2e; margin-bottom:0.3rem;'>"
        "⚙️ 模型设置</h1>"
        "<p style='color:#8892b0;'>配置蒸馏引擎使用的大模型 API，支持任何 OpenAI 兼容格式</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # 模型类型卡片
    st.markdown(
        "<div style='font-weight:600; color:#1a1a2e; margin-bottom:0.8rem;'>"
        "🎯 选择模型类型</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "<div class='card' style='text-align:center; cursor:pointer;'>"
            "<div style='font-size:1.8rem;'>🧮</div>"
            "<div style='font-weight:700; margin:0.3rem 0;'>数学推理型</div>"
            "<div style='color:#888; font-size:0.85rem;'>高数、线代、大物计算题</div>"
            "<div style='color:#667eea; font-size:0.8rem; margin-top:0.3rem;'>DeepSeek-R1 / Qwen-Math</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            "<div class='card' style='text-align:center; cursor:pointer;'>"
            "<div style='font-size:1.8rem;'>📖</div>"
            "<div style='font-weight:700; margin:0.3rem 0;'>文本处理型</div>"
            "<div style='color:#888; font-size:0.85rem;'>文科、概念理解、长篇材料</div>"
            "<div style='color:#667eea; font-size:0.8rem; margin-top:0.3rem;'>Qwen-Plus / GLM-4</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    st.markdown(
        "<div style='font-weight:600; color:#1a1a2e; margin-bottom:0.8rem;'>"
        "🔑 API 配置</div>",
        unsafe_allow_html=True,
    )

    model_type_options = ["math", "text"]
    mt_idx = model_type_options.index(st.session_state.model_type) if st.session_state.model_type in model_type_options else 0
    st.session_state.model_type = st.radio(
        "当前选择的模型类型",
        model_type_options,
        format_func=lambda x: ("🧮 数学推理型" if x == "math" else "📖 文本处理型"),
        horizontal=True,
        index=mt_idx,
    )

    st.session_state.api_key = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        help="你的API密钥，仅存于本地浏览器，不会上传到服务器"
    )

    preset_options = ["阿里云 DashScope（通义千问）", "DeepSeek", "SiliconFlow 硅基流动", "自定义"]
    saved_preset = st.session_state.get("api_preset", preset_options[0])
    saved_idx = preset_options.index(saved_preset) if saved_preset in preset_options else 0

    preset = st.selectbox(
        "选择API服务（或自定义）",
        preset_options,
        index=saved_idx,
    )
    st.session_state.api_preset = preset

    preset_urls = {
        "阿里云 DashScope（通义千问）": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "DeepSeek": "https://api.deepseek.com/v1",
        "SiliconFlow 硅基流动": "https://api.siliconflow.cn/v1",
        "自定义": "",
    }

    if preset == "自定义":
        st.session_state.base_url = st.text_input(
            "自定义 API Base URL",
            value=st.session_state.base_url,
            placeholder="https://your-api.com/v1",
        )
    else:
        st.session_state.base_url = preset_urls[preset]

    preset_models = {
        "阿里云 DashScope（通义千问）": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"],
        "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
        "SiliconFlow 硅基流动": ["Qwen/Qwen2.5-72B-Instruct", "deepseek-ai/DeepSeek-V3"],
        "自定义": [],
    }

    models = preset_models.get(preset, [])
    if models:
        saved_model = st.session_state.get("api_model_name", models[0])
        model_idx = models.index(saved_model) if saved_model in models else 0
        chosen_model = st.selectbox("选择模型", models, index=model_idx)
        st.session_state.model_name = chosen_model
        st.session_state.api_model_name = chosen_model
    else:
        st.session_state.model_name = st.text_input(
            "模型名称",
            value=st.session_state.get("custom_model_name", "") or st.session_state.model_name,
            placeholder="输入模型名称",
        )
        st.session_state.custom_model_name = st.session_state.model_name

    st.markdown("---")

    st.markdown("### SMTP 邮件配置（反馈功能）")
    st.markdown("配置后，用户提交的反馈会通过邮件发送到你指定的邮箱。")

    st.session_state.smtp_host = st.text_input(
        "SMTP 服务器",
        value=st.session_state.get("smtp_host", "smtp.qq.com"),
        placeholder="smtp.qq.com",
        help="QQ邮箱: smtp.qq.com | 163邮箱: smtp.163.com | 阿里邮箱: smtp.aliyun.com"
    )

    st.session_state.smtp_port = st.number_input(
        "SMTP 端口",
        value=st.session_state.get("smtp_port", 465),
        min_value=1,
        max_value=65535,
        help="SSL端口通常为465，TLS端口通常为587"
    )

    st.session_state.smtp_email = st.text_input(
        "发件邮箱",
        value=st.session_state.get("smtp_email", "2687033737@qq.com"),
        placeholder="your-email@qq.com",
        help="用于发送反馈邮件的邮箱地址"
    )

    st.session_state.smtp_auth_code = st.text_input(
        "SMTP 授权码",
        value=st.session_state.get("smtp_auth_code", ""),
        type="password",
        placeholder="在邮箱设置中生成的授权码（不是登录密码）",
        help="QQ邮箱：设置 → 账户 → POP3/SMTP服务 → 生成授权码"
    )

    if st.session_state.get("smtp_auth_code"):
        st.success("✅ SMTP已配置，反馈将自动发送邮件")
    else:
        st.warning("⚠️ 未配置SMTP授权码，反馈仅保存到本地")

    st.markdown("---")

    if st.session_state.api_key:
        st.success(f"✅ API已配置")
        st.info(f"当前配置：{preset} / {st.session_state.model_name} / {'数学推理' if st.session_state.model_type == 'math' else '文本处理'}")
    else:
        st.warning("⚠️ 未配置API Key，蒸馏将使用模板模式（基础功能可用，但质量不如LLM模式）")

    st.markdown("---")
    st.markdown(
        "💡 **提示**：API Key 仅保存在你的浏览器本地（Session State），不会上传到任何服务器。"
        "刷新页面后需要重新输入。"
    )


# ============================================================
# 反馈
# ============================================================

elif current_page == "反馈":
    st.markdown(
        "<div style='margin-bottom:1.5rem;'>"
        "<h1 style='font-weight:700; color:#1a1a2e; margin-bottom:0.3rem;'>"
        "💬 产品反馈</h1>"
        "<p style='color:#8892b0;'>你的反馈会直接发送到产品负责人邮箱</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("feedback_form"):
        feedback_type = st.selectbox(
            "反馈类型",
            ["功能建议", "Bug报告", "使用体验", "蒸馏质量", "其他"],
        )
        feedback_email = st.text_input(
            "你的联系方式（选填，方便我们回复你）",
            placeholder="邮箱/QQ/微信",
        )
        feedback_content = st.text_area(
            "反馈内容",
            placeholder="请描述你的想法、遇到的问题、或任何想说的话...",
            height=200,
        )
        submitted = st.form_submit_button("📮 提交反馈", use_container_width=True, type="primary")

        if submitted and feedback_content.strip():
            feedback_file = os.path.join(os.path.dirname(__file__), "data", "feedbacks.txt")
            os.makedirs(os.path.dirname(feedback_file), exist_ok=True)
            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"类型：{feedback_type}\n")
                f.write(f"联系方式：{feedback_email or '未填写'}\n")
                f.write(f"内容：{feedback_content}\n")

            smtp_auth_code = st.session_state.get("smtp_auth_code", "")
            smtp_host = st.session_state.get("smtp_host", "smtp.qq.com")
            smtp_port = st.session_state.get("smtp_port", 465)
            smtp_email = st.session_state.get("smtp_email", "2687033737@qq.com")

            email_sent = False
            if smtp_auth_code:
                try:
                    msg = MIMEMultipart()
                    msg["From"] = smtp_email
                    msg["To"] = smtp_email
                    msg["Subject"] = f"[一切皆蒸馏反馈] {feedback_type}"

                    body = f"""反馈类型：{feedback_type}
用户联系方式：{feedback_email or '未填写'}

反馈内容：
{feedback_content}

---
来自「一切皆蒸馏」产品反馈系统
"""
                    msg.attach(MIMEText(body, "plain", "utf-8"))

                    server = smtplib.SMTP_SSL(smtp_host, smtp_port)
                    server.login(smtp_email, smtp_auth_code)
                    server.sendmail(smtp_email, [smtp_email], msg.as_string())
                    server.quit()
                    email_sent = True
                except Exception as e:
                    st.warning(f"邮件发送失败：{str(e)}")

            st.success("✅ 反馈已收到！感谢你的宝贵意见。")

            if email_sent:
                st.info(" 反馈已通过邮件发送。")
            else:
                st.info("📧 邮件发送功能需要配置SMTP授权码，当前反馈已保存到本地。")

        elif submitted:
            st.warning("请填写反馈内容后再提交")
