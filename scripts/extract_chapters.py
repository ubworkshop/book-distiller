#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB Chapter Extractor (v2.2 单层平铺纯净版)
将 EPUB 电子书按章节提取并平铺切分为独立的 Markdown 文档。
特性：
- 严格单层平铺：所有章节整齐平铺在同一目录下，绝不产生层级混乱
- 统一相对路径：图片统一引用 ./assets/xxx.png，上一章/下一章统一为 ./xx.md
- YAML Frontmatter 元数据注入 (书名, 作者, 序号, 字数, 预估时长, 标签)
- 章节底部 上一章 / 返回目录 / 下一章 翻页导航
- 智能过滤版权页、空扉页、出版社广告与无效内部链接
- 自动生成全书 README.md 和 SUMMARY.md 索引目录
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

def is_redundant_page(title: str, text: str) -> bool:
    """判断是否为出版冗余页面（版权、免责声明、纯书名扉页等）"""
    t_lower = title.lower()
    
    # 明确的冗余标题
    noise_keywords = [
        'copyright', 'imprint', 'publisher', 'titlepage', 'title_page',
        'cover', 'toc', 'contents', 'table of contents',
        '版权', '图书在版编目', 'cip', '出版说明', '免责声明', '扉页', '书名页'
    ]
    if any(k in t_lower for k in noise_keywords):
        return True
        
    # 文本非常短，且内容大部分为版权信息
    if len(text) < 300:
        first_part = text[:200].lower()
        if any(w in first_part for w in ['isbn', 'all rights reserved', 'published by', '版权所有', '责任编辑', '字数', '印张']):
            return True
            
    return False

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
            rel_path = f"./assets/{orig_name}"
            img_map[orig_name] = rel_path
            img_map[item.get_name()] = rel_path
            img_map[f"../Images/{orig_name}"] = rel_path
            img_map[f"Images/{orig_name}"] = rel_path
            img_map[f"../images/{orig_name}"] = rel_path
            img_map[f"images/{orig_name}"] = rel_path
            
    return img_map

def clean_html_and_extract_title(content: bytes) -> tuple[BeautifulSoup, str]:
    """清洗 HTML 并提取第一候选标题"""
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style', 'link', 'meta']):
        tag.decompose()
        
    chapter_title = ""
    for selector in ['h1', 'h2', 'title', '.chapter-title', '.title', '.headline']:
        header = soup.select_one(selector)
        if header and header.get_text().strip():
            candidate = header.get_text().strip()
            if len(candidate) > 1 and not candidate.lower().startswith("table of contents"):
                chapter_title = candidate
                break
                
    return soup, chapter_title

def parse_toc_section_mapping(toc):
    """解析 TOC 建立 href -> 大分卷/部名称 的前缀映射"""
    mapping = {}
    for item in toc:
        if isinstance(item, tuple):
            section, subitems = item
            sec_title = section.title.strip() if hasattr(section, 'title') else ""
            sec_href = section.href.split('#')[0] if hasattr(section, 'href') and section.href else ""
            if sec_href and sec_title:
                mapping[sec_href] = sec_title
            for sub in subitems:
                if hasattr(sub, 'href') and sub.href:
                    mapping[sub.href.split('#')[0]] = sec_title
        elif hasattr(item, 'href') and item.href:
            mapping[item.href.split('#')[0]] = ""
    return mapping

def convert_to_markdown(soup: BeautifulSoup, img_map: dict) -> str:
    """替换图片路径、清洗内部死链并转为 Markdown"""
    for img in soup.find_all('img'):
        src = img.get('src', '')
        src_name = Path(src).name
        if src_name in img_map:
            img['src'] = img_map[src_name]
        elif src in img_map:
            img['src'] = img_map[src]

    for svg_img in soup.find_all(['image', 'svg:image']):
        href = svg_img.get('xlink:href') or svg_img.get('href')
        if href:
            href_name = Path(href).name
            if href_name in img_map:
                new_img = soup.new_tag("img", src=img_map[href_name])
                svg_img.replace_with(new_img)

    text = md(
        str(soup),
        heading_style="ATX",
        bullets_style="-",
        strip=['script', 'style']
    )
    # 清洗失效的内部 xhtml 链接跳转，保留显示文字
    text = re.sub(r'#\s*\[([^\]]+)\]\([^)]+\.xhtml[^)]*\)', r'# \1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\.xhtml[^)]*\)', r'\1', text)
    # 合并连续多余空行
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def parse_and_export(epub_path: str, output_dir: str, save_images: bool = True, keep_all: bool = False):
    """核心平铺导出执行流程"""
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
    print(f"🗂️  模式: 统一单层平铺模式 (Flat)")
    
    # 导出图片
    img_map = {}
    if save_images:
        print("🖼️  正在导出插图与封面...")
        img_map = dump_images(book, assets_dir)
        print(f"   已导出 {len(set(img_map.values()))} 个图片资源至 ./assets/")
        
    # 解析 TOC 卷名映射
    href_to_section = parse_toc_section_mapping(book.toc)
    
    print("✂️  正在提取与过滤各章节...")
    raw_chapters = []
    
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
            
        item_href = item.get_name()
        soup, title_from_html = clean_html_and_extract_title(item.get_content())
        plain_text = soup.get_text().strip()
        
        # 过滤过短无意义空页
        if len(plain_text) < 20 and not any(tag in str(soup) for tag in ['<img', 'src=']):
            continue
            
        # 智能过滤版权与冗余页
        if not keep_all:
            candidate_title = title_from_html if title_from_html else item_href
            if is_redundant_page(candidate_title, plain_text):
                continue
                
        section_name = href_to_section.get(item_href, "")
        raw_chapters.append({
            "soup": soup,
            "title_from_html": title_from_html,
            "section_name": section_name,
            "item_href": item_href
        })
        
    clean_tag = sanitize_filename(metadata['title']).lower().replace('_', '-')
    processed_articles = []
    
    # 连续顺次重排为单层平铺文件
    for idx, chap_info in enumerate(raw_chapters, start=1):
        soup = chap_info["soup"]
        title_from_html = chap_info["title_from_html"]
        section = chap_info["section_name"]
        
        # 标题生成
        title = title_from_html if title_from_html else f"Chapter_{idx:02d}"
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 如果有分卷名且标题未包含，在文件名中优雅体现分卷信息，但绝不创建子文件夹
        if section and section not in title:
            file_title = f"{section}_{title}"
        else:
            file_title = title
            
        safe_title = sanitize_filename(file_title)
        filename = f"{idx:02d}_{safe_title}.md"
        file_path = out_dir / filename
        rel_link = f"./{filename}"
        
        markdown_body = convert_to_markdown(soup, img_map)
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
            "section": section,
            "filename": filename,
            "file_path": file_path,
            "rel_link": rel_link,
            "frontmatter": "\n".join(frontmatter),
            "markdown_body": markdown_body
        })
        
    # 写入各章节文件（全部位于同一层级，导航链接极致稳定）
    for i, art in enumerate(processed_articles):
        nav_links = []
        
        # 上一章
        if i > 0:
            prev_art = processed_articles[i - 1]
            nav_links.append(f"⬅️ [上一章：{prev_art['title']}]({prev_art['rel_link']})")
        else:
            nav_links.append("⬅️ [第一章]")
            
        # 目录
        nav_links.append(f"📑 [返回目录](./README.md)")
        
        # 下一章
        if i + 1 < len(processed_articles):
            next_art = processed_articles[i + 1]
            nav_links.append(f"➡️ [下一章：{next_art['title']}]({next_art['rel_link']})")
        else:
            nav_links.append("➡️ [尾声]")
            
        nav_footer = f"\n\n---\n\n" + " | ".join(nav_links) + "\n"
        
        with open(art["file_path"], "w", encoding="utf-8") as f:
            f.write(art["frontmatter"] + "\n")
            if not art["markdown_body"].startswith("# "):
                f.write(f"# {art['title']}\n\n")
            f.write(art["markdown_body"])
            f.write(nav_footer)
            
    # 生成 README.md 与 SUMMARY.md
    print("📝 生成全书单层平铺目录与 SUMMARY.md...")
    readme_path = out_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# {metadata['title']}\n\n")
        f.write(f"- **作者**: {metadata['creator']}\n")
        f.write(f"- **语言**: {metadata['language']}\n")
        f.write(f"- **有效正文章节**: {len(processed_articles)}\n")
        if metadata['description']:
            f.write(f"- **简介**: {metadata['description']}\n")
        f.write("\n---\n\n## 📑 章节目录\n\n")
        for chap in processed_articles:
            prefix = f"【{chap['section']}】" if chap['section'] else ""
            f.write(f"- [{chap['index']:02d}. {prefix}{chap['title']}]({chap['rel_link']})\n")
            
    summary_path = out_dir / "SUMMARY.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Summary\n\n")
        f.write(f"* [{metadata['title']}](README.md)\n")
        for chap in processed_articles:
            prefix = f"{chap['section']} - " if chap['section'] else ""
            f.write(f"  * [{prefix}{chap['title']}]({chap['filename']})\n")
            
    print(f"\n🎉 提取完成！已按单层平铺输出 {len(processed_articles)} 个纯净章节。")
    print(f"📂 输出目录: {out_dir}")
    print(f"📑 目录索引: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="将 EPUB 电子书按章节拆分导出为单层平铺的 Markdown 文档 (v2.2)")
    parser.add_argument("input", help="EPUB 文件路径")
    parser.add_argument("-o", "--output", help="输出目录路径 (默认为当前目录/书名)", default=None)
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
        save_images=not args.no_images,
        keep_all=args.keep_all
    )

if __name__ == "__main__":
    main()
