---
name: epub-to-markdown
description: 将 EPUB 电子书按章节精确提取并切分为独立的 Markdown 文档。支持提取内嵌配图、保留标题层级与排版、自动重映射图片相对路径，并生成 README.md 和 SUMMARY.md 索引目录（适配 Obsidian、Notion 及 GitBook）。当用户提到"提取epub"、"epub转markdown"、"epub拆分章节"、"电子书拆解"、"epub 章节导出"等需求时触发。
---

# EPUB 章节转 Markdown Skill

将 EPUB 电子书按章节结构自动解包、清洗，并转成一套规范的独立 Markdown 知识库。

## 功能特性

1. **精准章节切分**：按书籍 Spine 顺序列序拆分，保留封面、序言、正文各章及附录，输出为 `00_序言.md`、`01_第一章_xxx.md`。
2. **插图与资源保留**：自动提取书籍内的配图到 `assets/` 目录，并在 Markdown 中重写为正确的相对路径引用（`![](./assets/xxx.png)`）。
3. **清洗排版**：剔除冗余内嵌 HTML/CSS、无意义空行与脚本，保留标准的 Markdown 标题（ATX）、列表、引用与粗斜体。
4. **自动化导航索引**：
   - 自动生成 `README.md`：包含书名、作者、简介及所有章节的点击跳转链接。
   - 自动生成 `SUMMARY.md`：兼容 GitBook / mdBook 的标准侧边栏目录格式。

## 执行命令

使用系统虚拟环境中的 Python 调用转换脚本：

```bash
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>"
```

### 参数说明

- `<EPUB_FILE_PATH>`: EPUB 文件的绝对路径或相对路径（必须项）。
- `-o, --output`: 目标输出目录。如不指定，默认在原 EPUB 文件所在目录下生成以书名命名的同名文件夹。
- `--no-images`: 可选，跳过图片资源的提取。

## 典型输出目录结构

```text
输出目录/
├── README.md               # 书籍元数据与完整章节清单
├── SUMMARY.md              # 导航树索引
├── assets/                 # 提取出的全部插图、封面
│   ├── cover.jpg
│   └── image_01.png
├── 00_封面与前言.md
├── 01_第一章_引言.md
├── 02_第二章_核心概念.md
└── ...
```

## Agent 执行指引

当收到用户对 EPUB 文件的转换请求时：
1. 确认用户的 EPUB 文件路径（若用户只提供文件名，在工作区中搜索该文件）。
2. 如用户未指定输出目录，优先在当前工作空间或 EPUB 所在目录创建目标文件夹。
3. 执行转换脚本：
   `~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>"`
4. 转换完成后，读取 `README.md`，向用户汇报提取的章节总数、输出路径以及前几个章节的概览。
