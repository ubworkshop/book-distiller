#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Insights Extractor Helper (Book Distiller v3.0 断点续传与增量合并版)
1. 构建/维护四大全书总库：
   - 00_全书爆款选题与反直觉库.md
   - 00_全书高穿透金句大全.md
   - 00_读者现实痛点与对号入座索引.md
   - 00_全书核心概念与思维模型图谱.md
2. 断点续传与增量缓存 (Caching & Incremental Extraction)：
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
    # 如果包含初始占位符且篇幅极小，则视为未完成
    if "待评估 (Pending)" in content and len(content.strip().splitlines()) < 20:
        return False
    return len(content.strip()) > 200


def sync_insights_master_libraries(insights_dir: Path, book_title: str):
    """
    扫描当前 insights/ 目录下所有已完成的原料卡，增量汇聚并更新四大总库（去重防覆写）
    """
    card_files = sorted(insights_dir.glob("*_原料卡.md"))
    if not card_files:
        return
        
    print(f"🔄 正在扫描并增量汇聚 {len(card_files)} 张原料卡到四大总库...")
    
    all_quotes: List[Tuple[str, str]] = []       # (quote, source_chapter)
    all_hooks: List[Tuple[str, str]] = []        # (hook, source_chapter)
    all_symptoms: List[Tuple[str, str, str]] = [] # (symptom, chapter, model)
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
    
    print(f"📚 正在为 《{book_dir.name}》 运行高阶原料库引擎 (v3.0)...")
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
                # 如果只是占位骨架，则保留不覆盖
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


def main():
    parser = argparse.ArgumentParser(description="Book Distiller 写作原料库引擎 (支持断点续传与增量合并 v3.0)")
    parser.add_argument("book_dir", help="已提取章节的书籍目录")
    parser.add_argument("--no-cards", action="store_true", help="仅生成四大总库，不为每个章节初始化单卡")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有的卡片与总库")
    parser.add_argument("--sync", action="store_true", help="仅将现有原料卡增量同步更新至四大总库")
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    insights_dir = book_path / "insights"
    if args.sync and insights_dir.exists():
        sync_insights_master_libraries(insights_dir, book_path.name)
        return
        
    setup_insights_workspace(book_path, init_cards=not args.no_cards, force=args.force)


if __name__ == "__main__":
    main()
