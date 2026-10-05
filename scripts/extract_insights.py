#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Insights Extractor Helper (v2.5 高级创作版)
构建四大全书总库：
1. 00_全书爆款选题与反直觉库.md (含 🔥Top 5 必爆选题置顶)
2. 00_全书高穿透金句大全.md (带社交发帖语境)
3. 00_读者现实痛点与对号入座索引.md (现实烦恼 -> 章节原料映射)
4. 00_全书核心概念与思维模型图谱.md (Obsidian [[概念双链]])
"""

import os
import sys
import re
import argparse
from pathlib import Path

def setup_insights_workspace(book_dir: Path, init_cards: bool = True):
    """在书籍目录下创建专门的 insights/ 写作原料库，并初始化四大全书总库与章节原料卡"""
    insights_dir = book_dir / "insights"
    insights_dir.mkdir(parents=True, exist_ok=True)
    
    chapter_files = sorted([f for f in book_dir.glob("*.md") if re.match(r'^\d{2}_', f.name)])
    
    print(f"📚 正在为 《{book_dir.name}》 构建高阶写作原料库 (v2.5)...")
    print(f"📑 发现 {len(chapter_files)} 个独立正文章节")
    print(f"📂 原料存放目录: {insights_dir}")
    
    # 1. 爆款选题与反直觉库 (带评分)
    hooks_file = insights_dir / "00_全书爆款选题与反直觉库.md"
    if not hooks_file.exists():
        with open(hooks_file, "w", encoding="utf-8") as f:
            f.write(f"# ⚡️ 《{book_dir.name}》全书爆款选题与反直觉库\n\n")
            f.write("> 专门用于发 Threads、小红书大标题、公众号文章开篇的选题弹药库。\n\n")
            f.write("## 🔥 全书 Top 5 必爆黄金选题（高情绪张力 / 强反直觉）\n\n*(待提炼完成后自动置顶排序)*\n\n---\n\n")
            f.write("## 📑 各章节反直觉认知与 Hook 明细\n\n")
            
    # 2. 金句大全
    quotes_file = insights_dir / "00_全书高穿透金句大全.md"
    if not quotes_file.exists():
        with open(quotes_file, "w", encoding="utf-8") as f:
            f.write(f"# 💎 《{book_dir.name}》全书高穿透金句大全\n\n")
            f.write("> 精选全书最具情绪穿透力的句子，直接用于配图、封面金句与文末总结。\n\n---\n\n")
            
    # 3. 现实痛点与对号入座索引
    symptom_file = insights_dir / "00_读者现实痛点与对号入座索引.md"
    if not symptom_file.exists():
        with open(symptom_file, "w", encoding="utf-8") as f:
            f.write(f"# 🎯 《{book_dir.name}》读者现实痛点与对号入座索引\n\n")
            f.write("> 将原书抽象理论翻译为读者的现实烦恼。带着问题直接按图索骥，找到对应章节的破局解法。\n\n")
            f.write("| 读者现实痛点 / 搜索提问 | 对应破局章节 | 底层思维模型 |\n")
            f.write("| :--- | :--- | :--- |\n")
            
    # 4. 概念双链图谱
    concepts_file = insights_dir / "00_全书核心概念与思维模型图谱.md"
    if not concepts_file.exists():
        with open(concepts_file, "w", encoding="utf-8") as f:
            f.write(f"# 🧠 《{book_dir.name}》核心概念与思维模型图谱\n\n")
            f.write("> 导入 Obsidian 即可点亮全书网状知识图谱。点击概念可跨章节穿梭。\n\n---\n\n")
            
    # 为每个章节初始化原料卡
    if init_cards:
        for f in chapter_files:
            card_name = f.stem + "_原料卡.md"
            card_path = insights_dir / card_name
            if not card_path.exists():
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

    print(f"✅ 全书四大总库搭建完毕！")
    print(f"   1. ⚡️ 00_全书爆款选题与反直觉库.md (含 🔥Top 5 置顶)")
    print(f"   2. 💎 00_全书高穿透金句大全.md")
    print(f"   3. 🎯 00_读者现实痛点与对号入座索引.md")
    print(f"   4. 🧠 00_全书核心概念与思维模型图谱.md (Obsidian 双链)")
    print(f"💡 现在只要吩咐 AI 批量提取，AI 就会自动填充每张卡片并汇聚这四大总库！")

def main():
    parser = argparse.ArgumentParser(description="为 epub-to-markdown 目录初始化四大高阶写作原料总库 (v2.5)")
    parser.add_argument("book_dir", help="已提取的书籍目录路径")
    parser.add_argument("--no-cards", action="store_true", help="仅生成四大总库，不为每个章节初始化单卡")
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    setup_insights_workspace(book_path, init_cards=not args.no_cards)

if __name__ == "__main__":
    main()
