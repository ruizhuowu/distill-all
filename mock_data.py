"""
Mock 数据模块 - 湖经考霸（求职演示版）
用于展示社区功能、课程体系、考点库等
"""

# ============================================================
# 课程库
# ============================================================

COURSES = [
    {
        "id": "marxism",
        "name": "马克思主义基本原理",
        "code": "马原",
        "category": "公共必修",
        "department": "马克思主义学院",
        "semester": "2025秋季",
        "teachers": ["张教授", "李教授", "王教授"],
        "stats": {
            "total_materials": 127,
            "past_exams": 5,
            "active_students": 342,
            "avg_rating": 4.8,
        },
        "description": "涵盖唯物论、辩证法、认识论、历史唯物主义四大板块，期末考试以论述题为主。",
        "tags": ["热门", "必考", "有真题"],
    },
    {
        "id": "mao_zong",
        "name": "毛泽东思想和中国特色社会主义理论体系概论",
        "code": "毛概",
        "category": "公共必修",
        "department": "马克思主义学院",
        "semester": "2025秋季",
        "teachers": ["陈教授", "刘教授"],
        "stats": {
            "total_materials": 98,
            "past_exams": 4,
            "active_students": 289,
            "avg_rating": 4.6,
        },
        "description": "理论性较强，重点掌握各理论成果的历史地位和主要内容。",
        "tags": ["热门", "背诵量大"],
    },
    {
        "id": "math",
        "name": "高等数学",
        "code": "高数",
        "category": "公共必修",
        "department": "统计与数学学院",
        "semester": "2025秋季",
        "teachers": ["赵教授", "孙教授"],
        "stats": {
            "total_materials": 203,
            "past_exams": 8,
            "active_students": 512,
            "avg_rating": 4.9,
        },
        "description": "覆盖极限、微分、积分、级数等内容，计算量较大。",
        "tags": ["最热门", "挂科率高", "资料最多"],
    },
    {
        "id": "english",
        "name": "大学英语",
        "code": "大英",
        "category": "公共必修",
        "department": "外国语学院",
        "semester": "2025秋季",
        "teachers": ["周老师", "吴老师", "郑老师"],
        "stats": {
            "total_materials": 156,
            "past_exams": 3,
            "active_students": 423,
            "avg_rating": 4.3,
        },
        "description": "听说读写综合训练，期末含听力测试和写作。",
        "tags": ["日常积累", "四六级关联"],
    },
    {
        "id": "accounting",
        "name": "会计学原理",
        "code": "会计原理",
        "category": "专业核心",
        "department": "会计学院",
        "semester": "2025秋季",
        "teachers": ["钱教授"],
        "stats": {
            "total_materials": 89,
            "past_exams": 4,
            "active_students": 198,
            "avg_rating": 4.7,
        },
        "description": "会计学入门课程，借贷记账法是核心。",
        "tags": ["专业基础", "考证相关"],
    },
    {
        "id": "computer",
        "name": "计算机应用基础",
        "code": "计基",
        "category": "公共选修",
        "department": "信息管理学院",
        "semester": "2025秋季",
        "teachers": ["冯老师"],
        "stats": {
            "total_materials": 67,
            "past_exams": 2,
            "active_students": 156,
            "avg_rating": 4.2,
        },
        "description": "Office操作、计算机网络基础、程序设计入门。",
        "tags": ["实用", "通过率高"],
    },
]

# ============================================================
# 考点库（以马原为例）
# ============================================================

COURSE_KNOWLEDGE = {
    "marxism": {
        "key_points": [
            {
                "concept": "对立统一规律",
                "alias": "矛盾规律",
                "frequency": 5,  # 近5年出现次数
                "level": 3,      # 1=★ 2=★★ 3=★★★
                "recent_years": [2024, 2023, 2022, 2021, 2020],
                "exam_types": ["论述题", "材料分析题"],
                "tip": "张教授连续5年出大题，必须能默写定义+方法论意义",
                "source_text": "对立统一规律是唯物辩证法的实质和核心...",
            },
            {
                "concept": "实践的三特征",
                "frequency": 4,
                "level": 2,
                "recent_years": [2024, 2023, 2022, 2020],
                "exam_types": ["选择题", "简答题"],
                "tip": "三个特征必须写全：客观物质性、自觉能动性、社会历史性",
                "source_text": "实践具有客观物质性、自觉能动性和社会历史性...",
            },
            {
                "concept": "物质的唯一特性",
                "frequency": 4,
                "level": 3,
                "recent_years": [2024, 2023, 2021, 2020],
                "exam_types": ["选择题"],
                "tip": "唯一特性是'客观实在性'，根本属性是'运动'——这两个别搞混！",
                "source_text": "物质的唯一特性是客观实在性...",
            },
            {
                "concept": "联系的普遍性",
                "frequency": 3,
                "level": 2,
                "recent_years": [2024, 2022, 2021],
                "exam_types": ["辨析题", "选择题"],
                "tip": "联系具有普遍性、客观性、多样性、条件性",
                "source_text": "联系是指事物内部要素之间...",
            },
            {
                "concept": "否定之否定规律",
                "frequency": 2,
                "level": 2,
                "recent_years": [2023, 2021],
                "exam_types": ["简答题"],
                "tip": "波浪式前进、螺旋式上升——记住这个表述",
                "source_text": "事物的发展是螺旋式上升、波浪式前进的过程...",
            },
            {
                "concept": "意识的起源与本质",
                "frequency": 1,
                "level": 1,
                "recent_years": [2022],
                "exam_types": ["选择题"],
                "tip": "了解即可，近年很少单独出题",
                "source_text": "意识是物质世界长期发展的产物...",
            },
        ],
        "pitfalls": [
            {
                "point": "物质唯一特性 vs 根本属性",
                "error": "把'运动'当成唯一特性，或把'客观实在性'当成根本属性",
                "source": "2024年真题 选择题第8题，全班错误率62%",
                "correction": "唯一特性=客观实在性；根本属性=运动",
            },
            {
                "point": "实践三特征漏写",
                "error": "只写了'自觉能动性'和'社会历史性'，漏掉'客观物质性'",
                "source": "2023年简答题，扣2分（满分6分）",
                "correction": "三个特征缺一不可，建议用口诀'客自社'记忆",
            },
            {
                "point": "矛盾的同一性和斗争性关系",
                "error": "认为斗争性是绝对的所以更重要",
                "source": "2022年辨析题高频错点",
                "correction": "两者都是基本属性，不能说谁更重要。斗争性是绝对的，同一性是相对的",
            },
            {
                "point": "'质变就是发展'的错误理解",
                "error": "认为所有质变都是发展",
                "source": "历年经典易混点",
                "correction": "发展是新事物的产生和旧事物的灭亡，质变不一定是发展（可能是倒退）",
            },
        ],
        "teacher_tips": [
            "张教授偏爱辩证法大题，几乎每年必考",
            "李教授喜欢出材料分析题，注意结合时政热点",
            "选择题喜欢考'下列说法正确的是'这种辨析型",
            "论述题一定要分点作答，标①②③",
        ],
    }
}

# ============================================================
# 资料库（12份真实资料）
# ============================================================

RESOURCES = [
    # --- 马原 ---
    {
        "id": "res_001",
        "title": "马原期末复习重点笔记（完整版）",
        "course_id": "marxism",
        "course_name": "马克思主义基本原理",
        "type": "teacher_outline",
        "type_label": "📝 重点笔记",
        "uploader": "法学2301_林小夏",
        "avatar": "夏",
        "upload_time": "2小时前",
        "downloads": 312,
        "likes": 45,
        "rating": 4.8,
        "tags": ["期末", "重点", "唯物辩证法", "剩余价值"],
        "is_verified": True,
        "distilled_preview": "## 一、马克思主义哲学\n\n**唯物辩证法三大规律**：\n1. 对立统一规律（矛盾规律）★★★ - 事物内部对立又依存\n2. 质量互变规律 ★★ - 量变积累引发质变\n3. 否定之否定规律 ★★ - 螺旋式上升\n\n## 二、政治经济学\n\n**商品二重性**：使用价值 vs 价值\n**劳动二重性**：具体劳动 vs 抽象劳动\n**剩余价值理论**：m'=m/v，核心创新！\n\n⚠️ 易错点：价值≠价格，价格受供求影响围绕价值波动",
    },
    {
        "id": "res_002",
        "title": "马原高频考点与答题模板",
        "course_id": "marxism",
        "course_name": "马克思主义基本原理",
        "type": "past_exam",
        "type_label": "📋 答题技巧",
        "uploader": "国贸2301_陈志远",
        "avatar": "陈",
        "upload_time": "昨天",
        "downloads": 567,
        "likes": 89,
        "rating": 5.0,
        "tags": ["答题模板", "论述题", "简答题"],
        "is_verified": True,
        "distilled_preview": "**考频分析**：\n- 对立统一规律：5/5年考大题 ⭐⭐⭐\n- 实践三特征：4/5年考选择 ⭐⭐\n- 剩余价值：4/5年考计算 ⭐⭐\n\n**答题模板**：\n- 名词解释(4-6分)：定义归属 + 核心内涵 + 性质结果\n- 简答题(8-10分)：分点作答，(1)概念(2)关系(3)意义\n- 论述题(15-20分)：总述→分述→总结",
    },
    {
        "id": "res_003",
        "title": "马原易混概念辨析表",
        "course_id": "marxism",
        "course_name": "马克思主义基本原理",
        "type": "student_notes",
        "type_label": "📓 辨析总结",
        "uploader": "会计2202_张雨欣",
        "avatar": "张",
        "upload_time": "3天前",
        "downloads": 189,
        "likes": 34,
        "rating": 4.6,
        "tags": ["易混淆", "对比记忆", "避坑"],
        "is_verified": True,
        "distilled_preview": "| 概念对 | 区别要点 |\n|--------|----------|\n| 使用价值vs价值 | 自然属性 vs 社会属性 |\n| 具体劳动vs抽象劳动 | 创造使用价值 vs 形成价值 |\n| 不变资本vs可变资本 | 价值转移 vs 价值增殖 |\n| 绝对vs相对剩余价值 | 延长时间 vs 提高效率 |\n\n⚠️ 物质唯一特性=客观实在性；根本属性=运动",
    },
    # --- 毛概 ---
    {
        "id": "res_004",
        "title": "毛概必背知识点（全章节）",
        "course_id": "mao_zong",
        "course_name": "毛泽东思想和中国特色社会主义理论体系概论",
        "type": "mindmap",
        "type_label": "🗺️ 知识框架",
        "uploader": "金融2401_王子轩",
        "avatar": "王",
        "upload_time": "5小时前",
        "downloads": 234,
        "likes": 56,
        "rating": 4.7,
        "tags": ["毛概", "三个法宝", "南方谈话", "一国两制"],
        "is_verified": False,
        "distilled_preview": "## 核心考点速记\n\n**毛泽东思想活的灵魂**：实事求是、群众路线、独立自主 ★★★\n\n**新民主主义革命总路线**：无产阶级领导，人民大众，反帝反封建反官僚\n\n**一化三改**：社会主义工业化(主体) + 三大改造(两翼)\n\n**邓小平南方谈话(1992)**：社会主义本质=解放发展生产力+消灭剥削+共同富裕\n\n**新时代主要矛盾**：美好生活需要 vs 不平衡不充分发展",
    },
    {
        "id": "res_005",
        "title": "毛概各章重点句型翻译",
        "course_id": "mao_zong",
        "course_name": "毛泽东思想和中国特色社会主义理论体系概论",
        "type": "practice",
        "type_label": "✍️ 翻译练习",
        "uploader": "工管2301_李思涵",
        "avatar": "李",
        "upload_time": "1周前",
        "downloads": 445,
        "likes": 78,
        "rating": 4.9,
        "tags": ["翻译", "重点句型", "中英对照"],
        "is_verified": True,
        "distilled_preview": "**第一单元重点短语**：\n- reap a lot from... (从...获益良多)\n- have access to... (有权接触)\n- get along well with... (与...相处融洽)\n\n**第三单元重点短语**：\n- Now that... (既然)\n- adjust to... (适应)\n- with reluctance (勉强地)\n- urge sb. to do... (力劝某人做)",
    },
    # --- 高数 ---
    {
        "id": "res_006",
        "title": "高数期末复习主线：极限→导数→积分",
        "course_id": "math",
        "course_name": "高等数学",
        "type": "summary",
        "type_label": "📊 复习路线",
        "uploader": "统数2202_刘浩然",
        "avatar": "刘",
        "upload_time": "2天前",
        "downloads": 678,
        "likes": 123,
        "rating": 5.0,
        "tags": ["高数", "极限", "导数", "积分", "微分方程"],
        "is_verified": True,
        "distilled_preview": "### 一、极限与连续 ★★★\n等价无穷小：sinx~x, tanx~x, ln(1+x)~x, e^x-1~x\n两个重要极限：lim sinx/x=1, lim(1+1/x)^x=e\n\n### 二、微分中值定理 ★★★\n罗尔定理、拉格朗日定理、柯西定理\n求极值步骤：f'(x)=0 → 列表分析 → 确定极值\n\n### 三、积分学 ★★★\n凑微分、换元法(三角/根式)、分部积分(LIATE法则)\n定积分应用：面积、旋转体体积",
    },
    {
        "id": "res_007",
        "title": "高数常考函数与公式速查",
        "course_id": "math",
        "course_name": "高等数学",
        "type": "cheatsheet",
        "type_label": "📌 公式卡片",
        "uploader": "计科2401_赵雅婷",
        "avatar": "赵",
        "upload_time": "4天前",
        "downloads": 389,
        "likes": 67,
        "rating": 4.5,
        "tags": ["公式", "导数表", "积分表", "级数"],
        "is_verified": False,
        "distilled_preview": "**常用导数公式**：(sinx)'=cosx, (e^x)'=e^x, (lnx)'=1/x\n\n**分部积分**：∫udv = uv - ∫vdu\nLIATE选u顺序：Logarithmic > Inverse trig > Algebraic > Trig > Exponential\n\n**二阶微分方程**：r²+pr+q=0\n- 两不等实根：y=C₁e^(r₁x)+C₂e^(r₂x)\n- 共轭复根α±βi：y=e^(αx)(C₁cosβx+C₂sinβx)",
    },
    # --- 大英 ---
    {
        "id": "res_008",
        "title": "大学英语写作模板与关联词",
        "course_id": "english",
        "course_name": "大学英语",
        "type": "teacher_outline",
        "type_label": "📝 写作攻略",
        "uploader": "外语2301_黄诗琪",
        "avatar": "黄",
        "upload_time": "6小时前",
        "downloads": 256,
        "likes": 42,
        "rating": 4.6,
        "tags": ["写作", "作文模板", "关联词"],
        "is_verified": True,
        "distilled_preview": "## 作文结构（160-180词）\n\n**第一段**：Nowadays, ... has become a hot topic.\n**第二段**：On the one hand... On the other hand...\n**第三段**：In my opinion... Therefore...\n\n**必备关联词(5-7个)**：Firstly, Secondly, In addition, Moreover, However, Therefore, In conclusion\n\n**从句要求(5-7个)**：定语从句(which/who/that)、状语从句(if/because/although)、强调句(It is...that...)",
    },
    {
        "id": "res_009",
        "title": "英语语法重点：时态+情态动词+非谓语",
        "course_id": "english",
        "course_name": "大学英语",
        "type": "practice",
        "type_label": "✍️ 语法精讲",
        "uploader": "会计2401_吴佳怡",
        "avatar": "吴",
        "upload_time": "1天前",
        "downloads": 198,
        "likes": 35,
        "rating": 4.4,
        "tags": ["语法", "时态", "情态动词", "非谓语动词"],
        "is_verified": False,
        "distilled_preview": "**情态动词+have done**：\n- ought to have done 本应该做但没做\n- shouldn't have done 本不该做但做了\n- needn't have done 本不必做但做了\n\n**with复合结构**：\n- with + n. + doing (主动)\n- with + n. + done (被动)\n例：With the audience seated, the speech began.\n\n**主谓一致**：The number of... is; A number of... are",
    },
    # --- 会计原理 ---
    {
        "id": "res_010",
        "title": "会计学原理：借贷记账法完全指南",
        "course_id": "accounting",
        "course_name": "会计学原理",
        "type": "summary",
        "type_label": "📊 记账规则",
        "uploader": "会计2301_郑凯文",
        "avatar": "郑",
        "upload_time": "3天前",
        "downloads": 345,
        "likes": 67,
        "rating": 4.9,
        "tags": ["借贷记账法", "会计分录", "试算平衡"],
        "is_verified": True,
        "distilled_preview": "## 借贷记账法核心 ★★★\n\n**八字真言**：有借必有贷，借贷必相等\n\n**账户方向口诀**：\n资成费 → 借增贷减\n负所收 → 贷增借减\n\n**会计等式**：资产 = 负债 + 所有者权益\n\n**编制分录3步法**：\n1. 看增减 → 判断要素变化\n2. 找科目 → 匹配会计科目\n3. 定方向 → 确定借贷方向",
    },
    {
        "id": "res_011",
        "title": "常用会计科目表与典型分录",
        "course_id": "accounting",
        "course_name": "会计学原理",
        "type": "cheatsheet",
        "type_label": "📌 科目速查",
        "uploader": "会计2202_孙悦琳",
        "avatar": "孙",
        "upload_time": "5天前",
        "downloads": 278,
        "likes": 45,
        "rating": 4.7,
        "tags": ["会计科目", "分录示例", "T型账户"],
        "is_verified": True,
        "distilled_preview": "**典型业务分录**：\n\n① 投入资金：借:银行存款 / 贷:实收资本\n② 赊购材料：借:原材料+应交税费 / 贷:应付账款\n③ 销售商品：借:应收账款 / 贷:主营收入+应交税费\n④ 计提折旧：借:管理费用 / 贷:累计折旧\n⑤ 结转利润：借:各项收入 / 贷:本年利润 / 借:本年利润 / 贷:各项费用\n\n⚠️ 试算平衡≠一定正确！漏记/重记/科目错不影响平衡",
    },
    # --- 计基 ---
    {
        "id": "res_012",
        "title": "计算机基础：Office操作+网络知识",
        "course_id": "computer",
        "course_name": "计算机应用基础",
        "type": "summary",
        "type_label": "📊 操作要点",
        "uploader": "信管2401_周子墨",
        "avatar": "周",
        "upload_time": "4小时前",
        "downloads": 167,
        "likes": 28,
        "rating": 4.3,
        "tags": ["Word", "Excel", "PPT", "计算机网络"],
        "is_verified": False,
        "distilled_preview": "## Word重点 ★★\n格式刷：单击刷1次，双击刷多次\n邮件合并：主文档+数据源\n\n## Excel重点 ★★★\n引用方式：A1(相对) / $A$1(绝对) / $A1(混合)\n常用函数：SUM, AVERAGE, IF, VLOOKUP, COUNTIF\n分类汇总前必须先排序！\n\n## PPT重点 ★★\n母版统一字体背景Logo\n动画：进入/强调/退出/动作路径\n\n## 网络基础 ★★\nIP地址：IPv4(32位) / IPv6(128位)\n端口：HTTP(80), SMTP(25), POP3(110)",
    },
]

# ============================================================
# 讨论区帖子（8条真实感帖子）
# ============================================================

POSTS = [
    {
        "id": "post_001",
        "title": "张教授的马原今年会考啥？老生来分析一下",
        "author": "法学2301_林小夏",
        "avatar": "夏",
        "course_id": "marxism",
        "course_name": "马克思主义基本原理",
        "type": "discussion",
        "type_label": "💬 讨论",
        "content": "上周去蹭了张教授的复习课，他重点强调了这几个方向：\n\n1. **辩证法大题**（概率85%）：对立统一规律连续5年考大题，今年可能考否定之否定\n2. **剩余价值计算**（概率70%）：去年没考m'=m/v，今年很可能补上\n3. **认识论结合科技热点**（概率60%）：AI发展相关的实践观\n\n张教授原话：'不要死记硬背，要理解逻辑链'\n\n大家觉得呢？有没有其他预测？",
        "replies": 23,
        "likes": 45,
        "views": 312,
        "created_at": "3小时前",
        "is_hot": True,
        "is_solved": False,
        "tags": ["预测", "马原", "张教授"],
    },
    {
        "id": "post_002",
        "title": "会计学原理借贷记账法搞不懂怎么办😭",
        "author": "会计2401_王子轩",
        "avatar": "王",
        "course_id": "accounting",
        "course_name": "会计学原理",
        "type": "help",
        "type_label": "❓ 求助",
        "content": "下周就要考会计学了，但是借贷方向老是搞混！\n\n比如：\n- 应收账款增加为什么记借方？\n- 应付账款增加为什么记贷方？\n- 预收账款到底是资产还是负债？\n\n钱教授讲课太快了跟不上...求学长学姐分享记忆口诀或者整理好的笔记！感激不尽！🙏",
        "replies": 18,
        "likes": 12,
        "views": 156,
        "created_at": "1小时前",
        "is_hot": False,
        "is_solved": True,
        "tags": ["求助", "会计", "借贷记账法"],
    },
    {
        "id": "post_003",
        "title": "【经验贴】高数从58到92，我是怎么逆袭的",
        "author": "统数2202_刘浩然",
        "avatar": "刘",
        "course_id": "math",
        "course_name": "高等数学",
        "type": "experience",
        "type_label": "💡 经验",
        "content": "大一上学期高数期中考了58分（全班倒数），期末硬生生拉到92。分享一下我的血泪经验：\n\n**第一阶段：补基础（考前2周）**\n- 把课本例题全部做一遍，不要看答案\n- 重点搞懂极限的定义和连续性判断\n- 等价无穷小那8个公式背得滚瓜烂熟\n\n**第二阶段：刷真题（考前1周）**\n- 往年真题做3遍，第一遍不限时，第二遍限时，第三遍只做错题\n- 错题整理到本子上，写清楚错因\n\n**第三阶段：冲刺（考前3天）**\n- 只看错题和公式卡片\n- 背诵常见题型解法模板（特别是积分的凑微分）\n\n**最关键的一点**：不要盲目刷题，每道题都要知道考的是哪个知识点！\n\n希望对大家有帮助！有问题评论区问~",
        "replies": 56,
        "likes": 189,
        "views": 1234,
        "created_at": "2天前",
        "is_hot": True,
        "is_solved": False,
        "tags": ["经验", "高数", "逆袭", "干货"],
    },
    {
        "id": "post_004",
        "title": "这道马原选择题关于'质的多样性'选B不选C？",
        "author": "国贸2401_陈志远",
        "avatar": "陈",
        "course_id": "marxism",
        "course_name": "马克思主义基本原理",
        "type": "question",
        "type_label": "❓ 问题",
        "content": "题目：\"事物的质是由什么决定的？\"\nA. 事物的量的规定性\nB. 事物内部矛盾的特殊性 ★答案\nC. 事物的本质属性\nD. 人的主观认识\n\n我选了C但答案是B，为什么啊？\n\n我的理解：质不就是本质属性吗？为什么是矛盾特殊性决定的？\n\n有人能解释一下这个区别吗？感觉这两个选项很像...",
        "replies": 13,
        "likes": 8,
        "views": 156,
        "created_at": "5小时前",
        "is_hot": False,
        "is_solved": True,
        "best_answer": "好问题！这确实是高频易混点。\n\n**区分关键**：\n- **矛盾特殊性 → 决定质**（原因/根源）\n- **本质属性 → 表现质**（外在体现）\n\n打个比方：水的质由H₂O分子结构决定（矛盾特殊性），而\"无色无味透明液体\"是它的本质属性（表现形式）。\n\n所以题目问\"由什么决定\"要选B，问\"什么是质的表现\"才选C。建议记住：特殊性→决定；属性→表现。",
        "tags": ["问题", "马原", "选择题", "易混淆"],
    },
    {
        "id": "post_005",
        "title": "⚠️避坑！去年马原实践三特征漏写扣分惨案",
        "author": "金融2201_张雨欣",
        "avatar": "张",
        "course_id": "marxism",
        "course_name": "马克思主义基本原理",
        "type": "pitfall",
        "type_label": "⚠️ 避坑",
        "content": "⚠️ **2024年马原期末考试，我们班这道题错了超过一半的人！**\n\n题目（简答题6分）：\"简述实践的基本特征\"\n\n标准答案要求写出**三个特征**：\n1. 客观物质性 ✅\n2. 自觉能动性 ✅\n3. 社会历史性 ✅\n\n**但是！** 很多人（包括我）只写了后面两个，漏掉了第一个\"客观物质性\"！结果6分只拿了4分。\n\n**为什么会漏？** 因为\"自觉能动性\"和\"社会历史性\"比较好理解，老师上课也强调得多，而\"客观物质性\"感觉太 obvious 了就忽略了...\n\n**教训+口诀**：\n- 实践三特征一个都不能少，每个2分\n- 用口诀记：**「客自社」** = 客观物质性 + 自觉能动性 + 社会历史性\n\n希望大家不要重蹈覆辙！转发给身边的同学！",
        "replies": 34,
        "likes": 156,
        "views": 890,
        "created_at": "1天前",
        "is_hot": True,
        "is_solved": False,
        "tags": ["避坑", "马原", "易错", "必看", "实践三特征"],
    },
    {
        "id": "post_006",
        "title": "毛概南方谈话1992年那些考点，我整理好了",
        "author": "工管2401_李思涵",
        "avatar": "李",
        "course_id": "mao_zong",
        "course_name": "毛泽东思想和中国特色社会主义理论体系概论",
        "type": "share",
        "type_label": "📝 分享",
        "content": "毛概第五章邓小平理论，南方谈话是绝对的重点！我把核心考点整理出来了：\n\n**★★★ 必背**：\n1. **社会主义本质**：解放生产力，发展生产力，消灭剥削，消除两极分化，最终达到共同富裕\n2. **三个有利于标准**：是否有利于生产力/综合国力/生活水平\n3. **市场经济论**：社会主义可以搞市场经济（计划和市场都是手段）\n\n**★★ 重要**：\n4. 改革也是解放生产力\n5. 发展才是硬道理\n6. 科学技术是第一生产力\n\n已经做成思维导图上传到资料库了，需要的同学可以去下载~\n\n补充：陈老师说今年论述题很可能考\"社会主义本质与共同富裕的关系\"",
        "replies": 28,
        "likes": 89,
        "views": 567,
        "created_at": "6小时前",
        "is_hot": True,
        "is_solved": False,
        "tags": ["分享", "毛概", "南方谈话", "邓小平理论", "必背"],
    },
    {
        "id": "post_007",
        "title": "Excel绝对引用vs相对引用终于搞懂了！",
        "author": "信管2401_赵雅婷",
        "avatar": "赵",
        "course_id": "computer",
        "course_name": "计算机应用基础",
        "type": "experience",
        "type_label": "💡 经验",
        "content": "计基考试在即，之前一直搞不懂Excel的$符号什么意思，今天终于悟了！\n\n**三种引用方式**：\n| 类型 | 格式 | 复制时 |\n|------|------|--------|\n| 相对引用 | A1 | 自动变化 |\n| 绝对引用 | $A$1 | 不变(锁定) |\n| 混合引用 | $A1或A$1 | 行或列一个变 |\n\n**记忆技巧**：\n- $ = 锁定，加在谁前面谁就不变\n- $A$1 = 行列都锁（拖到哪里都是A1）\n- $A1 = 锁列不锁行（横向拖不变，纵向拖变）\n- A$1 = 锁行不锁列（相反）\n\n**考试常考场景**：\n- 做九九乘法表必须用混合引用\n- VLOOKUP查找值通常用绝对引用\n\n希望对还在纠结的同学有帮助！",
        "replies": 15,
        "likes": 45,
        "views": 234,
        "created_at": "4小时前",
        "is_hot": False,
        "is_solved": False,
        "tags": ["经验", "计基", "Excel", "引用方式"],
    },
    {
        "id": "post_008",
        "title": "大学英语作文总是写不够160词怎么办？",
        "author": "外语2301_黄诗琪",
        "avatar": "黄",
        "course_id": "english",
        "course_name": "大学英语",
        "type": "help",
        "type_label": "❓ 求助",
        "content": "每次英语考试写作都卡在120词左右，怎么扩展到160-180词啊？\n\n目前的问题：\n1. 观点说完了不知道怎么展开\n2. 句式太单一，全是简单句\n3. 关联词就会用and, but, so\n\n求大神分享扩展技巧！最好有模板可以套用那种\n\nPS: 周老师说过作文要有5-7个从句才能拿高分，但我只会写定语从句...",
        "replies": 21,
        "likes": 33,
        "views": 189,
        "created_at": "8小时前",
        "is_hot": False,
        "is_solved": True,
        "best_answer": "分享我的万能模板：\n\n**第一段(40-50词)**：Nowadays, [话题] has become a hot topic among people. Some people believe that [观点A], while others argue that [观点B]. From my perspective, I tend to support the former/latter view.\n\n**第二段(70-80词)**：There are several reasons accounting for this phenomenon. Firstly, [理由1]. For example/For instance, [例子]. Secondly, [理由2]. Moreover, [补充]. A case in point is that [另一个例子]. \n\n**第三段(40-50词)**：Taking all these factors into consideration, we may reasonably conclude that [总结观点]. Therefore, it is high time that we took measures to [建议/行动]. Only in this way can we [美好愿景].\n\n**扩充技巧**：\n- 每个观点后加For example举例\n- 用In addition, Furthermore, Moreover过渡\n- 加状语从句(When it comes to..., In terms of...)\n- 结尾用强调句(It is...that...)或倒装(Only...can we...)",
        "tags": ["求助", "大英", "写作", "作文模板"],
    },
]

# ============================================================
# 用户排行榜（真实学生名）
# ============================================================

LEADERBOARD = [
    {"rank": 1, "name": "统数2202_刘浩然", "points": 5680, "contributions": 23, "avatar": "刘"},
    {"rank": 2, "name": "金融2201_张雨欣", "points": 4320, "contributions": 18, "avatar": "张"},
    {"rank": 3, "name": "法学2301_林小夏", "points": 3890, "contributions": 31, "avatar": "夏"},
    {"rank": 4, "name": "国贸2301_陈志远", "points": 3450, "contributions": 15, "avatar": "陈"},
    {"rank": 5, "name": "会计2202_孙悦琳", "points": 2980, "contributions": 12, "avatar": "孙"},
    {"rank": 6, "name": "工管2401_李思涵", "points": 2560, "contributions": 9, "avatar": "李"},
    {"rank": 7, "name": "信管2401_赵雅婷", "points": 2100, "contributions": 7, "avatar": "赵"},
    {"rank": 8, "name": "外语2301_黄诗琪", "points": 1890, "contributions": 11, "avatar": "黄"},
]

# ============================================================
# 全站统计数据
# ============================================================

SITE_STATS = {
    "total_courses": 6,
    "total_materials": 740,
    "total_students": 1280,
    "total_downloads": 15600,
    "total_posts": 340,
    "avg_rating": 4.7,
}

# ============================================================
# 辅助函数
# ============================================================

def get_course_by_id(course_id: str) -> dict:
    """根据ID获取课程信息"""
    for c in COURSES:
        if c["id"] == course_id:
            return c
    return None


def get_resources_by_course(course_id: str = None) -> list:
    """获取资料列表，可按课程筛选"""
    if course_id:
        return [r for r in RESOURCES if r["course_id"] == course_id]
    return RESOURCES


def get_posts_by_course(course_id: str = None) -> list:
    """获取帖子列表，可按课程筛选"""
    if course_id:
        return [p for p in POSTS if p["course_id"] == course_id]
    return POSTS


def get_knowledge_points(course_id: str) -> list:
    """获取某课程的考点列表"""
    return COURSE_KNOWLEDGE.get(course_id, {}).get("key_points", [])


def get_pitfalls(course_id: str) -> list:
    """获取某课程的易错点列表"""
    return COURSE_KNOWLEDGE.get(course_id, {}).get("pitfalls", [])
