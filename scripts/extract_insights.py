#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Insights Extractor Helper (Batch Mode)
支持为全书章节批量构建原料卡文件骨架，汇总全书 Hooks 与 Quotes，并支持 Agent 批量提炼流水线。
"""

import os
import sys
import re
import argparse
from pathlib import Path

def setup_insights_workspace(book_dir: Path, init_cards: bool = True):
    """在书籍目录下创建专门的 insights/ 写作原料库，并为每个章节初始化原料卡"""
    insights_dir = book_dir / "insights"
    insights_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有章节 markdown 文件 (以数字开头)
    chapter_files = sorted([f for f in book_dir.glob("*.md") if re.match(r'^\d{2}_', f.name)])
    
    print(f"📚 正在为 《{book_dir.name}》 构建全书写作原料库...")
    print(f"📑 发现 {len(chapter_files)} 个独立正文章节")
    print(f"📂 原料存放目录: {insights_dir}")
    
    # 初始化全书汇总清单
    hooks_file = insights_dir / "00_全书爆款选题与反直觉库.md"
    quotes_file = insights_dir / "00_全书高穿透金句大全.md"
    
    if not hooks_file.exists():
        with open(hooks_file, "w", encoding="utf-8") as f:
            f.write(f"# ⚡️ 《{book_dir.name}》全书反直觉认知与 Hook 灵感库\n\n")
            f.write("> 随时翻看本文件，直接作为自媒体发帖、写长文的选题灵感。\n\n---\n\n")
            
    if not quotes_file.exists():
        with open(quotes_file, "w", encoding="utf-8") as f:
            f.write(f"# 💎 《{book_dir.name}》全书穿透金句大全\n\n")
            f.write("> 精选全书最具情绪共鸣与穿透力的句子，直接用于图卡、引言与文末金句。\n\n---\n\n")
            
    # 为每个章节初始化对应的原料卡文件
    card_list = []
    if init_cards:
        for f in chapter_files:
            card_name = f.stem + "_原料卡.md"
            card_path = insights_dir / card_name
            card_list.append(card_path)
            if not card_path.exists():
                with open(card_path, "w", encoding="utf-8") as out:
                    out.write(f"# 💡 《{f.stem}》写作黄金原料卡\n\n")
                    out.write(f"- **原文章节**：[{f.name}](../{f.name})\n")
                    out.write("- **状态**：待提炼 / Ready for Extraction\n\n---\n\n")
                    out.write("## 1. ⚡️ 反直觉认知 (Hook 灵感)\n\n")
                    out.write("## 2. 📖 故事与微案例 (论据素材)\n\n")
                    out.write("## 3. 🛠️ 可落地微清单 (读者收藏向)\n\n")
                    out.write("## 4. 💎 穿透金句 (可直接配图/发帖)\n\n")

    print(f"✅ 全书原料库搭建完毕！共创建/关联了 {len(chapter_files)} 张章节原料卡。")
    print(f"💡 接下来你可以直接指示 AI：'批量提取全书所有章节的黄金原料'，AI 将自动通读每章并将 4 类素材填满对应的卡片和总库！")

def main():
    parser = argparse.ArgumentParser(description="为 epub-to-markdown 目录批量初始化或处理全书写作黄金原料库")
    parser.add_argument("book_dir", help="已提取的书籍目录路径")
    parser.add_argument("--no-cards", action="store_true", help="仅生成汇总清单，不为每个章节初始化单卡")
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    setup_insights_workspace(book_path, init_cards=not args.no_cards)

if __name__ == "__main__":
    main()
