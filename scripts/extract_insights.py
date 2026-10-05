#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter Insights Extractor Helper
为 epub-to-markdown 解包出的章节文件搭建原料库目录骨架，支持单章提炼与全书洞察汇总。
"""

import os
import sys
import re
import argparse
from pathlib import Path

def setup_insights_workspace(book_dir: Path):
    """在书籍目录下创建专门的 insights/ 写作原料库"""
    insights_dir = book_dir / "insights"
    insights_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有章节 markdown 文件 (以数字开头)
    chapter_files = sorted([f for f in book_dir.glob("*.md") if re.match(r'^\d{2}_', f.name)])
    
    print(f"📚 正在为 《{book_dir.name}》 构建写作原料库...")
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
            
    print(f"✅ 原料库骨架搭建完毕！")
    print(f"💡 你可以直接在聊天中告诉我：'提取 [章节名] 的黄金原料'，AI 将自动深度提炼并收录至此。")

def main():
    parser = argparse.ArgumentParser(description="为 epub-to-markdown 目录初始化写作黄金原料库")
    parser.add_argument("book_dir", help="已提取的书籍目录路径")
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    setup_insights_workspace(book_path)

if __name__ == "__main__":
    main()
