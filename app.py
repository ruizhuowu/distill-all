"""
一切皆蒸馏 - 主应用
面向大学生的知识蒸馏备考平台
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
    extract_text, distill, distill_with_llm, METHODS,
    split_into_sections, extract_key_sentences
)
from knowledge_base import get_courses, render_course, render_chapter

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
# 自定义样式
# ============================================================

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.1rem;
        color: #666;
    }
    .method-card {
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        text-align: center;
        transition: all 0.2s;
    }
    .method-card:hover {
        border-color: #4CAF50;
        background: #f9fff9;
    }
    .stAlert { margin-top: 0.5rem; }
    div[data-testid="stSidebar"] { min-width: 240px; }
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
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# 侧边栏导航
# ============================================================

with st.sidebar:
    st.markdown("## 🧪 一切皆蒸馏")
    st.markdown("*把任何学习材料变成你的备考系统*")
    st.markdown("---")

    # 页面 key → 带 emoji 标签的映射
    page_labels = ["🏠 首页", "🧪 开始蒸馏", "📚 知识骨架", "⚙️ 模型设置", "💬 反馈"]
    page_keys = ["首页", "开始蒸馏", "知识骨架", "模型设置", "反馈"]
    default_idx = page_keys.index(st.session_state.page) if st.session_state.page in page_keys else 0

    page = st.radio(
        "导航",
        page_labels,
        index=default_idx,
        label_visibility="collapsed",
    )

    # 映射到页面key
    page_map = {
        "🏠 首页": "首页",
        "🧪 开始蒸馏": "开始蒸馏",
        "📚 知识骨架": "知识骨架",
        "⚙️ 模型设置": "模型设置",
        "💬 反馈": "反馈",
    }
    current_page = page_map[page]
    st.session_state.page = current_page

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#999; font-size:0.8rem;'>"
        "v0.1 Demo · 一切皆蒸馏</div>",
        unsafe_allow_html=True
    )

# ============================================================
# 首页
# ============================================================

if current_page == "首页":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown("# 🧪 一切皆蒸馏")
    st.markdown("#### 把任何学习材料变成你自己的备考系统")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 产品介绍
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📤 上传材料")
        st.markdown("PDF课件、文本笔记、习题集——任何学习材料都能导入")
    with col2:
        st.markdown("### 🧪 选择蒸馏方式")
        st.markdown("6种标准化蒸馏方式，从提纲到费曼到Cornell笔记")
    with col3:
        st.markdown("### 📝 获得备考系统")
        st.markdown("结构化笔记 + 自测题 + 可编辑，变成你自己的复习体系")

    st.markdown("---")

    # 蒸馏方式一览
    st.markdown("### 六种蒸馏方式")
    cols = st.columns(3)
    method_items = list(METHODS.items())
    for i, (key, info) in enumerate(method_items):
        with cols[i % 3]:
            st.markdown(f"#### {info['icon']} {info['name']}")
            st.markdown(f"*{info['desc']}*")

    st.markdown("---")

    # 快速开始
    st.markdown("### 🚀 快速开始")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("上传材料开始蒸馏", use_container_width=True):
            st.session_state.page = "开始蒸馏"
            st.rerun()
    with col2:
        if st.button("浏览预建知识骨架", use_container_width=True):
            st.session_state.page = "知识骨架"
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#888; font-size:0.9rem;'>"
        "💡 也可以先浏览「知识骨架」，看看高数、线代、大物的预建知识框架"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# 开始蒸馏
# ============================================================

elif current_page == "开始蒸馏":

    st.markdown("# 🧪 开始蒸馏")

    # 检查是否有已蒸馏的结果
    if st.session_state.distill_result is not None:
        st.success("蒸馏完成！查看结果 👇")

        # 显示蒸馏结果
        result = st.session_state.edited_result or st.session_state.distill_result

        # 编辑区域
        st.markdown("### 蒸馏结果")
        st.markdown(f"**蒸馏方式：** {st.session_state.distill_method}")
        st.markdown(f"**材料标题：** {st.session_state.distill_title}")

        # Markdown渲染预览
        st.markdown("---")
        st.markdown(result)
        st.markdown("---")

        # 编辑模式
        with st.expander("📝 编辑蒸馏结果", expanded=False):
            edited = st.text_area(
                "直接编辑Markdown内容",
                value=st.session_state.edited_result or st.session_state.distill_result,
                height=400,
                key="edit_area"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("保存修改"):
                    st.session_state.edited_result = edited
                    st.rerun()
            with col2:
                if st.button("放弃修改"):
                    st.session_state.edited_result = None
                    st.rerun()

        # 导出
        st.markdown("### 导出")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 下载 Markdown 文件",
                data=result,
                file_name=f"{st.session_state.distill_title}_蒸馏结果.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col2:
            if st.button("🔄 蒸馏新材料", use_container_width=True):
                st.session_state.distill_result = None
                st.session_state.edited_result = None
                st.rerun()

    else:
        # 蒸馏输入界面
        st.markdown("### 第一步：选择内容来源")

        source_tab1, source_tab2 = st.tabs(["📤 上传文件", "📚 从知识骨架选择"])

        with source_tab1:
            uploaded_file = st.file_uploader(
                "上传学习材料（支持 PDF、TXT、MD）",
                type=["pdf", "txt", "md"],
                help="上传你的课件、笔记、习题集等学习材料"
            )
            if uploaded_file:
                st.session_state["uploaded_file"] = uploaded_file
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
                # 合并选中章节的内容
                combined = []
                for ch in course["chapters"]:
                    if ch["title"] in selected_chapters:
                        combined.append(render_chapter(ch))
                skeleton_text = "\n---\n".join(combined)
                st.session_state["skeleton_text"] = skeleton_text
                st.session_state["source_type"] = "skeleton"
                st.session_state["skeleton_title"] = f"{course['name']} - {' + '.join(selected_chapters)}"
                st.info(f"已选择 {len(selected_chapters)} 个章节的知识骨架内容")

        st.markdown("---")
        st.markdown("### 第二步：选择蒸馏方式")

        # 用卡片式布局展示蒸馏方式，点击卡片选中
        method_keys_list = list(METHODS.keys())
        method_cols = st.columns(3)
        for i, key in enumerate(method_keys_list):
            info = METHODS[key]
            with method_cols[i % 3]:
                is_chosen = (st.session_state.get("chosen_method") == key)
                border_color = "#4CAF50" if is_chosen else "#e0e0e0"
                bg_color = "#f0fff0" if is_chosen else "white"
                st.markdown(
                    f"""<div style="padding:1rem; border:2px solid {border_color}; border-radius:8px;
                        background:{bg_color}; text-align:center; cursor:pointer; min-height:80px;"
                        onclick="void(0)">
                        <div style="font-size:1.5rem;">{info['icon']}</div>
                        <div style="font-weight:bold; margin:0.3rem 0;">{info['name']}</div>
                        <div style="font-size:0.85rem; color:#666;">{info['desc']}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )
                if st.button(f"选择 {info['name']}", key=f"select_{key}", use_container_width=True,
                             type="primary" if is_chosen else "secondary"):
                    st.session_state["chosen_method"] = key
                    st.rerun()

        chosen_method = st.session_state.get("chosen_method", method_keys_list[0])

        st.markdown("---")
        st.markdown("### 第三步：开始蒸馏")

        title_input = st.text_input(
            "给这份蒸馏结果起个名字",
            value="我的蒸馏笔记",
            placeholder="例如：高数第三章复习、大物力学期末速通..."
        )

        if st.button("🧪 开始蒸馏！", use_container_width=True, type="primary"):
            # 获取源文本
            source_text = ""
            source_title = title_input

            if st.session_state.get("source_type") == "upload":
                uf = st.session_state.get("uploaded_file")
                if uf:
                    file_bytes = uf.read()
                    source_text = extract_text(file_bytes, uf.name)
                    source_title = title_input or uf.name.replace(".pdf", "").replace(".txt", "")
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
                if api_key:
                    # LLM模式
                    base_url = st.session_state.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
                    model = st.session_state.get("model_name", "qwen-plus")
                    result = distill_with_llm(source_text, chosen_method, source_title,
                                              api_key, base_url, model)
                else:
                    # 模板模式
                    result = distill(source_text, chosen_method, source_title)

            st.session_state.distill_result = result
            st.session_state.distill_method = METHODS[chosen_method]["name"]
            st.session_state.distill_title = source_title
            st.session_state.edited_result = None
            st.rerun()


# ============================================================
# 知识骨架浏览
# ============================================================

elif current_page == "知识骨架":
    st.markdown("# 📚 知识骨架")
    st.markdown("平台预建的知识框架，覆盖高频考试科目。可以直接基于这些骨架进行蒸馏，也可以上传自己的材料。")
    st.markdown("---")

    courses = get_courses()
    course_names = [f"{c['icon']} {c['name']}" for c in courses]
    selected = st.selectbox("选择课程", course_names)
    idx = course_names.index(selected)
    course = courses[idx]

    st.markdown(f"**{course['desc']}**")
    st.markdown("---")

    # 章节导航
    chapter_names = [ch["title"] for ch in course["chapters"]]
    selected_ch = st.selectbox("选择章节", chapter_names)
    ch_idx = chapter_names.index(selected_ch)
    chapter = course["chapters"][ch_idx]

    st.markdown("---")
    st.markdown(render_chapter(chapter))

    st.markdown("---")
    if st.button(f"🧪 基于「{course['name']}」开始蒸馏"):
        st.session_state.page = "开始蒸馏"
        # 预设知识骨架为源
        full_text = "\n---\n".join(render_chapter(ch) for ch in course["chapters"])
        st.session_state["skeleton_text"] = full_text
        st.session_state["source_type"] = "skeleton"
        st.session_state["skeleton_title"] = course["name"]
        st.rerun()


# ============================================================
# 模型设置
# ============================================================

elif current_page == "模型设置":
    st.markdown("# ⚙️ 模型设置")
    st.markdown("配置蒸馏引擎使用的大模型API。支持任何 OpenAI 兼容格式的 API（DashScope、DeepSeek、SiliconFlow 等）。")

    st.markdown("---")

    st.markdown("### 模型类型")
    st.markdown("针对不同科目选择不同类型的模型，获得更好的蒸馏效果：")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🧮 数学推理型")
        st.markdown("适合：高数、线代、大物计算题等")
        st.markdown("推荐：DeepSeek-R1、Qwen-Math")
    with col2:
        st.markdown("#### 📖 文本处理型")
        st.markdown("适合：文科、概念理解、长篇材料等")
        st.markdown("推荐：Qwen-Plus、GLM-4")

    st.markdown("---")

    st.markdown("### API 配置")

    st.session_state.model_type = st.radio(
        "当前选择的模型类型",
        ["math", "text"],
        format_func=lambda x: "🧮 数学推理型" if x == "math" else "📖 文本处理型",
        horizontal=True,
    )

    st.session_state.api_key = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        help="你的API密钥，仅存于本地浏览器，不会上传到服务器"
    )

    # 预设API服务
    preset = st.selectbox(
        "选择API服务（或自定义）",
        ["阿里云 DashScope（通义千问）", "DeepSeek", "SiliconFlow 硅基流动", "自定义"],
    )

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

    # 模型名称
    preset_models = {
        "阿里云 DashScope（通义千问）": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-long"],
        "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
        "SiliconFlow 硅基流动": ["Qwen/Qwen2.5-72B-Instruct", "deepseek-ai/DeepSeek-V3"],
        "自定义": [],
    }

    models = preset_models.get(preset, [])
    if models:
        chosen_model = st.selectbox("选择模型", models)
        st.session_state.model_name = chosen_model
    else:
        st.session_state.model_name = st.text_input(
            "模型名称",
            value=st.session_state.get("custom_model_name", "") or st.session_state.model_name,
            placeholder="输入模型名称",
        )
        st.session_state.custom_model_name = st.session_state.model_name

    st.markdown("---")

    # 状态显示
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
    st.markdown("# 💬 产品反馈")
    st.markdown("你的每一条反馈都会直接发送到产品负责人的邮箱，帮助我们改进产品。")
    st.markdown("---")

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
            # 尝试发送邮件
            try:
                msg = MIMEMultipart()
                msg["From"] = "2687033737@qq.com"
                msg["To"] = "2687033737@qq.com"
                msg["Subject"] = f"[一切皆蒸馏反馈] {feedback_type}"

                body = f"""反馈类型：{feedback_type}
用户联系方式：{feedback_email or '未填写'}

反馈内容：
{feedback_content}

---
来自「一切皆蒸馏」产品反馈系统
"""
                msg.attach(MIMEText(body, "plain", "utf-8"))

                # 注意：这里需要SMTP授权码才能发送
                # Demo阶段先保存反馈到本地
                feedback_file = os.path.join(os.path.dirname(__file__), "data", "feedbacks.txt")
                os.makedirs(os.path.dirname(feedback_file), exist_ok=True)
                with open(feedback_file, "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*50}\n")
                    f.write(f"时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"类型：{feedback_type}\n")
                    f.write(f"联系方式：{feedback_email or '未填写'}\n")
                    f.write(f"内容：{feedback_content}\n")

                st.success("✅ 反馈已收到！感谢你的宝贵意见。")
                st.info("📧 邮件发送功能需要配置SMTP授权码，当前反馈已保存到本地。")

            except Exception as e:
                # 即使邮件发送失败，也保存本地
                feedback_file = os.path.join(os.path.dirname(__file__), "data", "feedbacks.txt")
                os.makedirs(os.path.dirname(feedback_file), exist_ok=True)
                with open(feedback_file, "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*50}\n")
                    f.write(f"时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"类型：{feedback_type}\n")
                    f.write(f"联系方式：{feedback_email or '未填写'}\n")
                    f.write(f"内容：{feedback_content}\n")
                st.success("✅ 反馈已保存到本地！")

        elif submitted:
            st.warning("请填写反馈内容后再提交")
