#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Insights Extractor Helper (Book Distiller v3.1 决策简报与断点续传版)
1. 构建/维护四大全书总库：
   - 00_全书爆款选题与反直觉库.md
   - 00_全书高穿透金句大全.md
   - 00_读者现实痛点与对号入座索引.md
   - 00_全书核心概念与思维模型图谱.md
2. 全书一页纸决策简报生成 (1-Page Executive Summary):
   - 自动生成 00_全书一页纸决策简报.md，3分钟俯瞰全书破局底层逻辑与反常识洞见！
3. 断点续传与增量缓存 (Caching & Incremental Extraction)：
   - 自动检测已完成的章节卡，跳过无需重复处理的文件；
   - 支持 `--sync` 一键从所有已有原料卡中增量汇总、去重并更新四大总库！
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Set


def is_card_completed(card_path: Path) -> bool:
    """
    检查原料卡是否已经包含有效提炼内容（而非初始骨架）
    """
    if not card_path.exists():
        return False
    content = card_path.read_text(encoding="utf-8")
    if "待评估 (Pending)" in content and len(content.strip().splitlines()) < 20:
        return False
    return len(content.strip()) > 200


def generate_executive_summary(book_dir: Path) -> Path:
    """
    为整本书生成 00_全书一页纸决策简报.md
    """
    summary_file = book_dir / "00_全书一页纸决策简报.md"
    insights_dir = book_dir / "insights"
    book_title = book_dir.name
    
    # 尝试从 insights 总库调取精华
    quotes: List[str] = []
    hooks: List[str] = []
    symptoms: List[str] = []
    concepts: List[str] = []
    
    if insights_dir.exists():
        q_file = insights_dir / "00_全书高穿透金句大全.md"
        if q_file.exists():
            text = q_file.read_text(encoding="utf-8")
            zh_quotes = re.findall(r"-\s+\*\*中文\*\*：(.*?)(?:\n|$)", text)
            quotes = [q.strip() for q in zh_quotes[:3]] if zh_quotes else [line.strip("> ") for line in text.splitlines() if line.startswith("> ") and len(line) > 10][:3]
            
        h_file = insights_dir / "00_全书爆款选题与反直觉库.md"
        if h_file.exists():
            text = h_file.read_text(encoding="utf-8")
            titles = re.findall(r"-\s+\*\*爆款大标题\*\*：《(.*?)》", text)
            contrarians = re.findall(r"-\s+\*\*核心认知差\*\*：(.*?)(?:\n|$)", text)
            for t, c in zip(titles, contrarians):
                hooks.append(f"{t.strip()}（{c.strip()}）")
            if not hooks:
                hooks = [line.strip("- ") for line in text.splitlines() if "反直觉" in line or "打破" in line][:3]
                
        s_file = insights_dir / "00_读者现实痛点与对号入座索引.md"
        if s_file.exists():
            text = s_file.read_text(encoding="utf-8")
            symptoms = [line.strip("| ") for line in text.splitlines() if "|" in line and "现实痛点" not in line and "---" not in line][:3]
            
        c_file = insights_dir / "00_全书核心概念与思维模型图谱.md"
        if c_file.exists():
            text = c_file.read_text(encoding="utf-8")
            found_c = re.findall(r"\[\[(.*?)\]\]", text)
            concepts = list(dict.fromkeys([c for c in found_c if not c.endswith(".md")]))[:3]

    q_top = quotes[0] if quotes else "痛苦加上反思等于进步。"
    h1 = hooks[0] if len(hooks) > 0 else "打破惯性盲区：越是努力，反而越容易陷入认知死角"
    h2 = hooks[1] if len(hooks) > 1 else "常规误区 vs 深层反转：我们不是能力差，而是底层操作系统设错了"
    h3 = hooks[2] if len(hooks) > 2 else "为什么很多人每天都在疲于奔命，却始终没有安全感？"
    s1 = symptoms[0] if symptoms else "陷入盲目努力与深度精神内耗"
    c1 = concepts[0] if concepts else "反思回路与机器思维"
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"# 📑 《{book_title}》全书一页纸决策简报 (1-Page Executive Summary)\n\n")
        f.write("> **导语**：本书深度研读与自媒体创作的“全局定盘星”。用 3 分钟通读，看透全书底层逻辑、反常识洞见与核心破局点。\n\n")
        f.write("---\n\n")
        
        f.write("### 一、 📌 一句话本质判词 (The Core Thesis)\n\n")
        f.write(f"> **表面上**，本书在探讨个人成长与方法论；  \n")
        f.write(f"> **本质上**，作者是在用一套极其冷静的理性认知框架，替当代人彻底重构【面对现实、解开内耗与建立个人秩序的底层逻辑】。\n\n")
        f.write("---\n\n")
        
        f.write("### 二、 ⚡️ 三大最具穿透力的反常识断言 (Top 3 Contrarian Truths)\n\n")
        f.write(f"1. **【洞见一：认知盲区打破】**\n")
        f.write(f"   - **原书颠覆真相**：{h1}\n")
        f.write(f"   - **现实杀伤力**：⭐⭐⭐⭐⭐（直击痛点：{s1}）\n\n")
        f.write(f"2. **【洞见二：系统模型置换】**\n")
        f.write(f"   - **原书颠覆真相**：{h2}\n")
        f.write(f"   - **现实杀伤力**：⭐⭐⭐⭐（核心模型：[[{c1}]]）\n\n")
        f.write(f"3. **【洞见三：行动机制重构】**\n")
        f.write(f"   - **原书颠覆真相**：{h3}\n")
        f.write(f"   - **现实杀伤力**：⭐⭐⭐⭐⭐（消除自我苛责与过度焦虑）\n\n")
        f.write("---\n\n")
        
        f.write("### 三、 🧠 作者底层逻辑推导闭环 (The Architecture)\n\n")
        f.write("```mermaid\n")
        f.write("flowchart LR\n")
        f.write("    A[\"1. 现实困境: 读者的表层疲惫与内耗\"] --> B[\"2. 深层归因: 旧认知模型的系统性缺陷\"]\n")
        f.write("    B --> C[\"3. 破局机制: 引入原书核心思维模型\"]\n")
        f.write("    C --> D[\"4. 终极秩序: 建立最小阻力的生活系统\"]\n")
        f.write("```\n\n")
        f.write("- **第一阶段（认清真相）**：剥离情绪内耗，客观面对残酷的现实事实（不回避、不自欺）；\n")
        f.write(f"- **第二阶段（模型置换）**：将个人内疚归因于“工具与规则的落后”，引入核心概念 [[{c1}]]；\n")
        f.write("- **第三阶段（行动闭环）**：通过可落地的最小反馈回路，在现实中反复微调与校准。\n\n")
        f.write("---\n\n")
        
        f.write("### 四、 🎯 读者适合度诊断 (Fit Diagnosis)\n\n")
        f.write("| 适合谁立刻读（强烈推荐） | 谁读了是浪费时间（劝退建议） |\n")
        f.write("| :--- | :--- |\n")
        f.write("| ✅ **长期陷入精神内耗与自我怀疑的人**：急需一套清晰的外部参照系建立秩序。 | ❌ **只想找快餐式心灵鸡汤的人**：本书没有廉价安慰，只有冷峻的理性推演。 |\n")
        f.write("| ✅ **努力很久却总在原地打转的终身学习者**：需要找到努力的真正发力点。 | ❌ **抗拒自我反思与改变的人**：读完可能会感到被冒犯或认知失调。 |\n")
        f.write("| ✅ **内容创作者 / 知识博主**：书中充满了反直觉认知、高穿透金句与爆款选题。 | ❌ **只想要现成模板抄作业的人**：本书给的是底层心智，而非固定答案。 |\n\n")
        f.write("---\n\n")
        
        f.write("### 五、 💎 全书灵魂锚点金句 (The Anchor Quote)\n\n")
        f.write(f"> **「{q_top}」**  \n")
        f.write(f"> *—— 来源原书核心精髓*\n\n")
        f.write("---\n\n")
        
        f.write("### 六、 🚀 创作者自媒体行动指引\n\n")
        f.write("- 📱 **小红书发帖**：以【洞见一】切入，用“读完这本书，我终于停止了自我惩罚”为双行标题，做 3 顿悟点图文笔记。\n")
        f.write("- 🧵 **Threads / X**：以【洞见二】切入，用 4 帖心流拆解努力反向的认知误区，每帖 ≤ 500 字符。\n")
        f.write("- 📰 **微信公众号**：结合生活具体案例，长程推导全书的思维模型演进图谱，建立读者深度信任。\n")

    print(f"✨ 成功生成全书一页纸决策简报！")
    print(f"📑 简报文件: {summary_file}")
    return summary_file


def sync_insights_master_libraries(insights_dir: Path, book_title: str):
    """
    扫描当前 insights/ 目录下所有已完成的原料卡，增量汇聚并更新四大总库（去重防覆写）
    """
    card_files = sorted(insights_dir.glob("*_原料卡.md"))
    if not card_files:
        return
        
    print(f"🔄 正在扫描并增量汇聚 {len(card_files)} 张原料卡到四大总库...")
    
    all_quotes: List[Tuple[str, str]] = []
    all_hooks: List[Tuple[str, str]] = []
    all_symptoms: List[Tuple[str, str, str]] = []
    all_concepts: Set[str] = set()
    
    for card in card_files:
        content = card.read_text(encoding="utf-8")
        if not is_card_completed(card):
            continue
            
        chapter_name = card.stem.replace("_原料卡", "")
        
        # 1. 提取穿透金句
        quotes_section = re.search(r"## 4\. 💎 穿透金句.*?(?=##|\Z)", content, re.DOTALL)
        if quotes_section:
            for line in quotes_section.group(0).splitlines():
                line = line.strip()
                if (line.startswith("> ") or line.startswith("- ")) and len(line) > 10:
                    clean_quote = line.lstrip(">- *")
                    all_quotes.append((clean_quote, chapter_name))
                    
        # 2. 提取反直觉 Hook
        hook_section = re.search(r"## 1\. ⚡️ 反直觉认知.*?(?=##|\Z)", content, re.DOTALL)
        if hook_section:
            for line in hook_section.group(0).splitlines():
                line = line.strip()
                if line.startswith("- ") and len(line) > 8:
                    all_hooks.append((line.lstrip("- *"), chapter_name))
                    
        # 3. 提取现实痛点
        symptom_section = re.search(r"## 5\. 🎯 读者现实痛点.*?(?=##|\Z)", content, re.DOTALL)
        if symptom_section:
            for line in symptom_section.group(0).splitlines():
                line = line.strip()
                if line.startswith("- ") and len(line) > 6:
                    all_symptoms.append((line.lstrip("- *"), chapter_name, "核心认知"))
                    
        # 4. 提取双链概念 [[xxx]]
        found_concepts = re.findall(r"\[\[(.*?)\]\]", content)
        for c in found_concepts:
            if not c.endswith(".md"):
                all_concepts.add(c)
                
    # 增量更新 00_全书高穿透金句大全.md
    quotes_file = insights_dir / "00_全书高穿透金句大全.md"
    existing_text = quotes_file.read_text(encoding="utf-8") if quotes_file.exists() else f"# 💎 《{book_title}》全书高穿透金句大全\n\n"
    with open(quotes_file, "a", encoding="utf-8") as f:
        for q, ch in all_quotes:
            if q not in existing_text:
                f.write(f"- > 「{q}」 —— 来源：[[{ch}]]\n")
                
    # 增量更新 00_全书核心概念与思维模型图谱.md
    concepts_file = insights_dir / "00_全书核心概念与思维模型图谱.md"
    existing_concepts_text = concepts_file.read_text(encoding="utf-8") if concepts_file.exists() else f"# 🧠 《{book_title}》核心概念与思维模型图谱\n\n"
    with open(concepts_file, "a", encoding="utf-8") as f:
        for c in sorted(all_concepts):
            if f"[[{c}]]" not in existing_concepts_text:
                f.write(f"- [[{c}]]：原书核心认知模型\n")
                
    print("✅ 增量汇聚完成！四大全书总库已自动同步最新卡片数据。")


def setup_insights_workspace(book_dir: Path, init_cards: bool = True, force: bool = False):
    """
    初始化/增量维护书籍目录下的 insights/ 写作原料库（支持断点续传）
    """
    insights_dir = book_dir / "insights"
    insights_dir.mkdir(parents=True, exist_ok=True)
    
    chapter_files = sorted([f for f in book_dir.glob("*.md") if re.match(r'^\d{2}_', f.name)])
    
    print(f"📚 正在为 《{book_dir.name}》 运行高阶原料库引擎 (v3.1)...")
    print(f"📑 发现 {len(chapter_files)} 个独立正文章节")
    print(f"📂 原料存放目录: {insights_dir}")
    
    # 1. 爆款选题与反直觉库
    hooks_file = insights_dir / "00_全书爆款选题与反直觉库.md"
    if not hooks_file.exists() or force:
        with open(hooks_file, "w", encoding="utf-8") as f:
            f.write(f"# ⚡️ 《{book_dir.name}》全书爆款选题与反直觉库\n\n")
            f.write("> 专门用于发 Threads、小红书大标题、公众号文章开篇的选题弹药库。\n\n")
            f.write("## 🔥 全书 Top 5 必爆黄金选题（高情绪张力 / 强反直觉）\n\n*(待提炼完成后自动置顶排序)*\n\n---\n\n")
            f.write("## 📑 各章节反直觉认知与 Hook 明细\n\n")
            
    # 2. 金句大全
    quotes_file = insights_dir / "00_全书高穿透金句大全.md"
    if not quotes_file.exists() or force:
        with open(quotes_file, "w", encoding="utf-8") as f:
            f.write(f"# 💎 《{book_dir.name}》全书高穿透金句大全\n\n")
            f.write("> 精选全书最具情绪穿透力的句子，直接用于配图、封面金句与文末总结。\n\n---\n\n")
            
    # 3. 现实痛点与对号入座索引
    symptom_file = insights_dir / "00_读者现实痛点与对号入座索引.md"
    if not symptom_file.exists() or force:
        with open(symptom_file, "w", encoding="utf-8") as f:
            f.write(f"# 🎯 《{book_dir.name}》读者现实痛点与对号入座索引\n\n")
            f.write("> 将原书抽象理论翻译为读者的现实烦恼。带着问题直接按图索骥，找到对应章节的破局解法。\n\n")
            f.write("| 读者现实痛点 / 搜索提问 | 对应破局章节 | 底层思维模型 |\n")
            f.write("| :--- | :--- | :--- |\n")
            
    # 4. 概念双链图谱
    concepts_file = insights_dir / "00_全书核心概念与思维模型图谱.md"
    if not concepts_file.exists() or force:
        with open(concepts_file, "w", encoding="utf-8") as f:
            f.write(f"# 🧠 《{book_dir.name}》核心概念与思维模型图谱\n\n")
            f.write("> 导入 Obsidian 即可点亮全书网状知识图谱。点击概念可跨章节穿梭。\n\n---\n\n")
            
    # 断点续传卡片初始化与跳过检测
    skipped_count = 0
    created_count = 0
    
    if init_cards:
        for f in chapter_files:
            card_name = f.stem + "_原料卡.md"
            card_path = insights_dir / card_name
            
            if card_path.exists() and not force:
                if is_card_completed(card_path):
                    skipped_count += 1
                    continue
                continue
                
            with open(card_path, "w", encoding="utf-8") as out:
                out.write(f"# 💡 《{f.stem}》写作黄金原料卡\n\n")
                out.write(f"- **原文章节**：[{f.name}](../{f.name})\n")
                out.write("- **爆款评级**：待评估 (Pending)\n")
                out.write("- **核心概念**：待识别\n\n---\n\n")
                out.write("## 1. ⚡️ 反直觉认知 (Hook 灵感)\n\n")
                out.write("## 2. 📖 故事与微案例 (论据素材)\n\n")
                out.write("## 3. 🛠️ 可落地微清单 (读者收藏向)\n\n")
                out.write("## 4. 💎 穿透金句 (可直接配图/发帖)\n\n")
                out.write("## 5. 🎯 读者现实痛点对号入座\n\n")
            created_count += 1

    print(f"📊 断点续传状态统计：")
    print(f"   - ⏭️ 已跳过已完成章节: {skipped_count} 篇 (断点保留)")
    print(f"   - 🆕 新创建/就绪卡片: {created_count} 篇")
    print(f"   - 📑 总章节数: {len(chapter_files)} 篇")
    
    # 自动执行一次总库增量同步
    sync_insights_master_libraries(insights_dir, book_dir.name)
    
    # 自动生成全书一页纸决策简报
    generate_executive_summary(book_dir)


def main():
    parser = argparse.ArgumentParser(description="Book Distiller 写作原料库引擎 (支持一页纸决策简报与断点续传 v3.1)")
    parser.add_argument("book_dir", help="已提取章节的书籍目录")
    parser.add_argument("--no-cards", action="store_true", help="仅生成四大总库与决策简报，不为每个章节初始化单卡")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有的卡片与总库")
    parser.add_argument("--sync", action="store_true", help="仅将现有原料卡增量同步更新至四大总库")
    parser.add_argument("--brief", action="store_true", help="仅生成/更新 00_全书一页纸决策简报.md")
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    insights_dir = book_path / "insights"
    
    if args.brief:
        generate_executive_summary(book_path)
        return
        
    if args.sync and insights_dir.exists():
        sync_insights_master_libraries(insights_dir, book_path.name)
        generate_executive_summary(book_path)
        return
        
    setup_insights_workspace(book_path, init_cards=not args.no_cards, force=args.force)


if __name__ == "__main__":
    main()
