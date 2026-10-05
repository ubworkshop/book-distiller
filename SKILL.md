---
name: epub-to-markdown
description: 将 EPUB 电子书按章节精确提取并切分为单层平铺的独立 Markdown 文档。所有章节统一平铺在同一目录下，路径稳定不混乱；支持智能过滤版权页与无意义杂质、自动注入 YAML Frontmatter 元数据（书名、作者、字数、阅读时长、标签）、章节底部双向连续翻页导航、提取内嵌配图与重定向相对路径，并自动生成 README.md 和 SUMMARY.md 索引目录（完美适配 Obsidian、Notion 及 GitBook）。当用户提到"提取epub"、"epub转markdown"、"epub拆分章节"、"电子书拆解"、"epub 章节导出"等需求时触发。
---

# EPUB 章节转 Markdown Skill (v2.2 单层平铺纯净版)

将 EPUB 电子书按章节结构自动解包、清洗，并转成一套规范的单层平铺独立 Markdown 知识库。

## 功能特性

1. **统一单层平铺（Flat Structure）**：所有章节文件与 `README.md` 统一存放在同一级目录下，绝不产生层级混乱，避免多级子文件夹导致的路径断链。若书籍含有大卷/分部，自动体现在文件名与目录标记中（如 `01_第一部_第一章.md`）。
2. **绝对稳定的相对路径**：所有图片统一引用 `./assets/xxx.png`，上一章/下一章统一为 `./xx.md`，在 Obsidian、Notion 或本地 Markdown 查看器中零死链。
3. **智能去杂质与版权页过滤**：自动识别并过滤书籍中的版权声明（ISBN、免责声明）、出版社宣传页与失效的内部 XHTML 目录跳转，保持知识库纯粹（可用 `--keep-all` 显式保留）。
4. **YAML Frontmatter 元数据注入**：每章开头自动生成结构化 YAML 头信息（包含书名、作者、章节序号、中英文字数统计、预估阅读时间、标签），完美适配 Obsidian 与 Notion 属性视图。
5. **章节底部连续翻页导航**：每章末尾自动生成 `⬅️ 上一章 | 📑 返回目录 | ➡️ 下一章` 互联链接。
6. **插图与资源保留**：自动提取书籍内的配图到 `./assets/` 目录，并在 Markdown 中重写为干净的相对路径引用（`![](./assets/xxx.png)`）。
7. **自动化导航索引**：
   - 自动生成 `README.md`：包含书名、作者、简介及所有正文章节的平铺跳转清单。
   - 自动生成 `SUMMARY.md`：兼容 GitBook / mdBook 的标准侧边栏目录格式。

## 执行命令

使用系统虚拟环境中的 Python 调用转换脚本：

```bash
# 标准平铺纯净模式（推荐，自动过滤版权杂页）
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>"

# 保留全部页面（不过滤版权页）
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>" --keep-all

# 仅提取文字（跳过提取图片）
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>" --no-images
```

### 参数说明

- `<EPUB_FILE_PATH>`: EPUB 文件的绝对路径或相对路径（必须项）。
- `-o, --output`: 目标输出目录。如不指定，默认在原 EPUB 文件所在目录下生成以书名命名的同名文件夹。
- `--keep-all`: 可选，保留版权页、空扉页与出版社介绍等全部附属页面。
- `--no-images`: 可选，跳过图片资源的提取。

## 典型输出目录结构

```text
输出目录/
├── README.md               # 书籍元数据与完整正文平铺清单
├── SUMMARY.md              # 导航树索引
├── assets/                 # 提取出的全部插图、封面
│   ├── cover.jpg
│   └── figure_01.png
├── 01_导论.md
├── 02_第一部_我的历程_探索.md
├── 03_第一部_我的历程_顿悟.md
├── 04_第二部_生活原则_拥抱现实.md
└── ...
```
