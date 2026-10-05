#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB Chapter Extractor (v2.1 智能纯净版)
将 EPUB 电子书按章节精确提取并切分为独立的 Markdown 文档。
新增：
- 智能出版冗余过滤：自动剔除纯版权声明、出版社广告、重复目录、空扉页与残注页。
- 复合副标题自动合并：将 "Chapter 1" 与 "Leverage" 智能拼合为 "Chapter 1: Leverage"。
- 文本深度洁癖净化：清除 xml version 残留及 xhtml 内部跳转失效锚点。
- 连续顺次重排编号：过滤后章节重新按 01, 02... 连续命名，杜绝断号与跳号。
- 支持多级目录嵌套模式 (--nested) 与 YAML Frontmatter 元数据注入。
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
    cjk_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    non_cjk_words = len(re.findall(r'[a-zA-Z0-9_-]+', text))
    total_words = cjk_count + non_cjk_words
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
            img_map[orig_name] = orig_name
            img_map[item.get_name()] = orig_name
            img_map[f"../Images/{orig_name}"] = orig_name
            img_map[f"Images/{orig_name}"] = orig_name
            img_map[f"../images/{orig_name}"] = orig_name
            img_map[f"images/{orig_name}"] = orig_name
    return img_map

def clean_html_and_extract_title(content: bytes) -> tuple[BeautifulSoup, str]:
    """清洗 HTML 并智能提取标题与副标题"""
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style', 'link', 'meta']):
        tag.decompose()
        
    headers = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'title']):
        txt = tag.get_text().strip()
        if txt and len(txt) > 1 and not txt.lower().startswith("table of contents"):
            headers.append(txt)
            
    chapter_title = ""
    if len(headers) >= 2:
        h0, h1 = headers[0], headers[1]
        # 如果 h0 是 "Chapter 1", h1 是 "Leverage" -> 合并为 "Chapter 1: Leverage"
        if re.match(r'^(Chapter|Part|Section|第[0-9一二三四五六七八九十]+章)\s*\d*$', h0, re.I):
            chapter_title = f"{h0}: {h1}"
        elif len(h0) < 30 and len(h1) < 40 and not re.search(r'(contents|copyright)', h0, re.I):
            chapter_title = f"{h0} - {h1}"
        else:
            chapter_title = h0
    elif len(headers) == 1:
        chapter_title = headers[0]
        
    if not chapter_title:
        # 尝试 class 中带有 title 的标签
        for selector in ['.chapter-title', '.title', '.chapter', 'h1', 'h2']:
            el = soup.select_one(selector)
            if el and el.get_text().strip():
                chapter_title = el.get_text().strip()
                break
                
    return soup, chapter_title

def is_redundant_front_or_back_matter(title: str, text: str) -> bool:
    """识别出版无实质正文的冗余页面（版权、广告、目录、残注）"""
    t_lower = title.lower().strip()
    
    # 纯版权、出版信息
    if any(k in t_lower for k in [
        'copyright', 'all rights reserved', 'about the publisher',
        'table of contents', 'contents', 'also by', 'praise for'
    ]):
        return True
        
    # 纯书名扉页或封面占位页（字符极少且无主要段落）
    if any(k in t_lower for k in ['title page', 'cover', 'dedication', 'quote', 'epigraph']):
        if len(text.split()) < 60:
            return True
            
    # 尾注残页或无内容占位
    if re.match(r'^chapter_\d+$', t_lower) and len(text.split()) < 40:
        return True
        
    # 纯数字或无意义短文本
    if len(text.strip()) < 80 and not any(k in text.lower() for k in ['http', 'www', 'introduction', 'prologue']):
        return True
        
    return False

def parse_toc_tree(toc, level=0, parent_title=""):
    """递归解析 EPUB 的 TOC 层级树"""
    tree = []
    for item in toc:
        if isinstance(item, tuple):
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
    """替换图片相对链接并转换为洁净 Markdown"""
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
    
    # 洁癖级文本清洗
    # 1. 移除 xml version 声明
    text = re.sub(r'xml version=[\'"][^\'"]*[\'"]\s*encoding=[\'"][^\'"]*[\'"]\??', '', text)
    # 2. 清除失效的 xhtml 跳转锚点，恢复纯文本标题
    text = re.sub(r'##\s*\[([^\]]+)\]\([^)]+\.xhtml[^)]*\)', r'## \1', text)
    text = re.sub(r'#\s*\[([^\]]+)\]\([^)]+\.xhtml[^)]*\)', r'# \1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\.xhtml[^)]*\)', r'\1', text)
    # 3. 合并过多空行
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def parse_and_export(epub_path: str, output_dir: str, nested: bool = False, save_images: bool = True, keep_all: bool = False):
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
    
    metadata = extract_metadata(book)
    print(f"📌 书名: {metadata['title']}")
    print(f"👤 作者: {metadata['creator']}")
    print(f"🗂️  模式: {'多级目录嵌套模式 (Nested)' if nested else '标准单级平铺模式 (Flat)'}")
    
    img_map = {}
    if save_images:
        print("🖼️  正在导出插图与封面...")
        img_map = dump_images(book, assets_dir)
        print(f"   已导出 {len(set(img_map.values()))} 个图片资源至 assets/")
        
    toc_tree = parse_toc_tree(book.toc)
    href_to_section = build_href_to_section_map(toc_tree) if nested else {}
    
    print("✂️  正在提取与过滤各章节...")
    raw_chapters = []
    
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
            
        item_href = item.get_name()
        soup, title_from_html = clean_html_and_extract_title(item.get_content())
        plain_text = soup.get_text().strip()
        
        # 基础过滤：字符过短
        if len(plain_text) < 20 and not any(tag in str(soup) for tag in ['<img', 'src=']):
            continue
            
        # 智能过滤出版冗余页（版权页、出版社介绍、空扉页、无意义目录）
        if not keep_all:
            candidate_title = title_from_html if title_from_html else item_href
            if is_redundant_front_or_back_matter(candidate_title, plain_text):
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
    clean_tag = sanitize_filename(metadata['title']).lower().replace('_', '-')
    
    # 连续顺次重排序号 (1-indexed)
    for idx, chap_info in enumerate(raw_chapters, start=1):
        soup = chap_info["soup"]
        title_from_html = chap_info["title_from_html"]
        section = chap_info["section_name"]
        
        title = title_from_html if title_from_html else f"Chapter_{idx:02d}"
        title = re.sub(r'\s+', ' ', title).strip()
        safe_title = sanitize_filename(title)
        
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
        
    for i, art in enumerate(processed_articles):
        nav_links = []
        root_pre = art["rel_root_prefix"]
        
        if i > 0:
            prev_art = processed_articles[i - 1]
            prev_rel = prev_art["rel_link"].replace("./", root_pre)
            nav_links.append(f"⬅️ [上一章：{prev_art['title']}]({prev_rel})")
        else:
            nav_links.append("⬅️ [第一章]")
            
        nav_links.append(f"📑 [返回目录]({root_pre}README.md)")
        
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
            
    print("📝 生成全书目录索引与 GitBook SUMMARY...")
    readme_path = out_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# {metadata['title']}\n\n")
        f.write(f"- **作者**: {metadata['creator']}\n")
        f.write(f"- **语言**: {metadata['language']}\n")
        f.write(f"- **有效正文章节**: {len(processed_articles)}\n")
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
            
    print(f"\n🎉 提取完成！已智能过滤杂质，共输出 {len(processed_articles)} 个纯净正文章节。")
    print(f"📂 输出目录: {out_dir}")
    print(f"📑 目录索引: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="将 EPUB 电子书按章节拆分导出为带元数据的 Markdown 文档 (v2.1 智能纯净版)")
    parser.add_argument("input", help="EPUB 文件路径")
    parser.add_argument("-o", "--output", help="输出目录路径 (默认为当前目录/书名)", default=None)
    parser.add_argument("--nested", action="store_true", help="启用多级目录嵌套模式 (按卷/部创建子文件夹)")
    parser.add_argument("--no-images", action="store_true", help="不导出图片资源")
    parser.add_argument("--keep-all", action="store_true", help="保留版权声明、封面占位等全部附属页面，不过滤")
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"错误: 文件不存在 -> {input_file}", file=sys.stderr)
        sys.exit(1)
        
    if not args.output:
        output_dir = Path.cwd() / input_file.stem
    else:
        output_dir = Path(args.output)
        
    parse_and_export(
        str(input_file),
        str(output_dir),
        nested=args.nested,
        save_images=not args.no_images,
        keep_all=args.keep_all
    )

if __name__ == "__main__":
    main()
