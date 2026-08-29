# 一切皆蒸馏 — 项目全景文档

> 本文档面向 AI 助手，目标是让你在读完后**完全理解**这个项目的全貌：做了什么、没做什么、怎么做的、为什么这么做、接下来该做什么。

---

## 一、项目定位与愿景

### 1.1 一句话描述
**「一切皆蒸馏」是一个面向大学生的知识蒸馏备考平台**，核心理念是：把任何学习材料（课件、笔记、习题集）通过 6 种标准化方法"蒸馏"成结构化的备考笔记系统。

### 1.2 目标用户
- 大学生（主要），备考期末/考研
- 需要把零散学习材料整理成系统化笔记的人

### 1.3 核心隐喻
用"蒸馏"比喻知识提炼过程——把厚重的教材"蒸发"掉冗余，留下精华"凝结"成可复习的结构化笔记。

---

## 二、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端框架** | Streamlit（>=1.30.0） | 纯 Python Web 框架，无需写前端代码 |
| **PDF 解析** | PyMuPDF（>=1.23.0） | 从上传的 PDF 中提取文本 |
| **LLM 调用** | openai SDK（>=1.0.0） | 兼容任何 OpenAI 格式的 API |
| **邮件发送** | smtplib（Python 内置） | SMTP SSL 发送反馈邮件 |
| **部署** | Streamlit Community Cloud | 免费社区版，连接 GitHub 仓库自动部署 |
| **版本管理** | Git + GitHub | 仓库地址见下方 |

### 2.1 支持的 LLM API 服务
用户可在"模型设置"页面选择：
- **阿里云 DashScope**（通义千问系列：qwen-plus, qwen-turbo, qwen-max, qwen-long）
- **DeepSeek**（deepseek-chat, deepseek-reasoner）
- **SiliconFlow 硅基流动**（Qwen2.5-72B, DeepSeek-V3）
- **自定义**（任何 OpenAI 兼容 API）

---

## 三、项目文件结构

```
一切皆蒸馏/
├── app.py                    # 主应用（963行），包含所有页面 UI + 交互逻辑
├── engine.py                 # 蒸馏引擎（384行），6种蒸馏方式的实现 + LLM调用
├── knowledge_base.py         # 知识骨架（459行），预建的高数/线代/大物知识数据
├── requirements.txt          # 依赖：streamlit, PyMuPDF, openai
├── run.bat                   # Windows 一键启动脚本
├── .gitignore                # 忽略 __pycache__, data/feedbacks.txt, .env
├── .streamlit/
│   └── config.toml           # Streamlit 全局主题配置
└── data/                     # 数据目录（feedbacks.txt 存反馈，已被 gitignore）
```

---

## 四、核心架构详解

### 4.1 app.py — 主应用（963行）

**整体结构**（按代码顺序）：

| 行号范围 | 功能模块 | 说明 |
|----------|----------|------|
| 1-31 | 导入 + 页面配置 | 导入依赖，set_page_config（wide布局，🧪图标） |
| 33-35 | session_state 初始化 | 初始化 `page` 状态，防止首次加载 ValueError |
| 41-222 | **全局 CSS 注入** | 渐变科技风样式：按钮、卡片、侧边栏、输入框、标签等 |
| 228-250 | **Session State 默认值** | 所有状态的默认值字典（page, distill_result, api_key, model_type 等） |
| 256-295 | **侧边栏导航** | Logo区 + 5个导航项（st.radio）+ 版本号 |
| 302-409 | **首页（Landing Page）** | Hero区 + CTA按钮 + 三步引导卡片 + 6种蒸馏方式展示 + 底部引导 |
| 416-631 | **开始蒸馏页面** | 上传/骨架选择 → 蒸馏方式选择（卡片式）→ 执行蒸馏 → 结果展示 |
| 638-701 | **知识骨架浏览** | 课程卡片展示 → 课程/章节选择 → 内容渲染 → 跳转蒸馏 |
| 708-877 | **模型设置** | 模型类型选择 → API配置（预设/自定义）→ SMTP邮件配置 → 状态显示 |
| 884-963 | **反馈页面** | 表单（类型/联系方式/内容）→ 保存到本地 + SMTP邮件发送 |

**关键 Session State 变量**：
```python
defaults = {
    "page": "首页",              # 当前页面
    "distill_result": None,      # 蒸馏结果（Markdown字符串）
    "distill_method": None,      # 蒸馏方式名称（显示用）
    "distill_title": None,       # 蒸馏标题
    "edited_result": None,       # 用户编辑后的结果
    "api_key": "",               # LLM API Key
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen-plus",   # 当前模型名
    "model_type": "text",        # math / text
    "chosen_method": "outline",  # 当前选中的蒸馏方式 key
    "api_preset": "阿里云 DashScope（通义千问）",
    "api_model_name": "qwen-plus",
    "smtp_host": "smtp.qq.com",
    "smtp_port": 465,
    "smtp_email": "2687033737@qq.com",
    "smtp_auth_code": "",        # SMTP授权码（密码）
}
```

**页面导航机制**：
- 侧边栏用 `st.radio` 展示 5 个导航项（带 emoji 前缀）
- 通过 `page_map` 字典映射 label → page key
- 选中后写入 `st.session_state.page`，用 `if/elif` 链渲染对应页面
- 页面间跳转通过修改 `st.session_state.page` + `st.rerun()` 实现

### 4.2 engine.py — 蒸馏引擎（384行）

**核心函数**：

| 函数 | 功能 |
|------|------|
| `extract_text(file_bytes, filename)` | 根据文件类型提取文本（PDF/TXT/MD） |
| `extract_pdf_text(file_bytes)` | PyMuPDF 提取 PDF 文本 |
| `split_into_sections(text)` | 按标题行/空行切分长文本 |
| `extract_key_sentences(text, max_count)` | 基于关键词权重提取关键句子 |
| `distill(source_text, method, title)` | **模板模式**主入口，分发到6种蒸馏函数 |
| `distill_with_llm(...)` | **LLM模式**，调用 OpenAI 兼容 API |
| `_build_llm_prompt(...)` | 构建 LLM 蒸馏 Prompt |

**6种蒸馏方式**（METHODS 字典）：
```python
"outline"  → 📋 提纲式     — 层级结构，提取要点
"qa"       → ❓ Q&A式      — 问答对照，自测用
"feynman"  → 🧠 费曼式     — 大白话讲透，留空让用户填
"formula"  → 📐 公式卡片   — 提取公式/定理，留空填适用场景
"mindmap"  → 🗺️ 思维导图   — Mermaid mindmap 语法
"cornell"  → 📝 Cornell笔记 — 表格形式，线索+笔记
```

**双模式运行机制**：
- **模板模式**（无需 API Key）：纯 Python 文本处理，基于关键词提取和模板填充，质量有限但零成本
- **LLM 模式**（需 API Key）：调用大模型生成高质量蒸馏结果，如果调用失败会自动降级到模板模式并显示警告

### 4.3 knowledge_base.py — 知识骨架（459行）

**预建课程数据**（硬编码 Python 字典）：

| 课程 | ID | 章节数 | 内容 |
|------|----|--------|------|
| 📐 高等数学 | calculus | 6章 | 极限与连续、一元微分学、积分学、多元微分学、级数、微分方程 |
| 🔢 线性代数 | linalg | 6章 | 行列式、矩阵、向量、线性方程组、特征值、二次型 |
| ⚡ 大学物理 | physics | 5部分 | 力学、热学、静电学、磁场与电磁感应、波动光学 |

**每章数据结构**：
```python
{
    "title": "第X章 ...",
    "core": [...],       # 核心概念（3-4条）
    "formulas": [...],   # 关键公式（3-5条）
    "methods": [...],    # 解题方法（2-4条）
    "pitfalls": [...],   # 常见错误/易错点（3条）
}
```

**渲染函数**：
- `render_chapter(chapter)` → Markdown 格式渲染单章
- `render_course(course)` → Markdown 格式渲染整课程

### 4.4 .streamlit/config.toml — 主题配置

```toml
[theme]
primaryColor = "#667eea"        # 蓝紫渐变起点
backgroundColor = "#FAFBFF"     # 极浅蓝白
secondaryBackgroundColor = "#FFFFFF"  # 纯白（侧边栏/组件背景）
textColor = "#1a1a2e"           # 深色文字
font = "sans serif"
```

---

## 五、UI 设计系统

### 5.1 设计风格
**渐变科技风**（方案A），主色调：
- 渐变色：`#667eea` → `#764ba2`（蓝紫渐变）
- 主背景：`#FAFBFF`（极浅蓝白）
- 深色文字：`#1a1a2e`
- 辅助灰：`#8892b0`

### 5.2 侧边栏设计
- 深色背景：`linear-gradient(180deg, #1a1a2e, #16213e)`
- Logo 区：🧪 emoji + 白色粗体标题"一切皆蒸馏" + 浅蓝副标题
- 导航项：浅色文字 `#e8ecf4`，hover 时蓝紫背景，选中项加深背景
- 底部：版本号 `v0.2 · 一切皆蒸馏`

### 5.3 全局 CSS 组件
- **按钮**：蓝紫渐变背景 + 圆角10px + 阴影 + hover上浮
- **卡片**（.card）：白色背景 + 圆角14px + 阴影 + hover上浮+蓝紫边框
- **蒸馏方式卡片**（.method-card）：类似卡片但居中 + min-height:120px
- **步骤引导**（.step-card + .step-num）：白色卡片 + 蓝紫渐变圆形编号
- **标签**（.tag / .tag-primary）：圆角药丸 + 蓝紫半透明背景
- **结果卡片**（.result-card）：大内边距 + 轻阴影
- **输入框**：圆角10px + focus时蓝紫边框 + 光晕

---

## 六、已完成的工作

### ✅ 阶段一：UI 全面美化（已完成并部署）

1. **全局主题配置**：创建 `.streamlit/config.toml`，设定蓝紫渐变主题色
2. **全局 CSS 注入**：渐变按钮、卡片阴影/hover、侧边栏深色背景、标签样式、输入框圆角
3. **侧边栏重新设计**：Logo区（emoji+白色粗体标题+副标题）+ 导航高亮 + 版本号
4. **首页 Landing Page 化**：
   - Hero 区（大 emoji + 渐变标题 + 副标题）
   - CTA 按钮（🚀 立即开始蒸馏）
   - 三步引导卡片（上传→选择→获得）
   - 六种蒸馏方式卡片展示（2行×3列）
   - 底部引导按钮（知识骨架 / 模型设置）
5. **蒸馏结果页优化**：渐变成功横幅 + 标签式元信息 + 结果卡片包裹 + expander编辑
6. **模型设置页优化**：模型类型卡片展示 + API预设选择 + SMTP配置
7. **知识骨架页优化**：课程卡片 + 章节导航 + 结果卡片渲染
8. **反馈页优化**：表单 + 邮件发送逻辑

### ✅ 核心功能（v0.1 已有，v0.2 修复增强）

1. **6种蒸馏方式**：提纲式、Q&A式、费曼式、公式卡片、思维导图、Cornell笔记
2. **双模式运行**：模板模式（零成本）+ LLM模式（高质量）
3. **文件上传**：支持 PDF / TXT / MD
4. **知识骨架浏览**：高数6章 + 线代6章 + 大物5部分
5. **蒸馏结果编辑**：expander 内直接编辑 Markdown
6. **导出下载**：下载为 .md 文件
7. **产品反馈**：表单 + 本地保存 + SMTP 邮件
8. **多 API 支持**：阿里云/DeepSeek/SiliconFlow/自定义

### ✅ Bug 修复历史

| Commit | 修复内容 |
|--------|----------|
| `ecab0c7` | 初始版本 v0.1 |
| `4cf7647` | 修复中文引号导致的 SyntaxError |
| `70995ec` | 初始化 session_state.page 防止首次加载 ValueError |
| `32047ee` | 替换损坏的双 radio 按钮为卡片式选择器 |
| `50f2f72` | 修复 page index 不匹配（emoji列表 vs 非emoji列表导致 ValueError） |
| `2818df9` | 持久化 API preset 和 model 选择 |
| `2230e83` | 持久化 model_type 选择（math/text） |
| `e13a366` | 缓存上传文件字节 + 防止骨架 tab 覆盖上传 source_type |
| `4449fa1` | 分离 LLM 错误与模板输出，优雅降级 |
| `b824b2b` | UI 全面升级：渐变科技风设计 |
| `1808030` | 修复侧边栏文字在深色背景下不可见 |
| `0380d15` | 强制侧边栏 radio 项 opacity: 1 |
| `11b4f7f` | 更激进的侧边栏文字颜色覆盖（所有嵌套元素） |

---

## 七、尚未完成的工作

### 🔴 阶段四：名师1:1复刻（核心待开发功能）

这是用户最期待的新功能，**完整需求链路**如下：

#### 7.1 创建教师分身
- 用户上传老师的文字资料（课件、教案、笔记等）
- **未来**：上传老师视频（提取音频→转文字→分析教学风格）
- AI 分析后生成"教师风格卡"（记录教学风格、常用表达、重点强调方式等）

#### 7.2 蒸馏时选择教师分身
- 在"开始蒸馏"页面的蒸馏方式中，增加一个"名师复刻"选项
- 或者作为独立的入口/页面

#### 7.3 蒸馏后分支选择
蒸馏完成后，用户可以选择两种输出模式：
- **生成讲义模式**：用老师的风格重新生成笔记/讲义 → 可导出
- **对话模式**：进入聊天界面 + 老师头像 → 用老师的风格回答学科问题

#### 7.4 头像框
- 上传老师的照片作为头像
- 在对话模式和讲义中展示

#### 7.5 自然语言反馈自动修改
- 蒸馏结果出来后，学生可以用自然语言说"这里讲得太难了"、"加个例子"等
- AI 自动根据反馈修改蒸馏内容

#### 7.6 当前状态
**完全未开始开发**。仅停留在需求讨论阶段。

### 🟡 侧边栏文字可见性问题（可能未完全解决）

**问题描述**：Streamlit Cloud 部署后，侧边栏深色背景下导航未选中项文字太暗，看不清。

**已尝试的修复**：
1. 标题改为白色+粗体，副标题调亮 `#c8d0e8`
2. 导航标签颜色 `#e8ecf4` + `opacity: 1 !important`
3. 强制 radio 行容器 `opacity: 1`
4. 对所有嵌套元素（label, span, p, div）强制 `color: #e8ecf4 !important`

**可能仍未解决**：因为 Streamlit 内部 DOM 结构可能比 CSS 选择器更深。如果问题持续，备选方案是：
> **放弃 st.radio 做导航，改用自定义 HTML 按钮**（通过 `st.markdown` + `unsafe_allow_html` + `st.experimental_rerun` 配合），彻底绕过 Streamlit 的 radio 样式限制。

### 🟡 其他可能需要的改进

1. **视频处理**（名师复刻的前置需求）：视频→音频→文字→风格分析
2. **用户系统**：当前无登录/注册，所有数据在浏览器 session 中
3. **数据持久化**：蒸馏结果、教师风格卡等需要存储（当前仅 session_state，刷新即丢失）
4. **更多知识骨架**：目前只有高数/线代/大物，可扩展更多科目

---

## 八、部署信息

### 8.1 GitHub 仓库
- 仓库地址：需从 Streamlit Cloud 配置中查看（GitHub 用户名/仓库名）
- 分支：`main`
- 最新 commit：`11b4f7f`

### 8.2 Streamlit Cloud
- 部署 URL：`https://distill-all-aaow9u6ke4a63md7thnhdb.streamlit.app`
- **重要**：Streamlit Cloud 的 Reboot 操作**不会**拉取新代码，只重启容器
- 强制重新部署：需要**删除 app 后重新创建**（delete-and-recreate）
- Webhook 可能因 GitHub App 授权过期而失效

### 8.3 本地运行
```bash
# 方式一：直接运行
streamlit run app.py

# 方式二：使用批处理
run.bat

# 指定端口
streamlit run app.py --server.port 8501
```

---

## 九、关键技术决策与陷阱

### 9.1 Streamlit 陷阱（必须注意！）

1. **st.selectbox / st.radio 不记忆选择**：
   - 必须用 `index=` 参数 + `session_state` 手动管理选中状态
   - 否则每次 rerun 都会回到第一个选项

2. **st.file_uploader 文件只能读一次**：
   - 文件对象的 `read()` 指针用完即空
   - 必须在上传时立即 `read()` 并存入 `session_state["uploaded_file_bytes"]`

3. **st.tabs 的所有 tab 内容同时执行**：
   - 不是只执行当前激活的 tab！
   - 必须用不同的 session_state key 隔离各 tab 的数据

4. **Emoji 在 SearchReplace 工具中容易匹配失败**：
   - 修改 app.py 中含 emoji 的代码时，用 Python 脚本 + Unicode 转义更可靠
   - 例如 `🧪` 用 `\U0001f9ea` 替代

5. **st.popover 需要 Streamlit >= 1.33**：
   - requirements.txt 写的是 >=1.30.0
   - 已改用 st.expander 替代

### 9.2 架构决策

| 决策 | 原因 |
|------|------|
| 单文件 app.py（而非多页面） | Streamlit 单页应用，用 if/elif 控制页面切换更灵活 |
| 知识骨架硬编码在 Python 中 | 数据量不大，无需数据库，方便维护 |
| CSS 通过 st.markdown 注入 | Streamlit 不支持外部 CSS 文件，只能内联注入 |
| 双模式（模板+LLM） | 无 API Key 也能用（低质量），有 API Key 体验更好 |
| Session State 管理状态 | Streamlit 原生机制，无需额外数据库 |

---

## 十、用户原始需求全记录

用户最初提出的完整产品规划（分阶段）：

- **阶段一 ✅**：UI 全面美化 → 参考成熟产品，渐变科技风（#667eea → #764ba2）
- **阶段二**：（未明确讨论，可能是功能增强类）
- **阶段三**：（未明确讨论）
- **阶段四 🔴**：名师1:1复刻 → 上传老师教材+视频 → AI生成教师风格卡 → 蒸馏后分支（讲义/对话）→ 头像框 → 自然语言反馈自动修改

**用户明确要求**：
> "加一个功能或者加一些东西之前你问一下我不要擅自乱改"

**务必遵守**：在做任何功能新增或修改之前，先向用户确认方案，不要擅自实施。

---

## 十一、给下一个 AI 助手的操作建议

1. **读代码顺序**：先读 `engine.py`（理解蒸馏核心）→ 再读 `knowledge_base.py`（理解数据）→ 最后读 `app.py`（理解 UI 和交互）
2. **修改 app.py 时注意 emoji**：用 Python 脚本做替换比 SearchReplace 工具更可靠
3. **测试**：修改后本地运行 `streamlit run app.py` 验证
4. **推送后提醒用户**：Streamlit Cloud 可能需要删除重建 app 才能生效
5. **阶段四开发时**：建议分步实施，每完成一个子功能就让用户确认
6. **MVP 策略**：名师复刻功能建议先只做文字资料（不做视频），先跑通链路再迭代

---

*文档生成时间：2026年8月28日*
*项目版本：v0.2（UI改造完成，名师复刻待开发）*
