#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Review Generator Helper (Book Distiller v3.0 创作者矩阵版)
1. 全书书评创作矩阵规划 (Review Matrix Planning):
   - 自动生成 reviews/00_全书书评创作矩阵规划.md，为全书定制 4~6 篇差异化高赞选题。
2. 主题 Slug 语义化命名 (Semantic Slug Naming):
   - 产出文件带主题 Slug: review_{platform}_{slug}_{timestamp}.md
3. 四段心流积木自由搭配菜单 (Flow Modular Menu):
   - 供创作者自由挑选题材与心流路径 (flow_menu_{timestamp}.md)。
4. 双文件分离交付 (Dual-file Delivery):
   - 纯净平台排版正文 (.md) + 独立血统溯源与联系图谱 (_provenance.md)
"""

import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


def slugify_topic(topic: Optional[str]) -> str:
    """
    将主题转化为安全规范的文件名 Slug（去除特殊符号，保留中英文字符与下划线）
    """
    if not topic:
        return "顿悟时刻"
    clean = re.sub(r'[^\w\u4e00-\u9fff\-]+', '_', topic.strip())
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean[:30] if clean else "顿悟时刻"


def collect_insights_material(book_dir: Path, topic_keyword: Optional[str] = None) -> Dict[str, List[str]]:
    """
    从 insights/ 目录下扫描并收集可用原料（反直觉选题、金句、痛点、概念模型、行动清单）
    """
    insights_dir = book_dir / "insights"
    materials = {
        "hooks": [],
        "quotes": [],
        "symptoms": [],
        "concepts": [],
        "checklists": []
    }
    
    if not insights_dir.exists():
        return materials
        
    # 1. 扫描金句
    quotes_file = insights_dir / "00_全书高穿透金句大全.md"
    if quotes_file.exists():
        text = quotes_file.read_text(encoding="utf-8")
        zh_quotes = re.findall(r"-\s+\*\*中文\*\*：(.*?)(?:\n|$)", text)
        if zh_quotes:
            if topic_keyword:
                matched = [q.strip() for q in zh_quotes if topic_keyword in q]
                materials["quotes"] = matched if matched else [q.strip() for q in zh_quotes[:6]]
            else:
                materials["quotes"] = [q.strip() for q in zh_quotes[:6]]
        else:
            quotes = [line.strip("> ") for line in text.splitlines() if line.startswith("> ") and len(line) > 10 and not line.startswith("> 精选")]
            materials["quotes"] = quotes[:6]

    # 2. 扫描选题与反直觉
    hooks_file = insights_dir / "00_全书爆款选题与反直觉库.md"
    if hooks_file.exists():
        text = hooks_file.read_text(encoding="utf-8")
        titles = re.findall(r"-\s+\*\*爆款大标题\*\*：《(.*?)》", text)
        contrarians = re.findall(r"-\s+\*\*核心认知差\*\*：(.*?)(?:\n|$)", text)
        parsed_hooks = []
        for t, c in zip(titles, contrarians):
            parsed_hooks.append(f"{t.strip()}（反直觉：{c.strip()}）")
        if parsed_hooks:
            materials["hooks"] = parsed_hooks[:6]
        else:
            hooks = [line.strip("- ") for line in text.splitlines() if "反直觉" in line or "打破" in line or line.startswith("- ⚡️")]
            materials["hooks"] = hooks[:6]
        
    # 3. 扫描痛点（精准提取读者真实疑问句，过滤表格格式符号）
    symptom_file = insights_dir / "00_读者现实痛点与对号入座索引.md"
    if symptom_file.exists():
        text = symptom_file.read_text(encoding="utf-8")
        symptom_matches = re.findall(r"\|\s+\*\*“([^”]+)”\*\*", text)
        if symptom_matches:
            materials["symptoms"] = [s.strip() for s in symptom_matches[:8]]
        else:
            symptoms = [line.split("|")[1].strip().strip("*“ ”") for line in text.splitlines() if "|" in line and "现实痛点" not in line and "---" not in line and len(line.split("|")) > 2]
            materials["symptoms"] = symptoms[:6]

    # 4. 扫描思维模型
    concepts_file = insights_dir / "00_全书核心概念与思维模型图谱.md"
    if concepts_file.exists():
        text = concepts_file.read_text(encoding="utf-8")
        concepts = re.findall(r"\[\[(.*?)\]\]", text)
        clean_concepts = [c for c in concepts if not c.endswith(".md") and len(c) < 25]
        materials["concepts"] = list(dict.fromkeys(clean_concepts))[:8]
        
    return materials


def generate_review_matrix(book_dir: Path) -> Path:
    """
    为整本书生成多篇书评创作矩阵规划表 (00_全书书评创作矩阵规划.md)
    """
    reviews_dir = book_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    
    matrix_file = reviews_dir / "00_全书书评创作矩阵规划.md"
    book_title = book_dir.name
    book_display_title = book_title.replace("_", " ")
    materials = collect_insights_material(book_dir)
    
    # 尝试从选题库提取具体的 Top 选题信息
    hooks_file = book_dir / "insights" / "00_全书爆款选题与反直觉库.md"
    custom_rows = []
    if hooks_file.exists():
        htext = hooks_file.read_text(encoding="utf-8")
        top_matches = re.findall(r"###\s+[🥇🥈🥉🏅].*?-\s+\*\*爆款大标题\*\*：《(.*?)》.*?-\s+\*\*痛点与情绪\*\*：(.*?)(?:\n|$).*?-\s+\*\*核心认知差\*\*：(.*?)(?:\n|$)", htext, re.DOTALL)
        if top_matches:
            platforms = ["小红书 (图文)", "Threads / X (串帖)", "微信公众号 (深度随笔)", "小红书 / 博客 (思维破局)", "深度长文 (人生终局)"]
            combos = ["`1A + 2B + 3A + 4A`", "`1B + 2A + 3C + 4B`", "`1C + 2C + 3B + 4A`", "`1B + 2B + 3A + 4B`", "`1A + 2C + 3C + 4C`"]
            for idx, (t, p, c) in enumerate(top_matches[:5]):
                plat = platforms[idx % len(platforms)]
                combo = combos[idx % len(combos)]
                concept_tag = f"[[{materials['concepts'][idx % len(materials['concepts'])]}]]" if materials["concepts"] else "[[核心模型]]"
                custom_rows.append(f"| **0{idx+1}** | 《{t.strip()}》 | {plat} | {p.strip()[:35]}... | {concept_tag} | {combo} | 待创作 |")

    with open(matrix_file, "w", encoding="utf-8") as f:
        f.write(f"# 🗺️ 《{book_display_title}》全书书评创作矩阵规划表\n\n")
        f.write("> 本规划表基于全书 4D 黄金原料与核心模型，拆解出针对不同平台与生活痛点的高穿透矩阵选题。\n\n")
        f.write(f"- **书籍名称**：{book_display_title}\n")
        f.write(f"- **规划生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("## 📑 核心发帖选题矩阵\n\n")
        f.write("| 序号 | 选题大标题 | 目标平台 | 读者切入痛点 (Hook) | 核心思维模型 | 推荐四段心流组合 | 创作状态 |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        if custom_rows:
            for row in custom_rows:
                f.write(f"{row}\n")
        else:
            s1 = materials["symptoms"][0] if materials["symptoms"] else "深陷内耗与无效努力"
            s2 = materials["symptoms"][1] if len(materials["symptoms"]) > 1 else "讨好型人格与不敢拒绝"
            s3 = materials["symptoms"][2] if len(materials["symptoms"]) > 2 else "执行力瘫痪与目标迷茫"
            s4 = materials["symptoms"][3] if len(materials["symptoms"]) > 3 else "缺乏时间主权与精力透支"
            c1 = materials["concepts"][0] if materials["concepts"] else "核心概念A"
            c2 = materials["concepts"][1] if len(materials["concepts"]) > 1 else "核心概念B"
            c3 = materials["concepts"][2] if len(materials["concepts"]) > 2 else "核心概念C"
            c4 = materials["concepts"][3] if len(materials["concepts"]) > 3 else "核心概念D"
            f.write(f"| **01** | 《读完《{book_display_title}》，我终于戒掉了那该死的内耗》 | 小红书 (图文) | {s1} | [[{c1}]] | `1B + 2A + 3A + 4A` | 待创作 |\n")
            f.write(f"| **02** | 《你不是意志力差，你只是努力方向从一开始就反了》 | Threads / X | {s2} | [[{c2}]] | `1A + 2B + 3B + 4B` | 待创作 |\n")
            f.write(f"| **03** | 《写给经常自我怀疑的朋友：如何看清现实的底层规律》 | 公众号 (长随笔) | {s3} | [[{c3}]] | `1C + 2C + 3C + 4A` | 待创作 |\n")
            f.write(f"| **04** | 《真正厉害的人，早就悄悄换掉了这套思维操作系统》 | 小红书 / 博客 | {s4} | [[{c4}]] | `1B + 2C + 3A + 4B` | 待创作 |\n")
        f.write("\n---\n\n")
        f.write("### 💡 选题矩阵布局策略说明：\n")
        f.write("1. **篇 01（引流情绪向）**：从小红书高频情感共鸣切入，用反常识撕开内耗遮羞布，驱动高赞与收藏。\n")
        f.write("2. **篇 02（认知觉醒向）**：以 Threads 串帖形式，直击讨好与低效努力痛点，给读者认知松绑。\n")
        f.write("3. **篇 03（深度沉淀向）**：以公众号深夜随笔长文，促膝长谈，深度解构思维模型，建立信任感。\n")
        f.write("4. **篇 04（工具实操向）**：强调最小阻力行动法则，给极简微清单，适合多平台分发。\n")
        
    print(f"✨ 成功生成全书书评创作矩阵规划表！")
    print(f"🗺️ 规划文件: {matrix_file}")
    return matrix_file


def generate_flow_menu(book_dir: Path, topic: Optional[str] = None) -> Path:
    """
    生成四段心流积木自由搭配菜单文件 (flow_menu_{timestamp}.md)
    """
    reviews_dir = book_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    menu_file = reviews_dir / f"flow_menu_{timestamp}.md"
    
    book_title = book_dir.name
    materials = collect_insights_material(book_dir, topic_keyword=topic)
    
    h1 = materials["hooks"][0] if len(materials["hooks"]) > 0 else "打破惯性盲区：越是努力，反而越容易陷入认知死角"
    h2 = materials["hooks"][1] if len(materials["hooks"]) > 1 else "常规误区 vs 深层反转：我们不是能力差，而是目标从一开始就设定错了"
    h3 = materials["hooks"][2] if len(materials["hooks"]) > 2 else "为什么很多人每天都在疲于奔命，却始终没有安全感？"
    
    s1 = materials["symptoms"][0] if len(materials["symptoms"]) > 0 else "陷入盲目努力与深度精神内耗"
    s2 = materials["symptoms"][1] if len(materials["symptoms"]) > 1 else "经常陷入自我怀疑与讨好型人格"
    s3 = materials["symptoms"][2] if len(materials["symptoms"]) > 2 else "执行力瘫痪，计划永远停留在明天"
    
    c1 = materials["concepts"][0] if len(materials["concepts"]) > 0 else "反思闭环与机器思维"
    c2 = materials["concepts"][1] if len(materials["concepts"]) > 1 else "第一性原理与现实主义"
    c3 = materials["concepts"][2] if len(materials["concepts"]) > 2 else "阻抗最小路径"
    
    q1 = materials["quotes"][0] if len(materials["quotes"]) > 0 else "痛苦加上反思等于进步。"
    q2 = materials["quotes"][1] if len(materials["quotes"]) > 1 else "生活不是向别人交卷的考试，允许自己有属于自己的节奏。"
    q3 = materials["quotes"][2] if len(materials["quotes"]) > 2 else "愿你在喧嚣的世界里，找到属于自己的秩序。"

    with open(menu_file, "w", encoding="utf-8") as f:
        f.write(f"# 🧩 《{book_title}》四段心流自由搭配菜单 (Flow Modular Menu)\n\n")
        f.write(f"> 可以在以下四段心流中各选一项（如组合 `1B + 2A + 3A + 4A`），随后吩咐 AI 依据所选组合编写文章！\n\n")
        f.write(f"- **书籍名称**：{book_title}\n")
        f.write(f"- **探讨主题**：{topic if topic else '全书精华自由拼配'}\n")
        f.write(f"- **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("### 🎯 阶段 1：【Hook / 痛点引子】（挑一个最想聊的切入点）\n\n")
        f.write(f"- **[1A 扎心情境型]**：从读者的现实痛点切入 —— 「{s1}」，描摹深夜疲惫瞬间，拉近与读者的距离。\n")
        f.write(f"- **[1B 认知打脸型]**：用原书的反直觉事实打破盲区 —— 「{h1}」，制造强烈反差好奇。\n")
        f.write(f"- **[1C 灵魂发问型]**：直击本质的尖锐提问 —— 「{h3}」，开门见山破除心防。\n\n")
        
        f.write("### 💡 阶段 2：【Inversion / 认知反转】（挑一个作为核心解释）\n\n")
        f.write(f"- **[2A 底层系统归因]**：引入核心概念 [[{c1}]]，指出痛苦不是不够努力，而是底层操作系统设错了。\n")
        f.write(f"- **[2B 动机真相剖析]**：借助 [[{c2}]]，剥开表面借口，直面内心深处对失控与内耗的恐惧。\n")
        f.write(f"- **[2C 视角升维置换]**：借助 [[{c3}]]，将问题从个人情绪的死胡同转移到更高维度的规律。\n\n")
        
        f.write("### 🛠️ 阶段 3：【Action / 极简解法】（挑一个可落地的行动抓手）\n\n")
        f.write("- **[3A 微习惯切片法]**：下班后、睡前 5 分钟就能做的阻力最小微动作（如：每日 1 件事最小复盘）。\n")
        f.write("- **[3B 阻断红线法则]**：不再逼自己做什么，而是列出一条“绝不再无谓消耗自己”的防守红线。\n")
        f.write("- **[3C 三步闭环落地]**：情绪察觉 ➔ 记录阻抗 ➔ 最小微调的具体操作流程。\n\n")
        
        f.write("### 🌿 阶段 4：【Ending / 灵魂收尾】（挑一个传递给读者的余音）\n\n")
        f.write(f"- **[4A 温暖托举祝福]**：沉静平视的深夜促膝长谈 —— 「{q2}」，抚平内疚与自我苛责。\n")
        f.write(f"- **[4B 极简警醒金句]**：留下一句极具穿透力的灵魂判词 —— 「{q1}」，驱动读者点赞收藏。\n")
        f.write(f"- **[4C 开放留白共勉]**：留下一个给未来的叩问 —— 「{q3}」，引发评论区互动回音。\n\n")
        
        f.write("---\n\n")
        f.write("### ✍️ 推荐搭配组合示例：\n")
        f.write("- **治愈内耗流**：`1A + 2A + 3A + 4A`（适合小红书/公众号晚安心灵长文）\n")
        f.write("- **硬核觉醒流**：`1B + 2B + 3B + 4B`（适合 Threads/X 高赞思维反转串帖）\n")
        f.write("- **实操破局流**：`1C + 2C + 3C + 4B`（适合自律成长与工具清单向笔记）\n")
        
    print(f"✨ 成功生成四段心流积木自由搭配菜单！")
    print(f"📋 菜单文件: {menu_file}")
    return menu_file


def create_dual_review_files(
    book_dir: Path,
    platform: str,
    flow_combo: str = "1B+2A+3A+4A",
    topic: Optional[str] = None,
    chapter_file: Optional[str] = None
) -> Tuple[Path, Path]:
    """
    根据选定心流生成双文件：
    1. 纯净正文 review_{platform}_{slug}_{timestamp}.md
    2. 独立血统溯源 review_{platform}_{slug}_{timestamp}_provenance.md
    """
    reviews_dir = book_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = slugify_topic(topic)
    
    clean_file = reviews_dir / f"review_{platform}_{topic_slug}_{timestamp}.md"
    prov_file = reviews_dir / f"review_{platform}_{topic_slug}_{timestamp}_provenance.md"
    
    book_title = book_dir.name
    materials = collect_insights_material(book_dir, topic_keyword=topic)
    
    topic_display = topic if topic else f"读《{book_title}》的顿悟时刻"
    source_chapter_name = chapter_file if chapter_file else "核心正文章节"
    
    quote_sample = materials["quotes"][0] if materials["quotes"] else "痛苦加上反思等于进步。"
    hook_sample = materials["hooks"][0] if materials["hooks"] else "打破惯性思维的反直觉洞察"
    concept_sample = materials["concepts"][0] if materials["concepts"] else "反思闭环与心智升级"
    symptom_sample = materials["symptoms"][0] if materials["symptoms"] else "陷入盲目努力与深度精神内耗"
    
    # 1. 写入纯净正文
    with open(clean_file, "w", encoding="utf-8") as f:
        if platform == "xhs":
            f.write(f"# 读完《{book_title}》，我终于戒掉了那该死的内耗\n")
            f.write(f"## 原来真正厉害的人，早就悄悄换掉了这种底层思维\n\n")
            f.write("不知道你有没有过这样的时刻：\n")
            f.write(f"每天都在疲惫地赶路，却总觉得自己在原地打转。直到最近翻开《{book_title}》，书里这句话瞬间击中了我：\n\n")
            f.write(f"> 「{quote_sample}」\n\n")
            f.write("今天挑出让我最醍醐灌顶的 3 个认知刷新，分享给你：\n\n")
            f.write("1️⃣ **顿悟点一：痛苦不是惩罚，而是认知的信号灯**\n")
            f.write(f"在原书中，作者提到关于 [[{concept_sample}]] 的重要原理。我们之所以痛苦，不是因为能力不够，而是因为我们一直在用旧的地图寻找新大陆。\n\n")
            f.write("2️⃣ **顿悟点二：放慢节奏，找到阻力最小的行动闭环**\n")
            f.write("不要试图一天之内改变所有习惯，先从今晚的一件微行动做起。\n\n")
            f.write("3️⃣ **顿悟点三：允许自己有不完美的缝隙**\n")
            f.write("成长不是向所有人交卷的考试，而是允许自己放下执念。\n\n")
            f.write("🌿 **写在最后：**\n愿你在喧嚣的世界里，找到属于自己的秩序。\n\n")
            f.write("#读书笔记 #认知思维 #自我提升 #书单推荐 #治愈内耗\n\n")
        elif platform == "threads":
            f.write(f"# 读完《{book_title}》的 4 帖心流思考 🧵\n\n")
            f.write("#### 1/4【Hook 引子】\n")
            f.write(f"刚读完《{book_title}》，里面有句话彻底扎醒了我：\n")
            f.write(f"> “{quote_sample}”\n\n")
            f.write("表面上是在讲生活方法，本质上却是在替我们解开那些说不出的精神内耗。🧵👇\n\n")
            f.write("#### 2/4【认知反转】\n")
            f.write(f"书中指出了一个极其反直觉的真相：\n{hook_sample}。\n")
            f.write("当你习惯了在脑海里反复内耗，你其实是在放弃对自己生活的掌控权。\n\n")
            f.write("#### 3/4【行动解法】\n")
            f.write("如果你也正陷在类似的消耗里，不妨试着做这一个最小改变：\n")
            f.write("越是迷茫痛苦的节点，越不要在脑海里死磕，回到现实里做最小阻力动作。\n\n")
            f.write("#### 4/4【温柔收尾】\n")
            f.write("生活不是一场需要向所有人交卷的考试。\n放轻松一点，你已经在变好的路上了。\n\n")
        else: # wechat
            f.write(f"# 《{book_title}》：你不是能力不够，你只是从未真正看清现实\n\n")
            f.write(f"文 / 读书人\n\n")
            f.write(f"前几天深夜整理书架的时候，重新翻开了《{book_title}》。\n\n")
            f.write("很长一段时间里，很多人都在面临一种隐秘的消耗：明明每天都在拼命努力，却始终感觉内心空空落落。\n\n")
            f.write(f"直到看到书中关于 [[{concept_sample}]] 的论述，才突然明白，真正的成长从来不是逼自己脱胎换骨，而是学会看清真实的规律。\n\n")
            f.write(f"> 「{quote_sample}」\n\n")
            f.write("（此处展开具体生活场景与思维模型的深度解构随笔……）\n\n")
            
        f.write(f"> 🧬 本文设计演进与完整血统溯源档案：见同目录下的 [{prov_file.name}](./{prov_file.name})\n")
        
    # 2. 写入独立溯源档案
    with open(prov_file, "w", encoding="utf-8") as f:
        f.write(f"# 🧬 《{book_title}》书评完整血统溯源与联系图谱\n\n")
        f.write(f"- **目标平台**：{platform.upper()}\n")
        f.write(f"- **对应正文**：[{clean_file.name}](./{clean_file.name})\n")
        f.write(f"- **文章主题**：{topic_display}\n")
        f.write(f"- **采用心流组合**：`{flow_combo}`\n")
        f.write(f"- **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("### 1. 📊 创作者选定心流联系图谱 (Mermaid)\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        f.write("    subgraph 创作者选定心流组合 [" + flow_combo + " 心流搭配]\n")
        f.write("        Step1[\"1. Hook: 破除大众盲区 / 痛点共鸣\"]\n")
        f.write("        Step2[\"2. Inversion: 认知反转 / 底层归因\"]\n")
        f.write("        Step3[\"3. Action: 极简解法 / 微习惯\"]\n")
        f.write("        Step4[\"4. Ending: 灵魂收尾 / 温暖托举\"]\n")
        f.write("    end\n\n")
        f.write("    subgraph 原著知识血统 [原著核心血统]\n")
        f.write(f"        C1[\"原章节: [[{source_chapter_name}]]\"]\n")
        f.write(f"        M1[\"思维模型: [[{concept_sample}]]\"]\n")
        f.write(f"        Q1[\"核心原文: '{quote_sample[:15]}...'\"]\n")
        f.write("    end\n\n")
        f.write("    C1 --> M1\n")
        f.write("    M1 --> Step2\n")
        f.write("    C1 --> Q1\n")
        f.write("    Step1 --> Step2\n")
        f.write("    Step2 --> Step3\n")
        f.write("    Step3 --> Step4\n")
        f.write("    Q1 --> Step4\n")
        f.write("```\n\n")
        f.write("### 2. 📋 核心要素血统溯源表\n\n")
        f.write("| 文章模块 / 关键文案 | 原著章节与出处 | insights 原料卡映射 | 创作者意图与心理学设计 |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| **标题 / Hook** | 《{book_title}》{source_chapter_name} | `00_全书爆款选题与反直觉库.md` | **打破认知防御**：用常见生活误区制造反差好奇 |\n")
        f.write(f"| **痛点唤醒** | 原书关于【{topic_display}】的论述 | `00_读者现实痛点与对号入座索引.md` | **建立同盟共情**：描摹具体疲惫场景，消除说教感 |\n")
        f.write(f"| **认知反转** | 原书核心概念模型推演 | `00_全书核心概念与思维模型图谱.md` | **提供新解释框架**：将个人内疚归因于认知模型缺陷 |\n")
        f.write(f"| **行动指南** | 原书中的行为原则落地 | 对应章节原料卡第 3 节 (微清单) | **促成收藏与执行**：给低阻力、今天下班就能做的一件事 |\n")
        f.write(f"| **点睛金句** | 原书精选原文 | `00_全书高穿透金句大全.md` | **驱动转发与共鸣**：深夜治愈底色，让读者产生分享欲 |\n\n")
        f.write("### 3. 🧠 关联知识双链 (Obsidian Wikilinks)\n\n")
        f.write(f"- [[{concept_sample}]]\n")
        f.write(f"- [[{book_title}]]\n")
        
    print(f"✨ 成功生成语义化双文件：")
    print(f"   1. 纯净正文: {clean_file}")
    print(f"   2. 独立溯源: {prov_file}")
    return clean_file, prov_file


def main():
    parser = argparse.ArgumentParser(description="Book Distiller 读后感与心流共创生成器 (v3.0 创作者矩阵版)")
    parser.add_argument("book_dir", help="已提取章节的书籍目录")
    parser.add_argument(
        "--platform",
        choices=["xhs", "threads", "wechat", "menu_only"],
        default="xhs",
        help="目标平台: xhs(小红书), threads(Threads), wechat(公众号), menu_only(仅生成心流搭配菜单)"
    )
    parser.add_argument("--matrix", action="store_true", help="为整本书生成 4~6 篇书评创作矩阵规划表 (00_全书书评创作矩阵规划.md)")
    parser.add_argument("--combo", default="1B+2A+3A+4A", help="指定四段心流组合代号 (如 1A+2B+3A+4A)")
    parser.add_argument("--topic", help="探讨主题或痛点（会自动转换为语义化文件名 Slug）", default=None)
    parser.add_argument("--chapter", help="指定关联合并的章节文件名", default=None)
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    # 1. 若指定 --matrix，则生成全书创作矩阵规划表
    if args.matrix:
        generate_review_matrix(book_path)
        
    # 2. 生成四段心流自由搭配菜单
    menu_file = generate_flow_menu(book_path, topic=args.topic)
    
    if args.platform == "menu_only":
        print(f"\n🎉 心流菜单已就绪，可以在 {menu_file.name} 中挑选中意的心流组合！")
        return
        
    # 3. 生成语义化双文件
    create_dual_review_files(
        book_path,
        platform=args.platform,
        flow_combo=args.combo,
        topic=args.topic,
        chapter_file=args.chapter
    )
    print("\n🎉 全部文件生成完成！创作者可直接挑选心流积木进行微调。")


if __name__ == "__main__":
    main()
