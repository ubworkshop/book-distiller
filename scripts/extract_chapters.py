#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB Chapter Extractor
将 EPUB 电子书按章节提取并切分为独立的 Markdown 文档，支持抽取图片、清洗排版及生成目录索引。
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
    if not clean:
        clean = "untitled"
    return clean[:max_length]

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

def dump_images(book: epub.EpubBook, output_dir: Path) -> dict:
    """提取书中所有图片，并返回 原文件名 -> 导出相对路径 映射表"""
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    img_map = {}
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_IMAGE:
            # 取得文件名，避免深层路径问题
            orig_name = Path(item.get_name()).name
            target_path = assets_dir / orig_name
            with open(target_path, "wb") as f:
                f.write(item.get_content())
            img_map[orig_name] = f"./assets/{orig_name}"
            # 同时兼容带路径的匹配
            img_map[item.get_name()] = f"./assets/{orig_name}"
            img_map[f"../Images/{orig_name}"] = f"./assets/{orig_name}"
            img_map[f"Images/{orig_name}"] = f"./assets/{orig_name}"
            
    return img_map

def build_toc_map(toc_entries) -> dict:
    """递归解析 TOC 目录树，建立 href -> 标题 映射表"""
    toc_map = {}
    def _parse(entries):
        for entry in entries:
            if isinstance(entry, epub.Link):
                clean_href = entry.href.split('#')[0]
                if clean_href not in toc_map:
                    toc_map[clean_href] = entry.title
                toc_map[Path(clean_href).name] = entry.title
            elif isinstance(entry, tuple):
                section, sub = entry
                if hasattr(section, 'href') and section.href:
                    clean_href = section.href.split('#')[0]
                    if clean_href not in toc_map:
                        toc_map[clean_href] = section.title
                    toc_map[Path(clean_href).name] = section.title
                elif hasattr(section, 'title') and section.title:
                    pass
                _parse(sub)
    _parse(toc_entries)
    return toc_map

def clean_html_and_rewrite_images(content: bytes, img_map: dict, save_images: bool = True) -> tuple[str, str]:
    """清洗 HTML 并替换图片路径，提取第一优先标题"""
    content_str = content.decode('utf-8', errors='ignore')
    # 彻底剔除 xml 声明与特殊处理指令
    content_str = re.sub(r'<\?xml[^>]*\?>', '', content_str, flags=re.I)
    
    soup = BeautifulSoup(content_str, 'html.parser')
    
    # 移除无用标签
    for tag in soup(['script', 'style', 'link', 'meta']):
        tag.decompose()
        
    # 清理空的标题标签
    for h_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if not h_tag.get_text().strip():
            h_tag.decompose()
            
    # 尝试提取章节标题
    chapter_title = ""
    for h in ['h1', 'h2', 'h3', 'title']:
        header = soup.find(h)
        if header and header.get_text().strip():
            chapter_title = header.get_text().strip()
            break
            
    if not save_images:
        # 用户不需要图片时，彻底移除图片和 svg，避免留下裂图死链
        for img in soup.find_all('img'):
            img.decompose()
        for svg in soup.find_all(['svg', 'image', 'svg:image']):
            svg.decompose()
    else:
        # 替换图片链接
        for img in soup.find_all('img'):
            src = img.get('src', '')
            src_name = Path(src).name
            if src_name in img_map:
                img['src'] = img_map[src_name]
            elif src in img_map:
                img['src'] = img_map[src]
                
        # 替换 svg 中的 image
        for svg_img in soup.find_all(['image', 'svg:image']):
            href = svg_img.get('xlink:href') or svg_img.get('href')
            if href:
                href_name = Path(href).name
                if href_name in img_map:
                    new_img = soup.new_tag("img", src=img_map[href_name])
                    svg_img.replace_with(new_img)
                
    return str(soup), chapter_title

def convert_to_markdown(html_content: str) -> str:
    """将 HTML 转换为排版工整的 Markdown"""
    text = md(
        html_content,
        heading_style="ATX",
        bullets_style="-",
        strip=['script', 'style']
    )
    # 剔除可能残留的 xml 声明字符串
    text = re.sub(r'^(?:xml\s+version=[^\n]*|\<\?xml[^\n]*)\n*', '', text, flags=re.I | re.M)
    # 清理仅有 '#' 的空标题行
    text = re.sub(r'^[#]+\s*$\n+', '', text, flags=re.M)
    # 将 Unicode 实心圆点列表转换为标准 Markdown '-'
    text = re.sub(r'^[●•]\s*', '- ', text, flags=re.M)
    # 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def parse_and_export(epub_path: str, output_dir: str, save_images: bool = True):
    """主执行逻辑"""
    epub_file = Path(epub_path).resolve()
    if not epub_file.exists():
        print(f"错误: 找不到文件 {epub_path}", file=sys.stderr)
        sys.exit(1)
        
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📖 正在解析: {epub_file.name} ...")
    book = epub.read_epub(str(epub_file))
    
    # 1. 元数据与 TOC
    metadata = extract_metadata(book)
    print(f"📌 书名: {metadata['title']}")
    print(f"👤 作者: {metadata['creator']}")
    
    toc_map = build_toc_map(book.toc)
    print(f"📑 从 TOC 目录中识别出 {len(toc_map)} 个命名条目")
    
    # 2. 导出图片
    img_map = {}
    if save_images:
        print("🖼️  正在导出插图与封面...")
        img_map = dump_images(book, out_dir)
        print(f"   已导出 {len(img_map)} 个图片资源至 assets/")
    else:
        print("🚫 跳过图片提取，纯净 Markdown 模式")
        
    # 3. 遍历章节 (按 spine 顺序保证阅读流完整)
    print("✂️  正在按章节提取内容...")
    chapters_summary = []
    chapter_index = 0
    
    for item_id, linear in book.spine:
        item = book.get_item_with_id(item_id)
        if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
            
        html_str, title_from_html = clean_html_and_rewrite_images(item.get_content(), img_map, save_images=save_images)
        markdown_text = convert_to_markdown(html_str)
        
        # 忽略过短无实际内容的占位页面（如空页或仅有纯空格）
        if len(markdown_text.strip()) < 15 and not any(tag in html_str for tag in ['<img', 'src=']):
            continue
            
        # 确定章节标题：优先 TOC -> 其次 HTML header -> 再次特征文本 -> fallback
        item_name = item.get_name()
        title = toc_map.get(item_name) or toc_map.get(Path(item_name).name) or title_from_html
        
        if not title:
            lower_text = markdown_text.lower()
            if "table of contents" in lower_text[:400]:
                title = "Table of Contents"
            elif "all rights reserved" in lower_text[:400] or "copyright" in lower_text[:400]:
                title = "Copyright"
            elif "american idioms" in lower_text[:400] or "valencia" in lower_text[:400]:
                title = "Title Page"
            else:
                lines = [l.strip() for l in markdown_text.splitlines() if l.strip()]
                if lines and len(lines[0]) <= 50 and not lines[0].startswith('!'):
                    title = re.sub(r'^[#*\-_>\s]+', '', lines[0]).strip()
                
        if not title or len(title) < 2:
            title = f"Chapter_{chapter_index:02d}"
            
        # 清除标题内的回车换行与异常空白
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 文件命名: 00_章节名.md
        safe_title = sanitize_filename(title)
        filename = f"{chapter_index:02d}_{safe_title}.md"
        file_path = out_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            # 顶部增加一级标题（如果正文没有以该标题开头）
            if not markdown_text.startswith(f"# {title}") and not markdown_text.startswith(f"## {title}"):
                f.write(f"# {title}\n\n")
            f.write(markdown_text)
            f.write("\n")
            
        chapters_summary.append({
            "index": chapter_index,
            "title": title,
            "filename": filename
        })
        chapter_index += 1
        
    # 4. 生成 README.md 与 SUMMARY.md
    print("📝 生成书籍目录索引...")
    readme_path = out_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# {metadata['title']}\n\n")
        f.write(f"- **作者**: {metadata['creator']}\n")
        f.write(f"- **语言**: {metadata['language']}\n")
        if metadata['description']:
            f.write(f"- **简介**: {metadata['description']}\n")
        f.write("\n---\n\n## 章节目录\n\n")
        for chap in chapters_summary:
            f.write(f"- [{chap['title']}](./{chap['filename']})\n")
            
    summary_path = out_dir / "SUMMARY.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Summary\n\n")
        f.write(f"* [{metadata['title']}](README.md)\n")
        for chap in chapters_summary:
            f.write(f"  * [{chap['title']}]({chap['filename']})\n")
            
    print(f"\n✅ 提取完成！共输出 {len(chapters_summary)} 个章节文档。")
    print(f"📂 输出目录: {out_dir}")
    print(f"📑 目录索引: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="将 EPUB 电子书按章节拆分导出为 Markdown 文档")
    parser.add_argument("input", help="EPUB 文件路径")
    parser.add_argument("-o", "--output", help="输出目录路径 (默认为当前目录/书名)", default=None)
    parser.add_argument("--no-images", action="store_true", help="不导出图片资源")
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"错误: 文件不存在 -> {input_file}", file=sys.stderr)
        sys.exit(1)
        
    if not args.output:
        output_dir = input_file.parent / input_file.stem
    else:
        output_dir = Path(args.output)
        
    parse_and_export(str(input_file), str(output_dir), save_images=not args.no_images)

if __name__ == "__main__":
    main()
