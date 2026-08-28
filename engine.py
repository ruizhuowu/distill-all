"""
蒸馏引擎 - 一切皆蒸馏
支持6种蒸馏方式：提纲式、Q&A式、费曼式、公式卡片、思维导图、Cornell笔记
支持模板模式（无需API）和LLM增强模式（需配置API）
"""

import re
from pathlib import Path

# ============================================================
# PDF / 文本提取
# ============================================================

def extract_pdf_text(file_bytes: bytes) -> str:
    """从PDF字节流中提取全部文本"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return "[错误] 请先安装 PyMuPDF: pip install PyMuPDF"
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append(f"--- 第{i+1}页 ---\n{text}")
    doc.close()
    return "\n\n".join(pages)


def extract_text(file_bytes: bytes, filename: str) -> str:
    """根据文件类型提取文本"""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_pdf_text(file_bytes)
    elif ext in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="replace")
    else:
        return file_bytes.decode("utf-8", errors="replace")


# ============================================================
# 文本预处理
# ============================================================

def split_into_sections(text: str) -> list:
    """将长文本按段落/章节切分"""
    # 尝试按标题行切分
    lines = text.split("\n")
    sections = []
    current = []
    for line in lines:
        stripped = line.strip()
        # 检测可能的标题行
        if (re.match(r'^(第[一二三四五六七八九十\d]+[章节讲篇])', stripped) or
            re.match(r'^\d+[\.\s]', stripped) or
            re.match(r'^[一二三四五六七八九十]+[\.\、\s]', stripped)):
            if current:
                sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    # 如果没切出来，按空行切
    if len(sections) <= 1:
        sections = [s.strip() for s in re.split(r'\n\s*\n', text) if s.strip()]
    return sections if sections else [text]


def extract_key_sentences(text: str, max_count: int = 15) -> list:
    """提取关键句子（含关键词的优先）"""
    keywords = [
        "定义", "定理", "公式", "性质", "条件", "结论", "证明",
        "因此", "所以", "综上", "可得", "可知", "必须", "注意",
        "重要", "关键", "核心", "基本", "主要", "首先", "其次",
        "导数", "积分", "极限", "连续", "矩阵", "行列式", "向量",
        "力", "速度", "加速度", "能量", "电场", "磁场", "定理",
        "方程", "函数", "变量", "系数", "收敛", "发散"
    ]
    sentences = re.split(r'[。！？\.\!\?]\s*|\n+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    # 按关键词命中数排序
    scored = []
    for s in sentences:
        score = sum(1 for kw in keywords if kw in s)
        scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:max_count]]


# ============================================================
# 6种蒸馏方式（模板模式）
# ============================================================

METHODS = {
    "outline":    {"name": "提纲式",   "icon": "📋", "desc": "层级结构，一目了然"},
    "qa":         {"name": "Q&A式",    "icon": "❓", "desc": "问答对照，自测利器"},
    "feynman":    {"name": "费曼式",   "icon": "🧠", "desc": "大白话讲透本质"},
    "formula":    {"name": "公式卡片", "icon": "📐", "desc": "核心公式速查速记"},
    "mindmap":    {"name": "思维导图", "icon": "🗺️", "desc": "可视化知识网络"},
    "cornell":    {"name": "Cornell笔记", "icon": "📝", "desc": "经典笔记法，复习高效"},
}


def distill(source_text: str, method: str, title: str = "未命名材料") -> str:
    """主入口：根据method对source_text进行蒸馏"""
    sections = split_into_sections(source_text)
    key_points = extract_key_sentences(source_text)

    dispatch = {
        "outline":  _distill_outline,
        "qa":       _distill_qa,
        "feynman":  _distill_feynman,
        "formula":  _distill_formula,
        "mindmap":  _distill_mindmap,
        "cornell":  _distill_cornell,
    }
    func = dispatch.get(method, _distill_outline)
    return func(source_text, sections, key_points, title)


# ---------- 提纲式 ----------
def _distill_outline(text, sections, key_points, title):
    lines = [f"# {title} — 提纲\n"]
    for i, section in enumerate(sections, 1):
        sec_lines = section.strip().split("\n")
        heading = sec_lines[0][:80]
        lines.append(f"## {i}. {heading}\n")
        body = "\n".join(sec_lines[1:]).strip()
        if body:
            # 提取要点
            sub_points = extract_key_sentences(body, 5)
            for p in sub_points:
                lines.append(f"- {p[:120]}")
            lines.append("")
        else:
            for p in key_points[i-1:i+2]:
                lines.append(f"- {p[:120]}")
            lines.append("")
    lines.append("---")
    lines.append("> 💡 **复习建议**：先遮住细节，看标题回忆要点，再展开核对。")
    return "\n".join(lines)


# ---------- Q&A式 ----------
def _distill_qa(text, sections, key_points, title):
    lines = [f"# {title} — Q&A 自测卡\n"]
    lines.append("> 使用方法：先看问题尝试回答，再展开看参考答案。\n")
    for i, point in enumerate(key_points, 1):
        # 根据内容生成问题
        question = _generate_question(point, i)
        lines.append(f"### Q{i}: {question}\n")
        lines.append(f"<details>")
        lines.append(f"<summary>查看答案</summary>\n")
        lines.append(f"{point}\n")
        lines.append(f"</details>\n")
    lines.append("---")
    lines.append("> 💡 **提效技巧**：每天随机抽5题自测，连续3天答对的可以标记为已掌握。")
    return "\n".join(lines)


def _generate_question(point: str, idx: int) -> str:
    """从知识点生成问题（模板版，LLM模式下会更好）"""
    if "定义" in point:
        return "请叙述以下定义的核心含义"
    elif "定理" in point or "公式" in point:
        return "请写出相关定理/公式并说明适用条件"
    elif "注意" in point or "常见" in point:
        return "以下易错点你注意到了吗"
    elif "证明" in point:
        return "请简述证明思路"
    elif "方法" in point or "步骤" in point:
        return "请描述该方法/步骤的核心要点"
    elif any(kw in point for kw in ["导数", "积分", "极限", "矩阵", "方程", "力", "电场"]):
        return f"关于以下知识点，请用自己的话解释"
    else:
        return f"请解释以下知识要点"


# ---------- 费曼式 ----------
def _distill_feynman(text, sections, key_points, title):
    lines = [f"# {title} — 费曼笔记\n"]
    lines.append("> 用大白话把每个概念讲清楚——如果你不能简单地解释它，说明你还没真正理解它。\n")
    for i, point in enumerate(key_points, 1):
        lines.append(f"## 概念 {i}\n")
        lines.append(f"**原文要点：**\n")
        lines.append(f"> {point}\n")
        lines.append(f"**通俗理解：**\n")
        lines.append(f"<!-- 用你自己的话在这里写通俗解释 -->\n")
        lines.append(f"**类比：**\n")
        lines.append(f"<!-- 找一个生活中的类比来帮助理解 -->\n")
        lines.append(f"**一句话总结：**\n")
        lines.append(f"<!-- 用一句话概括这个概念的核心 -->\n")
        lines.append("---\n")
    lines.append("> 💡 **费曼学习法**：试着把这个概念讲给一个完全不懂的人听，卡壳的地方就是你还没掌握的地方。")
    return "\n".join(lines)


# ---------- 公式卡片 ----------
def _distill_formula(text, sections, key_points, title):
    lines = [f"# {title} — 公式速查卡\n"]
    # 提取含数学符号的行
    formula_patterns = [
        r'.*[=≠≤≥<>].*',
        r'.*[∫∑∏∂∇].*',
        r'.*[αβγδεθλμσφω].*',
        r'.*(公式|定理|性质|法则|定义).*',
    ]
    formulas = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line) > 5 and any(re.match(p, line) for p in formula_patterns):
            formulas.append(line)
    # 去重
    seen = set()
    unique_formulas = []
    for f in formulas:
        if f not in seen:
            seen.add(f)
            unique_formulas.append(f)
    formulas = unique_formulas[:20]

    if not formulas:
        formulas = key_points[:10]

    for i, formula in enumerate(formulas, 1):
        lines.append(f"### 卡片 {i}\n")
        lines.append(f"**内容：** {formula}\n")
        lines.append(f"**适用场景：** <!-- 填写 -->\n")
        lines.append(f"**易错点：** <!-- 填写 -->\n")
        lines.append("---\n")

    lines.append("> 💡 **记忆技巧**：把公式卡片打乱顺序，每天随机抽3张默写，连续3天全对就移除。")
    return "\n".join(lines)


# ---------- 思维导图 ----------
def _distill_mindmap(text, sections, key_points, title):
    lines = [f"# {title} — 思维导图\n"]
    lines.append("```mermaid")
    lines.append("mindmap")
    lines.append(f"  root(({title}))")
    for i, section in enumerate(sections[:8], 1):
        sec_lines = section.strip().split("\n")
        heading = sec_lines[0][:40].strip("# ").strip()
        if not heading:
            heading = f"主题{i}"
        lines.append(f"    {heading}")
        sub_points = extract_key_sentences("\n".join(sec_lines[1:]), 3)
        for p in sub_points:
            short = p[:30].strip()
            lines.append(f"      {short}")
    lines.append("```\n")
    lines.append("## 知识要点\n")
    for i, point in enumerate(key_points, 1):
        lines.append(f"{i}. {point[:120]}")
    lines.append("\n---")
    lines.append("> 💡 **使用建议**：看着中心主题，尝试默画出所有分支，画不出来的就是薄弱点。")
    return "\n".join(lines)


# ---------- Cornell笔记 ----------
def _distill_cornell(text, sections, key_points, title):
    lines = [f"# {title} — Cornell 笔记\n"]
    lines.append("| 线索 ( Cue ) | 笔记 ( Notes ) |")
    lines.append("|:---|:---|")

    for i, point in enumerate(key_points, 1):
        # 提取关键词作为线索
        cue = _extract_cue(point)
        note = point[:100]
        lines.append(f"| {cue} | {note} |")

    lines.append(f"\n## 总结\n")
    lines.append("<!-- 用2-3句话概括本次学习的核心内容 -->\n")
    lines.append("<!-- 写下你最需要复习的3个知识点 -->\n")
    lines.append("---")
    lines.append("> 💡 **Cornell复习法**：遮住右侧笔记，看左侧线索回忆内容。全部回忆后写总结。")
    return "\n".join(lines)


def _extract_cue(point: str) -> str:
    """从知识点提取线索词"""
    for kw in ["定义", "定理", "公式", "性质", "条件", "方法", "步骤", "法则"]:
        if kw in point:
            return f"什么是{kw}？"
    for kw in ["导数", "积分", "极限", "矩阵", "向量", "力", "电场", "磁场"]:
        if kw in point:
            return f"关于{kw}"
    return "核心要点"


# ============================================================
# LLM增强模式（用户配置API后启用）
# ============================================================

def distill_with_llm(source_text: str, method: str, title: str,
                     api_key: str, base_url: str, model: str) -> str:
    """调用LLM进行高质量蒸馏"""
    try:
        from openai import OpenAI
    except ImportError:
        return "[错误] 请先安装 openai: pip install openai"

    client = OpenAI(api_key=api_key, base_url=base_url)

    method_info = METHODS.get(method, METHODS["outline"])
    prompt = _build_llm_prompt(source_text, method, method_info["name"], title)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的知识蒸馏助手，擅长将复杂的学习材料转化为结构化的备考笔记。输出使用Markdown格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[LLM调用失败] {str(e)}\n\n已切换为模板模式输出：\n\n" + distill(source_text, method, title)


def _build_llm_prompt(text: str, method: str, method_name: str, title: str) -> str:
    """构建LLM蒸馏Prompt"""
    base = f"请将以下学习材料「{title}」用{method_name}进行知识蒸馏。\n\n要求：\n"

    prompts = {
        "outline": base + """
1. 提取所有核心知识点，按层级结构组织
2. 每个知识点用一句话概括
3. 标注重要程度（★★★必考 /★★常考 /★了解）
4. 末尾给出复习优先级建议
输出为Markdown格式。

材料内容：
""",
        "qa": base + """
1. 针对每个核心知识点生成1-2个高质量问题
2. 问题要有区分度，不只是简单记忆，要有理解题和应用题
3. 答案要准确、简洁
4. 用 <details> 标签折叠答案
输出为Markdown格式。

材料内容：
""",
        "feynman": base + """
1. 用大白话解释每个核心概念，假设读者是零基础
2. 每个概念配一个生活中的类比
3. 指出一句话总结
4. 标注容易混淆的地方
输出为Markdown格式。

材料内容：
""",
        "formula": base + """
1. 提取所有重要公式/定理/性质
2. 每个公式说明：内容、适用条件、常见变形、易错点
3. 按使用频率排序
输出为Markdown格式。

材料内容：
""",
        "mindmap": base + """
1. 用Mermaid mindmap语法绘制思维导图
2. 中心主题→主要章节→核心知识点→细节
3. 层级不超过4层
4. 节点文字简洁（不超过15字）
输出为Markdown格式（含mermaid代码块）。

材料内容：
""",
        "cornell": base + """
1. 左侧线索栏：提取关键词/核心问题
2. 右侧笔记栏：对应的详细解释
3. 底部总结栏：2-3句话概括全部核心内容
用Markdown表格格式呈现。

材料内容：
""",
    }
    return prompts.get(method, prompts["outline"]) + text[:8000]
