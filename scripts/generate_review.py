#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Book Review Generator Helper (Sub-skill: book-review)
根据书籍拆解目录和 insights/ 黄金原料库，自动为不同社交平台（小红书、Threads、公众号）生成读后感草稿脚手架。
"""

import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


def load_templates() -> Dict[str, str]:
    """
    读取 subskills/book-review/templates/review-templates.md 中的模具定义
    """
    script_dir = Path(__file__).resolve().parent
    template_file = script_dir.parent / "subskills" / "book-review" / "templates" / "review-templates.md"
    
    templates = {
        "xhs": "",
        "threads": "",
        "wechat": ""
    }
    
    if not template_file.exists():
        return templates
        
    content = template_file.read_text(encoding="utf-8")
    
    # 拆分模具
    xhs_match = re.search(r"## 模具 A：小红书深度读后图文笔记.*?(?=## 模具 B：|\Z)", content, re.DOTALL)
    threads_match = re.search(r"## 模具 B：Threads / X 串帖读后感.*?(?=## 模具 C：|\Z)", content, re.DOTALL)
    wechat_match = re.search(r"## 模具 C：微信公众号 / 博客深度随笔书评.*?\Z", content, re.DOTALL)
    
    if xhs_match:
        templates["xhs"] = xhs_match.group(0).strip()
    if threads_match:
        templates["threads"] = threads_match.group(0).strip()
    if wechat_match:
        templates["wechat"] = wechat_match.group(0).strip()
        
    return templates


def collect_insights_material(book_dir: Path, topic_keyword: Optional[str] = None) -> Dict[str, List[str]]:
    """
    从 insights/ 目录下扫描并收集可用原料（反直觉选题、金句、痛点）
    """
    insights_dir = book_dir / "insights"
    materials = {
        "hooks": [],
        "quotes": [],
        "symptoms": [],
        "concepts": []
    }
    
    if not insights_dir.exists():
        return materials
        
    # 1. 扫描金句
    quotes_file = insights_dir / "00_全书高穿透金句大全.md"
    if quotes_file.exists():
        text = quotes_file.read_text(encoding="utf-8")
        # 提取引用行
        quotes = [line.strip("> ") for line in text.splitlines() if line.startswith("> ") and len(line) > 10]
        if topic_keyword:
            quotes = [q for q in quotes if topic_keyword in q] or quotes
        materials["quotes"] = quotes[:5]

    # 2. 扫描选题与反直觉
    hooks_file = insights_dir / "00_全书爆款选题与反直觉库.md"
    if hooks_file.exists():
        text = hooks_file.read_text(encoding="utf-8")
        # 寻找反直觉行
        hooks = [line.strip("- ") for line in text.splitlines() if "反直觉" in line or "打破" in line or line.startswith("- ⚡️")]
        materials["hooks"] = hooks[:5]
        
    # 3. 扫描痛点
    symptom_file = insights_dir / "00_读者现实痛点与对号入座索引.md"
    if symptom_file.exists():
        text = symptom_file.read_text(encoding="utf-8")
        symptoms = [line.strip("| ") for line in text.splitlines() if "|" in line and "现实痛点" not in line and "---" not in line]
        materials["symptoms"] = symptoms[:5]
        
    return materials


def create_review_draft(
    book_dir: Path,
    platform: str,
    topic: Optional[str] = None,
    chapter_file: Optional[str] = None
) -> Path:
    """
    在书籍目录下的 reviews/ 生成指定平台的读后感排版草稿
    """
    reviews_dir = book_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"review_{platform}_{timestamp}.md"
    target_path = reviews_dir / file_name
    
    book_title = book_dir.name
    templates = load_templates()
    materials = collect_insights_material(book_dir, topic_keyword=topic)
    
    topic_display = topic if topic else f"读《{book_title}》的顿悟时刻"
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(f"# ✍️ 《{book_title}》读后感草稿 ({platform.upper()})\n\n")
        f.write(f"- **目标平台**：{platform.upper()}\n")
        f.write(f"- **探讨主题**：{topic_display}\n")
        f.write(f"- **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if chapter_file:
            f.write(f"- **依托章节**：[{chapter_file}](../{chapter_file})\n")
        f.write("\n---\n\n")
        
        # 附上已扫描到的原料线索
        if any(materials.values()):
            f.write("## 💡 已调取的黄金原料储备\n\n")
            if materials["quotes"]:
                f.write("**推荐穿透金句：**\n")
                for q in materials["quotes"][:3]:
                    f.write(f"- > {q}\n")
                f.write("\n")
            if materials["hooks"]:
                f.write("**反直觉切入点 (Hook)：**\n")
                for h in materials["hooks"][:3]:
                    f.write(f"- {h}\n")
                f.write("\n")
            if materials["symptoms"]:
                f.write("**读者痛点投射：**\n")
                for s in materials["symptoms"][:3]:
                    f.write(f"- {s}\n")
                f.write("\n")
            f.write("---\n\n")
            
        f.write("## 📝 读后感正文排版（待 AI 润色 / 创作者填充）\n\n")
        
        # 植入对应模具
        if platform == "xhs":
            f.write(f"### [小红书标题建议]\n")
            f.write(f"读完《{book_title}》，我终于戒掉了那该死的内耗\n")
            f.write(f"原来真正厉害的人，早就悄悄换掉了这种底层思维\n\n")
            f.write("### [正文预览]\n")
            f.write("不知道你有没有过这样的时刻：\n")
            f.write("（在这里描述一个具象的生活或工作扎心场景……）\n\n")
            f.write("直到最近翻开《{book_title}》，书里这句话瞬间击中了我：\n")
            f.write("> 「……（填入书中最有力量的一句金句）」\n\n")
            f.write("今天挑出让我最醍醐灌顶的 3 个认知刷新，分享给你：\n\n")
            f.write("1️⃣ **顿悟点一：……**\n\n2️⃣ **顿悟点二：……**\n\n3️⃣ **顿悟点三：……**\n\n")
            f.write("🌿 **写在最后：**\n成长不是逼自己脱胎换骨，而是允许自己放下执念。\n\n")
            f.write("#读书笔记 #认知思维 #自我提升 #书单推荐\n")
            
        elif platform == "threads":
            f.write("### [Threads 4 帖心流]\n\n")
            f.write("#### 1/4【Hook 引子】\n")
            f.write(f"读完《{book_title}》，最大的感触其实只有一句话：\n")
            f.write("我们很多时候觉得痛苦，并不是因为不够努力，而是努力的方向从一开始就颠倒了。\n\n")
            f.write("#### 2/4【认知反转】\n")
            f.write("书中指出了一个极其反直觉的真相：\n")
            f.write("（阐述书中最核心的打破盲区的思维反转……）\n\n")
            f.write("#### 3/4【行动解法】\n")
            f.write("如果你也正陷在类似的消耗里，不妨试着做这一个最小改变：\n")
            f.write("（给出一个极低摩擦、今天下班就能做到的微行动……）\n\n")
            f.write("#### 4/4【温柔收尾】\n")
            f.write("生活不是一场需要向所有人交卷的考试。\n")
            f.write("放轻松一点，你已经在变好的路上了。\n")
            
        elif platform == "wechat":
            f.write(f"### [公众号深度随笔：{topic_display}]\n\n")
            f.write("文 / （你的名字）\n\n")
            f.write("前几天深夜整理书架的时候，重新翻开了《{book_title}》。\n\n")
            f.write("（第一部分：生活场景引入，描摹一种近期的普遍心理状态）\n\n")
            f.write("（第二部分：引入书中的核心概念，展开深度解构）\n\n")
            f.write("（第三部分：联系具体的现实人际或工作案例，剖析背后的阻抗）\n\n")
            f.write("（第四部分：温和收敛，给出心智层面的松绑视角）\n")
            
    print(f"✨ 成功生成 {platform.upper()} 读后感模具草稿！")
    print(f"📄 保存路径: {target_path}")
    return target_path


def main():
    parser = argparse.ArgumentParser(description="为电子书生成多平台（小红书/Threads/公众号）读后感脚手架")
    parser.add_argument("book_dir", help="已提取章节的书籍目录")
    parser.add_argument(
        "--platform",
        choices=["xhs", "threads", "wechat", "all"],
        default="all",
        help="目标平台: xhs(小红书), threads(Threads/X), wechat(微信公众号), all(全部)"
    )
    parser.add_argument("--topic", help="指定读后感探讨的主题或痛点关键字", default=None)
    parser.add_argument("--chapter", help="指定关联合并的章节文件名", default=None)
    
    args = parser.parse_args()
    book_path = Path(args.book_dir).resolve()
    
    if not book_path.exists() or not book_path.is_dir():
        print(f"错误: 找不到书籍目录 -> {book_path}", file=sys.stderr)
        sys.exit(1)
        
    platforms = ["xhs", "threads", "wechat"] if args.platform == "all" else [args.platform]
    
    print(f"📖 正在为 《{book_path.name}》 生成社交媒体读后感草稿...")
    for p in platforms:
        create_review_draft(book_path, platform=p, topic=args.topic, chapter_file=args.chapter)
        
    print("\n🎉 全部读后感草稿脚手架已就绪！可以命令 AI 结合原料库进行深度润色。")


if __name__ == "__main__":
    main()
