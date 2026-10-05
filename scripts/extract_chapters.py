#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB Chapter Extractor (v2.0)
将 EPUB 电子书按章节提取并切分为独立的 Markdown 文档。
支持：
- 多级目录嵌套模式 (--nested)
- YAML Frontmatter 元数据注入 (书名, 作者, 序号, 字数, 预估时长, 标签)
- 章节底部 上一章/下一章 翻页导航
- 抽取配图并重定向相对路径
- 自动生成 README.md 和 SUMMARY.md 索引目录
"""

import os
import sys
import re
import argparse
from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def sanitize_filename(name: str, max_length: int = 60) -> str:
    """清理文件名中的非法字符"""
    clean = re.sub(r'[\\/*?:"<>|#\n\r\t]', '', name)
    clean = clean.strip().replace(' ', '_')
    clean = re.sub(r'_+', '_', clean)
    if not clean:
        clean = "untitled"
    return clean[:max_length]

def calculate_stats(text: str) -> tuple[int, str]:
    """计算文本字数与预估阅读时间（中英文混排）"""
    # 统计汉字数
    cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 统计英文单词数
    non_cjk_words = len(re.findall(r'[a-zA-Z0-9_-]+', text))
    total_words = cjk_count + non_cjk_words
    
    # 预估时长：中文按 400字/分钟，英文按 200词/分钟 计算
    mins = max(1, round(total_words / 350))
    return total_words, f"{mins} min"

def extract_metadata(book: epub.EpubBook) -> dict:
    """提取图书元数据"""
    metadata = {
        "title": "未知书名",
        "creator": "未知作者",
        "language": "zh",
        "description": ""
    }
    
    titles = book.get_metadata('DC', 'title')
    if titles:
        metadata["title"] = titles[0][0]
        
    creators = book.get_metadata('DC', 'creator')
    if creators:
        metadata["creator"] = creators[0][0]
        
    languages = book.get_metadata('DC', 'language')
    if languages:
        metadata["language"] = languages[0][0]
        
    descriptions = book.get_metadata('DC', 'description')
    if descriptions:
        metadata["description"] = BeautifulSoup(descriptions[0][0], 'html.parser').get_text().strip()
        
    return metadata

def dump_images(book: epub.EpubBook, assets_dir: Path) -> dict:
    """提取书中所有图片，并返回 原文件名 -> assets 导出相对路径 映射表"""
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    img_map = {}
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_IMAGE:
            orig_name = Path(item.get_name()).name
            target_path = assets_dir / orig_name
            with open(target_path, "wb") as f:
                f.write(item.get_content())
            # 基础映射
            img_map[orig_name] = orig_name
            img_map[item.get_name()] = orig_name
            img_map[f"../Images/{orig_name}"] = orig_name
            img_map[f"Images/{orig_name}"] = orig_name
            img_map[f"../images/{orig_name}"] = orig_name
            img_map[f"images/{orig_name}"] = orig_name
            
    return img_map

def clean_html_and_extract_title(content: bytes) -> tuple[BeautifulSoup, str]:
    """清洗 HTML 并提取第一候选标题"""
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style', 'link', 'meta']):
        tag.decompose()
        
    chapter_title = ""
    for selector in ['h1', 'h2', 'title', '.chapter-title', '.title']:
        header = soup.select_one(selector)
        if header and header.get_text().strip():
            candidate = header.get_text().strip()
            if len(candidate) > 1 and not candidate.lower().startswith("table of contents"):
                chapter_title = candidate
                break
                
    return soup, chapter_title

def parse_toc_tree(toc, level=0, parent_title=""):
    """递归解析 EPUB 的 TOC 层级树"""
    tree = []
    for item in toc:
        if isinstance(item, tuple):
            # item 为 (Section, [subitems...])
            section, subitems = item
            sec_title = section.title.strip() if hasattr(section, 'title') else "Section"
            sec_href = section.href if hasattr(section, 'href') else ""
            tree.append({
                "title": sec_title,
                "href": sec_href.split('#')[0] if sec_href else "",
                "is_section": True,
                "children": parse_toc_tree(subitems, level + 1, sec_title)
            })
        elif hasattr(item, 'href'):
            # item 为 Link
            tree.append({
                "title": item.title.strip(),
                "href": item.href.split('#')[0] if item.href else "",
                "is_section": False,
                "children": []
            })
    return tree

def build_href_to_section_map(toc_tree, current_section=""):
    """建立 href 文件名 -> 所属分卷/分部(Section) 名称的映射"""
    mapping = {}
    for node in toc_tree:
        sec_name = current_section
        if node["is_section"]:
            sec_name = node["title"]
        if node["href"]:
            mapping[node["href"]] = sec_name
        if node["children"]:
            sub_map = build_href_to_section_map(node["children"], sec_name)
            mapping.update(sub_map)
    return mapping

def convert_to_markdown(soup: BeautifulSoup, img_map: dict, rel_assets_prefix: str) -> str:
    """替换图片相对链接并转换为 Markdown"""
    for img in soup.find_all('img'):
        src = img.get('src', '')
        src_name = Path(src).name
        if src_name in img_map:
            img['src'] = f"{rel_assets_prefix}{img_map[src_name]}"
        elif src in img_map:
            img['src'] = f"{rel_assets_prefix}{img_map[src]}"

    for svg_img in soup.find_all(['image', 'svg:image']):
        href = svg_img.get('xlink:href') or svg_img.get('href')
        if href:
            href_name = Path(href).name
            if href_name in img_map:
                new_img = soup.new_tag("img", src=f"{rel_assets_prefix}{img_map[href_name]}")
                svg_img.replace_with(new_img)

    text = md(
        str(soup),
        heading_style="ATX",
        bullets_style="-",
        strip=['script', 'style']
    )
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def parse_and_export(epub_path: str, output_dir: str, nested: bool = False, save_images: bool = True):
    """核心导出执行流程"""
    epub_file = Path(epub_path).resolve()
    if not epub_file.exists():
        print(f"错误: 找不到文件 {epub_path}", file=sys.stderr)
        sys.exit(1)
        
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "assets"
    
    print(f"📖 正在解析: {epub_file.name} ...")
    book = epub.read_epub(str(epub_file))
    
    # 1. 提取元数据
    metadata = extract_metadata(book)
    print(f"📌 书名: {metadata['title']}")
    print(f"👤 作者: {metadata['creator']}")
    print(f"🗂️  模式: {'多级目录嵌套模式 (Nested)' if nested else '标准单级平铺模式 (Flat)'}")
    
    # 2. 导出图片
    img_map = {}
    if save_images:
        print("🖼️  正在导出插图与封面...")
        img_map = dump_images(book, assets_dir)
        print(f"   已导出 {len(set(img_map.values()))} 个图片资源至 assets/")
        
    # 3. 解析 TOC 层级映射 (用于 --nested 模式分卷)
    toc_tree = parse_toc_tree(book.toc)
    href_to_section = build_href_to_section_map(toc_tree) if nested else {}
    
    # 4. 遍历阅读流 (Spine)
    print("✂️  正在提取与转换各章节...")
    raw_chapters = []
    
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
            
        item_href = item.get_name()
        soup, title_from_html = clean_html_and_extract_title(item.get_content())
        
        # 预先探测纯文本长度，过滤无意义空页
        plain_text = soup.get_text().strip()
        if len(plain_text) < 15 and not any(tag in str(soup) for tag in ['<img', 'src=']):
            continue
            
        section_name = href_to_section.get(item_href, "")
        raw_chapters.append({
            "item": item,
            "soup": soup,
            "title_from_html": title_from_html,
            "section_name": section_name,
            "item_href": item_href
        })
        
    total_chapters = len(raw_chapters)
    processed_articles = []
    
    # 构建安全 Tag 名称
    clean_tag = sanitize_filename(metadata['title']).lower().replace('_', '-')
    
    for idx, chap_info in enumerate(raw_chapters):
        soup = chap_info["soup"]
        title_from_html = chap_info["title_from_html"]
        section = chap_info["section_name"]
        
        title = title_from_html if title_from_html else f"Chapter_{idx:02d}"
        title = re.sub(r'\s+', ' ', title).strip()
        safe_title = sanitize_filename(title)
        
        # 确定文件存放子路径与相对 assets 前缀
        if nested and section:
            safe_section = sanitize_filename(section)
            target_folder = out_dir / safe_section
            target_folder.mkdir(parents=True, exist_ok=True)
            filename = f"{idx:02d}_{safe_title}.md"
            file_path = target_folder / filename
            rel_link = f"./{safe_section}/{filename}"
            rel_assets_prefix = "../assets/"
            rel_root_prefix = "../"
        else:
            filename = f"{idx:02d}_{safe_title}.md"
            file_path = out_dir / filename
            rel_link = f"./{filename}"
            rel_assets_prefix = "./assets/"
            rel_root_prefix = "./"
            
        markdown_body = convert_to_markdown(soup, img_map, rel_assets_prefix)
        word_count, read_time = calculate_stats(markdown_body)
        
        # 构造 YAML Frontmatter
        frontmatter = [
            "---",
            f"book: \"{metadata['title']}\"",
            f"author: \"{metadata['creator']}\"",
            f"chapter_index: {idx}",
            f"title: \"{title}\"",
            f"word_count: {word_count}",
            f"read_time: \"{read_time}\"",
            f"tags:",
            f"  - ebook",
            f"  - {clean_tag}",
            "---\n"
        ]
        
        processed_articles.append({
            "index": idx,
            "title": title,
            "file_path": file_path,
            "rel_link": rel_link,
            "rel_root_prefix": rel_root_prefix,
            "frontmatter": "\n".join(frontmatter),
            "markdown_body": markdown_body,
            "section": section
        })
        
    # 5. 写入各章节文件（附带 Frontmatter 与上一章/下一章翻页导航）
    for i, art in enumerate(processed_articles):
        nav_links = []
        root_pre = art["rel_root_prefix"]
        
        # 上一章
        if i > 0:
            prev_art = processed_articles[i - 1]
            # 计算从当前文章到上一章的相对路径
            prev_rel = prev_art["rel_link"].replace("./", root_pre)
            nav_links.append(f"⬅️ [上一章：{prev_art['title']}]({prev_rel})")
        else:
            nav_links.append("⬅️ [第一章]")
            
        # 目录
        nav_links.append(f"📑 [返回目录]({root_pre}README.md)")
        
        # 下一章
        if i + 1 < len(processed_articles):
            next_art = processed_articles[i + 1]
            next_rel = next_art["rel_link"].replace("./", root_pre)
            nav_links.append(f"➡️ [下一章：{next_art['title']}]({next_rel})")
        else:
            nav_links.append("➡️ [尾声]")
            
        nav_footer = f"\n\n---\n\n" + " | ".join(nav_links) + "\n"
        
        with open(art["file_path"], "w", encoding="utf-8") as f:
            f.write(art["frontmatter"] + "\n")
            if not art["markdown_body"].startswith("# "):
                f.write(f"# {art['title']}\n\n")
            f.write(art["markdown_body"])
            f.write(nav_footer)
            
    # 6. 生成 README.md 与 SUMMARY.md
    print("📝 生成全书目录索引与 GitBook SUMMARY...")
    readme_path = out_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# {metadata['title']}\n\n")
        f.write(f"- **作者**: {metadata['creator']}\n")
        f.write(f"- **语言**: {metadata['language']}\n")
        f.write(f"- **总章节数**: {len(processed_articles)}\n")
        if metadata['description']:
            f.write(f"- **简介**: {metadata['description']}\n")
        f.write("\n---\n\n## 📑 章节目录\n\n")
        
        current_sec = None
        for chap in processed_articles:
            if nested and chap["section"] and chap["section"] != current_sec:
                current_sec = chap["section"]
                f.write(f"\n### 📂 {current_sec}\n\n")
            f.write(f"- [{chap['index']:02d}. {chap['title']}]({chap['rel_link']})\n")
            
    summary_path = out_dir / "SUMMARY.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Summary\n\n")
        f.write(f"* [{metadata['title']}](README.md)\n")
        current_sec = None
        for chap in processed_articles:
            if nested and chap["section"] and chap["section"] != current_sec:
                current_sec = chap["section"]
                f.write(f"\n* **{current_sec}**\n")
            indent = "    " if (nested and chap["section"]) else "  "
            f.write(f"{indent}* [{chap['title']}]({chap['rel_link'].replace('./', '')})\n")
            
    print(f"\n🎉 提取完成！共输出 {len(processed_articles)} 个独立章节。")
    print(f"📂 输出目录: {out_dir}")
    print(f"📑 目录索引: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="将 EPUB 电子书按章节拆分导出为带元数据的 Markdown 文档 (v2.0)")
    parser.add_argument("input", help="EPUB 文件路径")
    parser.add_argument("-o", "--output", help="输出目录路径 (默认为当前目录/书名)", default=None)
    parser.add_argument("--nested", action="store_true", help="启用多级目录嵌套模式 (按卷/部创建子文件夹)")
    parser.add_argument("--no-images", action="store_true", help="不导出图片资源")
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"错误: 文件不存在 -> {input_file}", file=sys.stderr)
        sys.exit(1)
        
    if not args.output:
        output_dir = Path.cwd() / input_file.stem
    else:
        output_dir = Path(args.output)
        
    parse_and_export(str(input_file), str(output_dir), nested=args.nested, save_images=not args.no_images)

if __name__ == "__main__":
    main()
