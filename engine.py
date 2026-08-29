"""
蒸馏引擎 - 一切皆蒸馏 v0.3
=======================
架构升级：从"6种形式的筛子"升级为"1条蒸馏管线 + 多种结晶呈现"

蒸馏管线（三段式）：
  Stage 1 清洗   -> clean_text()          去页码/页眉页脚/重复空行
  Stage 2 建骨架 -> build_skeleton()      多路专项提取器（概念/公式/方法/易错点 + 考点强度）
  Stage 3 结晶   -> distill_from_skeleton() 骨架按6种方式呈现

设计启发：
  - 仓颉 Skill（kangarooking/cangjie-skill）：多路并行提取器 + 质量门 + 可执行维度
  - Mr.-Ranedeer：结构化的教学风格 prompt 设计
  - 备考场景迁移：易错点提取器（反例）是备考最值钱的信息

双模式：
  - 模板模式（无需 API）：规则提取骨架 + 规则结晶
  - LLM 模式（需 API）：两阶段 prompt（先建骨架再结晶）+ 数学材料 LaTeX + 低温度
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
    else:
        return file_bytes.decode("utf-8", errors="replace")


# ============================================================
# Stage 1 文本清洗
# ============================================================

def clean_text(text: str) -> str:
    """清洗文本：去纯页码行、去页眉页脚特征行、压缩重复空行"""
    lines = [ln.strip() for ln in text.split("\n")]
    # 统计重复行（页眉页脚通常全篇重复出现）
    line_counter = {}
    for s in lines:
        line_counter[s] = line_counter.get(s, 0) + 1

    cleaned = []
    for s in lines:
        if not s:
            continue
        # 纯数字 / 页码 / 分隔线
        if re.fullmatch(r'\d{1,4}', s) or re.fullmatch(r'[-—－_·•]{3,}', s):
            continue
        # 页眉页脚特征：全篇重复 >=3 次、短行、且不像完整句子
        if line_counter.get(s, 0) >= 3 and len(s) < 30 \
                and not re.search(r'[\u4e00-\u9fa5].*[。！？!?]', s):
            continue
        cleaned.append(s)

    # 合并连续空行（按空行分段的语义保留）
    result = []
    prev_blank = False
    for s in cleaned:
        if not s:
            if not prev_blank:
                result.append("")
            prev_blank = True
        else:
            result.append(s)
            prev_blank = False
    return "\n".join(result).strip()


def _strip_intro(sentence: str) -> str:
    """剥离句首引语（'XX认为/指出/强调...'），避免被当作术语名"""
    m = re.match(r'^[^，。；]{2,10}?(?:认为|指出|强调|主张|表明|说明|揭示|总结|提出)[，,：:]', sentence)
    if m:
        return sentence[m.end():].strip()
    return sentence


def _split_sentences(text: str, min_len: int = 8) -> list:
    """按句号/换行切句（分号保留，用于枚举句提取），剥离引语前缀，过滤过短片段"""
    parts = re.split(r'[。！？!?]\s*|\n+', text)
    out = []
    for p in parts:
        p = _strip_intro(p.strip())
        if len(p) >= min_len:
            out.append(p)
    return out


def _truncate(text: str, n: int) -> str:
    """压缩空白并截断"""
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n - 1] + "…"


# ============================================================
# Stage 2 多路专项提取器
# ============================================================

# --- 概念提取器 ---
CONCEPT_KWS = [
    "定义", "概念", "含义", "是指", "称为", "叫做", "本质", "实质",
    "特征", "特点", "属性", "具有", "规律", "决定", "是",
    "表现", "原因", "内容", "意义", "作用", "关系", "地位", "前提",
    "包括", "分为", "区别", "联系", "要求", "条件",
]

# --- 公式提取器 ---
# 强公式：数学符号/希腊字母/定理定律等，只要命中即收
STRONG_FORMULA_PATTERNS = [
    r'[=＝≠≤≥<>±×÷∫∑∏∂∇∞∈√≈]',          # 数学符号
    r'[αβγδεθλμνπρστφχψω]',              # 希腊字母
    r'(定理|定律|公式|法则|等于)',           # 领域关键词
]
# 弱公式：仅"规律/原理"字样，需出现 >=2 次才收，避免概念句误入
WEAK_FORMULA_KWS = ["规律", "原理"]

# --- 方法提取器 ---
METHOD_KWS = [
    "步骤", "方法", "过程", "首先", "其次", "然后", "最后", "做法",
    "途径", "方式", "思路", "流程", "要坚持", "必须", "应当", "要求",
    "通过", "采取",
]

# --- 易错点提取器 ---
PITFALL_KWS = [
    "易错", "注意", "误区", "切勿", "切忌", "容易混淆", "常见错误",
    "不要", "不能", "避免", "错误", "切记", "须注意", "严格",
    "防止", "反对", "警惕", "否则", "恰恰相反", "相混", "误把", "误认",
]

# --- 考点强度（质量门） ---
IMPORTANCE_STRONG = ["必考", "核心", "根本", "重点", "关键", "决定", "最重要", "唯一"]
IMPORTANCE_MED = ["基本", "主要", "重要", "常考", "特征", "规律", "实质", "本质", "基础"]


def assign_importance(text: str) -> int:
    """考点强度评分：1=★了解 / 2=★★常考 / 3=★★★必考"""
    s = sum(1 for k in IMPORTANCE_STRONG if k in text)
    m = sum(1 for k in IMPORTANCE_MED if k in text)
    score = 1
    if s >= 1:
        score += 2
    if m >= 2:
        score += 1
    return min(score, 3)


_TERM_PATTERNS = [
    r'^([^，。；:：、\s]{2,16}?)(?:是指|是|指|称为|叫做|等于|定义为)',
    r'^([^，。；:：、\s]{2,16}?)(?:具有|包括|包含|分为|由|源于)',
    r'^([^，。；:：、\s]{2,16}?)(?:的)(?:基本|主要|核心|重要|本质|根本)',
]


def _extract_term(sentence: str) -> str:
    """从句子中提取"概念名/术语名"，失败时回退到首句片段"""
    for pat in _TERM_PATTERNS:
        m = re.match(pat, sentence)
        if m:
            term = m.group(1)
            if len(term) >= 2:
                return term
    # 回退：第一个标点前片段，截断到 10 字
    head = re.split(r'[，,。；;]', sentence)[0].strip()
    return head[:10]


def _extract_method_term(sentence: str) -> str:
    """方法句的术语提取：优先取"坚持/通过/采取"后的对象短语"""
    m = re.match(r'^[^，。；:：]{0,4}?(?:坚持|通过|采取|运用|使用|按照)([^，。；:：]{2,14})', sentence)
    if m:
        return m.group(1).strip()
    return _extract_term(sentence)


def extract_concepts(text: str, heading: str = "") -> list:
    """概念提取器：抓定义/概念/特征句，提取术语名 + 考点强度；支持枚举型句子回退"""
    results, seen = [], set()
    for sent in _split_sentences(text):
        matched = any(kw in sent for kw in CONCEPT_KWS)
        if matched:
            term = _extract_term(sent)
            if len(term) >= 2 and term not in seen:
                seen.add(term)
                results.append({"term": term, "text": sent, "importance": assign_importance(sent)})
            continue
        # 枚举型句子回退："A；B；C；D。" 拆分为独立要点（如"生产资料公有制；按劳分配；…"）
        if "；" in sent:
            items = [x.strip() for x in sent.split("；") if 2 <= len(x.strip()) <= 20]
            if len(items) >= 2:
                for it in items[:6]:
                    it = it.lstrip("·-—0123456789.、 ")
                    if len(it) >= 2 and it not in seen:
                        seen.add(it)
                        results.append({"term": it, "text": it, "importance": 2})
                continue
    return results[:10]


def extract_formulas(text: str) -> list:
    """公式提取器：强公式符号直接收；弱"规律/原理"需重复出现才收"""
    results, seen = [], set()
    for sent in _split_sentences(text):
        if len(sent) < 6:
            continue
        strong = any(re.search(p, sent) for p in STRONG_FORMULA_PATTERNS)
        weak = sum(sent.count(kw) for kw in WEAK_FORMULA_KWS)
        if not (strong or weak >= 2):
            continue
        term = _extract_term(sent)
        if len(term) < 2 or term in seen:
            continue
        seen.add(term)
        results.append({"term": term, "text": sent, "importance": assign_importance(sent)})
    return results[:10]


def extract_methods(text: str) -> list:
    """方法提取器：抓解题步骤/方法论句"""
    results, seen = [], set()
    for sent in _split_sentences(text):
        if not any(kw in sent for kw in METHOD_KWS):
            continue
        term = _extract_method_term(sent)
        if len(term) < 2 or term in seen:
            continue
        seen.add(term)
        results.append({"term": term, "text": sent, "importance": assign_importance(sent)})
    return results[:6]


def extract_pitfalls(text: str) -> list:
    """易错点提取器（备考最值钱）：抓注意/错误/误区/不能句"""
    results, seen = [], set()
    for sent in _split_sentences(text):
        if not any(kw in sent for kw in PITFALL_KWS):
            continue
        term = _extract_term(sent)
        if len(term) < 2 or term in seen:
            continue
        seen.add(term)
        results.append({"term": term, "text": sent, "importance": 2})
    return results[:6]


def build_skeleton(source_text: str, title: str = "未命名材料") -> dict:
    """Stage 2：清洗 + 切分 + 多路提取，产出结构化知识骨架"""
    text = clean_text(source_text)
    raw_sections = split_into_sections(text)
    skeleton = {"title": title, "sections": []}

    pending_headings = []  # 纯标题节（如"第一章…"无正文）合并到下一节
    for sec in raw_sections:
        sec_lines = [l for l in sec.strip().split("\n") if l.strip()]
        if not sec_lines:
            continue
        heading = sec_lines[0][:50]
        body = "\n".join(sec_lines[1:]).strip() if len(sec_lines) > 1 else ""

        if not body:
            pending_headings.append(heading)
            continue
        if pending_headings:
            heading = " | ".join(pending_headings + [heading])
            pending_headings = []

        skeleton["sections"].append({
            "heading": heading,
            "concepts": extract_concepts(body, heading),
            "formulas": extract_formulas(body),
            "methods": extract_methods(body),
            "pitfalls": extract_pitfalls(body),
        })

    # 末尾残留的纯标题节
    if pending_headings:
        skeleton["sections"].append({
            "heading": " | ".join(pending_headings),
            "concepts": [], "formulas": [], "methods": [], "pitfalls": [],
        })
    return skeleton


# ============================================================
# Stage 3 结晶（6 种方式基于骨架呈现）
# ============================================================

def _star(n: int) -> str:
    return "★" * n


def _crystallize_outline(skeleton: dict, title: str) -> str:
    lines = [f"# {title} — 提纲\n"]
    for i, sec in enumerate(skeleton["sections"], 1):
        if not (sec["concepts"] or sec["formulas"] or sec["methods"] or sec["pitfalls"]):
            continue
        lines.append(f"## {i}. {sec['heading']}\n")
        for c in sec["concepts"]:
            lines.append(f"- **{c['term']}**（{_star(c['importance'])}）：{_truncate(c['text'], 90)}")
        for f in sec["formulas"]:
            lines.append(f"- 📐 **{f['term']}**（{_star(f['importance'])}）：{_truncate(f['text'], 90)}")
        for m in sec["methods"]:
            lines.append(f"- 🛠️ **{m['term']}**（{_star(m['importance'])}）：{_truncate(m['text'], 90)}")
        for p in sec["pitfalls"]:
            lines.append(f"- ⚠️ **易错·{_truncate(p['term'], 12)}**：{_truncate(p['text'], 90)}")
        lines.append("")
    lines.append("---")
    lines.append("> 💡 **复习建议**：先遮住细节，看标题回忆要点，再展开核对。")
    return "\n".join(lines)


def _crystallize_qa(skeleton: dict, title: str) -> str:
    lines = [f"# {title} — Q&A 自测卡\n"]
    lines.append("> 使用方法：先看问题尝试回答，再展开看参考答案。\n")
    qid = 0
    for sec in skeleton["sections"]:
        items = []
        for c in sec["concepts"]:
            items.append(("概念", f"什么是「{c['term']}」？", c["text"]))
        for f in sec["formulas"]:
            items.append(("公式", f"写出/说明「{f['term']}」的内容与适用条件", f["text"]))
        for m in sec["methods"]:
            items.append(("方法", f"「{_truncate(m['term'], 16)}」的核心要点是什么？", m["text"]))
        for p in sec["pitfalls"]:
            items.append(("易错", f"关于「{_truncate(p['term'], 16)}」有哪些易错点？", p["text"]))
        for typ, q, a in items:
            qid += 1
            lines.append(f"### Q{qid}（{typ}）：{q}\n")
            lines.append("<details>")
            lines.append("<summary>查看答案</summary>\n")
            lines.append(f"{a}\n")
            lines.append("</details>\n")
    lines.append("---")
    lines.append("> 💡 **提效技巧**：每天随机抽5题自测，连续3天答对的可以标记为已掌握。")
    return "\n".join(lines)


def _crystallize_feynman(skeleton: dict, title: str) -> str:
    lines = [f"# {title} — 费曼笔记\n"]
    lines.append("> 用大白话把每个概念讲清楚——如果你不能简单地解释它，说明你还没真正理解它。\n")
    idx = 0
    for sec in skeleton["sections"]:
        for c in sec["concepts"]:
            idx += 1
            lines.append(f"## 概念 {idx}：{c['term']}\n")
            lines.append(f"**原文要点：**\n")
            lines.append(f"> {_truncate(c['text'], 120)}\n")
            # 通俗理解初稿（规则生成，不再留空）
            def_part = _strip_term_prefix(c["text"], c["term"])
            lines.append(f"**通俗理解（初稿）：**\n")
            lines.append(f"> 简单来说，**{c['term']}** 的核心意思是：{_truncate(def_part, 100)}\n")
            # 类比自测（引导式，非空模板）
            lines.append(f"**类比自测：**\n")
            lines.append(f"- [ ] 我能用生活中的例子解释「{c['term']}」吗？（答不上来 = 还没理解）\n")
            lines.append(f"**一句话总结：**\n")
            lines.append(f"> {_truncate(c['text'], 36)}\n")
            # 关联易错点
            related = [p for p in sec["pitfalls"] if c["term"] in p["text"] or p["term"] in c["text"]]
            if related:
                lines.append(f"**⚠️ 易错提示：**\n")
                for p in related:
                    lines.append(f"> {_truncate(p['text'], 90)}\n")
            lines.append("---\n")
    lines.append("> 💡 **费曼学习法**：试着把概念讲给完全不懂的人听，卡壳的地方就是还没掌握的地方。")
    return "\n".join(lines)


def _strip_term_prefix(text: str, term: str) -> str:
    """去掉定义句的'X是'前缀，得到定义核心"""
    t = text
    for kw in ["是指", "是", "指", "称为", "叫做"]:
        if t.startswith(term + kw):
            rest = t[len(term + kw):].strip()
            if rest:
                return rest
    return t


def _crystallize_formula(skeleton: dict, title: str) -> str:
    lines = [f"# {title} — 公式速查卡\n"]
    all_items = []
    for sec in skeleton["sections"]:
        for f in sec["formulas"]:
            all_items.append((sec["heading"], f, _pitfalls_for(sec, f["term"])))
    if not all_items:  # 无公式时用概念顶替
        for sec in skeleton["sections"]:
            for c in sec["concepts"]:
                all_items.append((sec["heading"], c, _pitfalls_for(sec, c["term"])))
    if not all_items:
        return lines[0] + "\n> 未检测到公式/定理内容。\n"

    all_items.sort(key=lambda x: -x[1]["importance"])
    lines.append(f"> 共 {len(all_items)} 张卡片，按考点强度排序，优先记忆 ★★★\n")
    for i, (sec_h, f, pfs) in enumerate(all_items[:20], 1):
        lines.append(f"### 卡片 {i}：{f['term']}\n")
        lines.append(f"**来源章节：** {sec_h}\n")
        lines.append(f"**内容：** {_truncate(f['text'], 140)}\n")
        lines.append(f"**考点等级：** {_star(f['importance'])}\n")
        if pfs:
            lines.append(f"**易错点：** {_truncate(pfs, 90)}\n")
        lines.append("**自测引导：** 先遮住内容默写，默不出的就是薄弱点。\n")
        lines.append("---\n")
    lines.append("> 💡 **记忆技巧**：打乱顺序每天随机抽3张默写，连续3天全对就移除。")
    return "\n".join(lines)


def _pitfalls_for(sec: dict, term: str) -> str:
    """查找与该术语相关的易错点（文本或术语关联）"""
    for p in sec["pitfalls"]:
        if term in p["text"] or p["term"] in term or term in p["term"]:
            return p["text"]
    return ""


def _crystallize_mindmap(skeleton: dict, title: str) -> str:
    lines = [f"# {title} — 思维导图\n"]
    lines.append("```mermaid")
    lines.append("mindmap")
    lines.append(f"  root(({_truncate(title, 14)}))")
    for sec in skeleton["sections"][:8]:
        if not (sec["concepts"] or sec["pitfalls"]):
            continue
        head = sec["heading"].strip("# ").strip()[:18]
        lines.append(f"    {head}")
        for c in sec["concepts"][:3]:
            lines.append(f"      {_truncate(c['term'], 14)}")
        for p in sec["pitfalls"][:2]:
            lines.append(f"      ⚠️ {_truncate(p['term'], 10)}")
    lines.append("```\n")
    lines.append("## 核心要点\n")
    for sec in skeleton["sections"]:
        for c in sec["concepts"][:2]:
            lines.append(f"- {_star(c['importance'])} **{c['term']}**：{_truncate(c['text'], 70)}")
        for p in sec["pitfalls"][:1]:
            lines.append(f"- ⚠️ **易错**：{_truncate(p['text'], 70)}")
    lines.append("\n---")
    lines.append("> 💡 **使用建议**：看着中心主题，尝试默画出所有分支，画不出来的就是薄弱点。")
    return "\n".join(lines)


def _crystallize_cornell(skeleton: dict, title: str) -> str:
    lines = [f"# {title} — Cornell 笔记\n"]
    lines.append("| 线索（Cue） | 笔记（Notes） | 掌握度 |")
    lines.append("|:---|:---|:---:|")
    for sec in skeleton["sections"]:
        for c in sec["concepts"]:
            lines.append(f"| 什么是「{c['term']}」？ | {_truncate(c['text'], 60)} | 🟡 |")
        for f in sec["formulas"][:1]:
            lines.append(f"| 📐{_truncate(f['term'], 12)} | {_truncate(f['text'], 60)} | 🟡 |")
        for p in sec["pitfalls"][:1]:
            lines.append(f"| ⚠️ {_truncate(p['term'], 10)}易错 | {_truncate(p['text'], 60)} | 🟡 |")
    lines.append(f"\n## 总结（自动初稿，可修改）\n")
    summary_parts = []
    for sec in skeleton["sections"]:
        if sec["concepts"]:
            summary_parts.append(_truncate(sec["concepts"][0]["text"], 60))
        if sec["pitfalls"]:
            summary_parts.append("注意：" + _truncate(sec["pitfalls"][0]["text"], 40))
    summary = "；".join(summary_parts[:4])[:220] if summary_parts else "（本节无内容）"
    lines.append(f"> {summary}\n")
    lines.append("---")
    lines.append("> 💡 **Cornell复习法**：遮住右侧笔记，看左侧线索回忆内容；复习后将掌握度改为 ✅/🔴。")
    return "\n".join(lines)


# ============================================================
# 蒸馏方式定义 & 主入口
# ============================================================

METHODS = {
    "outline":    {"name": "提纲式",     "icon": "📋", "desc": "层级结构，一目了然",     "phase": "整理记忆"},
    "qa":         {"name": "Q&A式",      "icon": "❓", "desc": "问答对照，自测利器",     "phase": "自测刷题"},
    "feynman":    {"name": "费曼式",     "icon": "🧠", "desc": "大白话讲透本质",         "phase": "理解难点"},
    "formula":    {"name": "公式卡片",   "icon": "📐", "desc": "核心公式速查速记",     "phase": "考前速查"},
    "mindmap":    {"name": "思维导图",   "icon": "🗺️", "desc": "可视化知识网络",       "phase": "理解难点"},
    "cornell":    {"name": "Cornell笔记", "icon": "📝", "desc": "经典笔记法，复习高效", "phase": "整理记忆"},
}

_CRYSTALLIZERS = {
    "outline": _crystallize_outline,
    "qa": _crystallize_qa,
    "feynman": _crystallize_feynman,
    "formula": _crystallize_formula,
    "mindmap": _crystallize_mindmap,
    "cornell": _crystallize_cornell,
}


def distill_from_skeleton(skeleton: dict, method: str, title: str = "未命名材料") -> str:
    """Stage 3：骨架按指定方式结晶"""
    func = _CRYSTALLIZERS.get(method, _crystallize_outline)
    return func(skeleton, title)


def distill(source_text: str, method: str, title: str = "未命名材料") -> str:
    """模板模式主入口：清洗 → 建骨架 → 结晶"""
    skeleton = build_skeleton(source_text, title)
    return distill_from_skeleton(skeleton, method, title)


# ============================================================
# 自定义要求（自然语言）——用户自主性的柔性入口
# ============================================================

_TYPE_ALIASES = {
    "公式": "formula", "定理": "formula", "计算": "formula", "推导": "formula",
    "概念": "concept", "定义": "concept", "名词": "concept", "术语": "concept",
    "方法": "method", "步骤": "method", "流程": "method", "解题": "method",
    "易错": "pitfall", "陷阱": "pitfall", "错误": "pitfall", "误区": "pitfall",
}

_TYPE_LABELS = {
    "concept": "概念", "formula": "公式", "method": "方法", "pitfall": "易错点",
}


def parse_custom_requirements(requirement: str) -> dict:
    """模板模式解析自然语言要求 → 骨架级过滤/加权配置。

    能识别的三类约束：
      1. 章节过滤：如「只看第一章和第三章」
      2. 类型过滤：如「去掉公式」「只要概念」
      3. 重点强调：如「重点讲物质观相关的内容」
    识别不到的约束靠 LLM 模式兜底（prompt 最高优先级）。
    """
    r = requirement
    cfg = {
        "section_filters": [],  # 章节关键词（"第X章"）
        "keep_types": [],       # 只保留的类型
        "drop_types": [],       # 排除的类型
        "boost_terms": [],      # 重点强调词
        "summary": [],          # 已识别要求的一句话说明
    }

    # 1) 章节过滤：第X章 / 第X讲 / 第X篇
    secs = re.findall(r'第[一二三四五六七八九十百\d]+[章节篇讲]', r)
    cfg["section_filters"] = list(dict.fromkeys(secs))
    if secs:
        cfg["summary"].append(f"只看{'、'.join(dict.fromkeys(secs))}")

    # 2) 类型过滤：排除（不要/去掉/不用/略过/跳过 + 类型词），可同时命中多个类型
    for pat in [r'(?:不要|去掉|不用|略过|跳过|删掉)[^，。；,;]{0,6}',
                r'[^，。；,;]{0,6}(?:不需要|不用管)[^，。；,;]{0,4}']:
        for m in re.finditer(pat, r):
            seg = m.group(0)
            for name, t in _TYPE_ALIASES.items():
                if name in seg and t not in cfg["drop_types"]:
                    cfg["drop_types"].append(t)
                    cfg["summary"].append(f"去掉{name}")
    # 类型过滤：保留（只要/只看/重点看 + 类型词），可同时命中多个类型
    for pat in [r'(?:只要|只看|重点看|主要看|重点抓)[^，。；,;]{0,8}']:
        for m in re.finditer(pat, r):
            seg = m.group(0)
            for name, t in _TYPE_ALIASES.items():
                if name in seg and t not in cfg["keep_types"]:
                    cfg["keep_types"].append(t)
                    cfg["summary"].append(f"只保留{name}")
    cfg["keep_types"] = list(dict.fromkeys(cfg["keep_types"]))
    cfg["drop_types"] = list(dict.fromkeys(cfg["drop_types"]))

    # 3) 重点强调：重点/详细/强调/多写 + 具体名词（允许到句尾，如"重点讲物质观"）
    m = re.search(r'(?:重点|详细|强调|多写|展开|着重)[^，。；,;]{0,6}?([^，。；,;]{2,12}?)(?:的(?:相关内容|内容|部分|定义|概念|问题|考点)|相关|$)', r)
    if m:
        # 清洗常见动词/助词前缀，只留名词核心（如"重点讲物质观"→"物质观"）
        word = re.sub(r'^(?:的|是|和|与|及|还|以及|讲|写|说|看|记|学|背|梳理|整理|复习|了解|掌握|理解|记忆|关注|围绕|强调|突出)[,，]?', '', m.group(1).strip())
        if 2 <= len(word) <= 12:
            cfg["boost_terms"].append(word)
            cfg["summary"].append(f"重点:{word}")

    # 兜底说明：完全没识别出任何约束
    if not (cfg["section_filters"] or cfg["keep_types"] or cfg["drop_types"] or cfg["boost_terms"]):
        cfg["summary"].append("未识别到明确约束（模板模式能力有限，已按提纲输出）")
    return cfg


def distill_custom(source_text: str, requirement: str, title: str = "未命名材料") -> str:
    """模板模式自定义蒸馏：建骨架 → 解析要求 → 过滤/加权 → 结晶（提纲形态）"""
    skeleton = build_skeleton(source_text, title)
    cfg = parse_custom_requirements(requirement)

    # 应用章节过滤
    if cfg["section_filters"]:
        kept = [sec for sec in skeleton["sections"]
                if any(f in sec["heading"] for f in cfg["section_filters"])]
        skeleton["sections"] = kept or skeleton["sections"]

    # 应用类型过滤（keep 优先于 drop）
    for sec in skeleton["sections"]:
        if cfg["keep_types"]:
            for t, key in [("formula", "formulas"), ("concept", "concepts"),
                           ("method", "methods"), ("pitfall", "pitfalls")]:
                if t not in cfg["keep_types"]:
                    sec[key] = []
        elif cfg["drop_types"]:
            for t, key in [("formula", "formulas"), ("concept", "concepts"),
                           ("method", "methods"), ("pitfall", "pitfalls")]:
                if t in cfg["drop_types"]:
                    sec[key] = []

    # 应用重点加权（命中词 ★+1，最多 ★★★）
    if cfg["boost_terms"]:
        for sec in skeleton["sections"]:
            for lst in (sec["concepts"], sec["formulas"], sec["methods"]):
                for item in lst:
                    if any(b in item["term"] or b in item["text"] for b in cfg["boost_terms"]):
                        item["importance"] = min(item["importance"] + 1, 3)

    body = distill_from_skeleton(skeleton, "outline", title)
    note = "已识别要求：" + "；".join(cfg["summary"]) + "。"
    return (f"> 🎯 **自定义要求**：{requirement}\n"
            f"> 📋 {note}\n"
            f"> 💡 想要更精确地理解你的要求，请在「模型设置」配置 API Key 后重试。\n\n"
            f"---\n\n{body}")


# ============================================================
# 文本预处理（保留，兼容 app.py 导入）
# ============================================================

def split_into_sections(text: str) -> list:
    """将长文本按段落/章节切分"""
    lines = text.split("\n")
    sections = []
    current = []
    for line in lines:
        stripped = line.strip()
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
    if len(sections) <= 1:
        sections = [s.strip() for s in re.split(r'\n\s*\n', text) if s.strip()]
    return sections if sections else [text]


def extract_key_sentences(text: str, max_count: int = 15) -> list:
    """提取关键句子（含关键词的优先）——旧版抽句逻辑，保留兼容"""
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
    scored = []
    for s in sentences:
        score = sum(1 for kw in keywords if kw in s)
        scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:max_count]]


# ============================================================
# LLM 增强模式（两阶段 prompt）
# ============================================================

def _looks_math(text: str) -> bool:
    """启发式判断材料是否偏数学/理科"""
    math_marks = 0
    if re.search(r'[=＝∫∑√≈≠≤≥]', text):
        math_marks += 1
    if re.search(r'[αβγδεθλμνπρστφχψω]', text):
        math_marks += 1
    if re.search(r'(方程|函数|定理|导数|积分|矩阵|向量|公式|计算|证明)', text):
        math_marks += 1
    return math_marks >= 2


def distill_with_llm(source_text: str, method: str, title: str,
                     api_key: str, base_url: str, model: str,
                     model_type: str = "text", requirement: str = "") -> str:
    """LLM 模式：两阶段思维（先建骨架再结晶）+ 数学 LaTeX + 低温度"""
    try:
        from openai import OpenAI
    except ImportError:
        return "[错误] 请先安装 openai: pip install openai"

    client = OpenAI(api_key=api_key, base_url=base_url)
    method_info = METHODS.get(method, METHODS["outline"])
    is_math = (model_type == "math") or _looks_math(source_text)
    prompt = _build_llm_prompt(source_text, method, method_info["name"], title, is_math, requirement)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=6000,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"LLM调用失败: {str(e)}")


_LLM_SYSTEM_PROMPT = """你是一个专业的知识蒸馏助手，擅长将复杂的学习材料转化为结构化的备考笔记。
你的工作方式遵循"两阶段思维"：
第一阶段：先在心里建立知识骨架——识别材料中的 概念/定义、公式/定理、方法/步骤、易错点/常见错误，并为每个知识点标注考点强度（★★★必考/★★常考/★了解）。
第二阶段：基于这个骨架，按用户要求的方式组织输出。
输出使用 Markdown 格式。要求内容准确，不编造材料中没有的内容。"""


def _build_llm_prompt(text: str, method: str, method_name: str, title: str, is_math: bool,
                      requirement: str = "") -> str:
    """构建 LLM 蒸馏 Prompt（两阶段 + 方式要求 + 数学 LaTeX + 自定义要求）"""
    latex_hint = (
        "\n- 数学材料：所有公式必须用 LaTeX 语法输出（行内 $...$，独立公式 $$...$$）\n"
        if is_math else ""
    )
    custom_part = (
        f"\n⚠️ 用户自定义要求（最高优先级，必须逐条满足，可与{method_name}格式共存或覆盖之）：\n{requirement}\n"
        if requirement else ""
    )
    base = (
        f"请将以下学习材料「{title}」用{method_name}进行知识蒸馏。\n\n"
        f"{custom_part}"
        f"要求（两阶段）：\n"
        f"1. 第一阶段：先建立知识骨架——提取概念/公式/方法/易错点，标注考点强度（★★★必考 / ★★常考 / ★了解）\n"
        f"2. 第二阶段：按{method_name}的格式组织输出\n"
        f"3. 每条知识点尽量给出：是什么 + 怎么考 + 易错点\n"
        f"4. 不得编造材料中不存在的内容\n"
        f"{latex_hint}"
    )

    prompts = {
        "outline": base + """
【提纲式格式】
# 标题
## 章节/主题
- **知识点名**（★★★）：一句话要点
- ⚠️ 易错点：...
末尾给出复习优先级建议。

材料内容：
""",
        "qa": base + """
【Q&A式格式】
### Q1（概念）：问题
<details><summary>查看答案</summary>
答案
</details>
问题要有区分度：概念题、理解题、陷阱题（针对易错点）都要有。

材料内容：
""",
        "feynman": base + """
【费曼式格式】
## 概念N：名称
**原文要点：** ...
**通俗理解：** 用大白话解释，假设读者是零基础
**类比：** 一个生活中的类比
**一句话总结：** ...
**易错点：** ...

材料内容：
""",
        "formula": base + """
【公式卡片格式】
### 卡片N：公式/定理名
**内容：** ...
**适用条件：** ...
**常见变形：** ...
**易错点：** ...
按使用频率/重要性排序。

材料内容：
""",
        "mindmap": base + """
【思维导图格式】
用 Mermaid mindmap 语法绘制：
- 中心主题 → 主要章节 → 核心知识点 → 细节
- 层级不超过4层，节点文字简洁（不超过15字）
输出含 mermaid 代码块。

材料内容：
""",
        "cornell": base + """
【Cornell笔记格式】
| 线索（Cue） | 笔记（Notes） |
|:---|:---|
底部给出 2-3 句总结。

材料内容：
""",
    }
    return prompts.get(method, prompts["outline"]) + text[:8000]
