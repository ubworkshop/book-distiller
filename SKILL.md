---
name: epub-to-markdown
description: 将 EPUB 电子书按章节精确提取并切分为独立的 Markdown 文档。支持多级目录嵌套模式（--nested，按卷/部创建子文件夹）、智能过滤版权与出版冗余页（--keep-all 保留全部）、自动注入 YAML Frontmatter 元数据（书名、作者、字数、阅读时长、标签）、章节底部双向翻页导航、提取内嵌配图与重定向相对路径，并自动生成 README.md 和 SUMMARY.md 索引目录（适配 Obsidian、Notion 及 GitBook）。当用户提到"提取epub"、"epub转markdown"、"epub拆分章节"、"电子书拆解"、"epub 章节导出"等需求时触发。
---

# EPUB 章节转 Markdown Skill (v2.1 智能纯净版)

将 EPUB 电子书按章节结构自动解包、清洗，并转成一套规范的独立 Markdown 知识库。

## 功能特性

1. **精准章节切分**：按书籍 Spine 顺序列序拆分，保留序言、正文各章及附录，输出为 `01_第一章_xxx.md`。
2. **智能去杂质与版权页过滤**：自动识别并过滤书籍中的版权声明（ISBN、免责声明）、出版社宣传页与失效的内部 XHTML 目录跳转，保持知识库纯粹（可用 `--keep-all` 显式保留）。
3. **多级目录嵌套模式 (`--nested`)**：支持自动识别书籍的大卷/大部（Parts / Sections），自动建立二级子文件夹归档各章。
4. **YAML Frontmatter 元数据注入**：每章开头自动生成结构化 YAML 头信息（包含书名、作者、章节序号、中英文字数统计、预估阅读时间、标签），完美适配 Obsidian 与 Notion 属性视图。
5. **章节底部连续翻页导航**：每章末尾自动生成 `⬅️ 上一章 | 📑 返回目录 | ➡️ 下一章` 互联链接。
6. **插图与资源保留**：自动提取书籍内的配图到 `assets/` 目录，并在 Markdown 中重写为正确的相对路径引用（`![](./assets/xxx.png)` 或 `![](../assets/xxx.png)`）。
7. **自动化导航索引**：
   - 自动生成 `README.md`：包含书名、作者、简介及所有正文章节的层级跳转清单。
   - 自动生成 `SUMMARY.md`：兼容 GitBook / mdBook 的标准侧边栏目录格式。

## 执行命令

使用系统虚拟环境中的 Python 调用转换脚本：

```bash
# 智能纯净模式（自动过滤版权杂页）
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>"

# 多级目录嵌套模式（按大卷/分部自动建立子文件夹）
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>" --nested

# 保留全部页面（不过滤版权页）
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>" --keep-all
```

### 参数说明

- `<EPUB_FILE_PATH>`: EPUB 文件的绝对路径或相对路径（必须项）。
- `-o, --output`: 目标输出目录。如不指定，默认在原 EPUB 文件所在目录下生成以书名命名的同名文件夹。
- `--nested`: 可选，开启按分卷/分部的多级子目录嵌套模式。
- `--keep-all`: 可选，保留版权页、空扉页与出版社介绍等全部附属页面。
- `--no-images`: 可选，跳过图片资源的提取。

## 典型输出目录结构

### 启用 `--nested` 模式：
```text
输出目录/
├── README.md               # 书籍元数据与完整层级章节清单
├── SUMMARY.md              # 导航树索引
├── assets/                 # 提取出的全部插图、封面
│   ├── cover.jpg
│   └── figure_01.png
├── 第一部分_我的历程/
│   ├── 01_第一章_导论.md
│   └── 02_第二章_探索.md
├── 第二部分_生活原则/
│   ├── 03_拥抱现实.md
│   └── 04_五步流程.md
└── 01_序言.md
```
