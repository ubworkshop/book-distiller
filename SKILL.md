---
name: epub-to-markdown
description: 将 EPUB 电子书按章节精确提取并切分为单层平铺的独立 Markdown 文档。支持挂载子技能（Sub-skills，如 extract-insights 提取 4 类写作黄金原料）、智能过滤版权与无意义杂质、自动注入 YAML Frontmatter 元数据（书名、作者、字数、阅读时长、标签）、章节底部双向连续翻页导航、提取内嵌配图与重定向相对路径，并自动生成 README.md 和 SUMMARY.md 索引目录（完美适配 Obsidian、Notion 及 GitBook）。当用户提到"提取epub"、"epub转markdown"、"epub拆分章节"、"电子书拆解"、"epub 章节导出"、"提取黄金原料"等需求时触发。
---

# EPUB 章节转 Markdown Skill (v2.3 模块化子技能版)

将 EPUB 电子书按章节结构自动解包、清洗，并转成一套规范的单层平铺独立 Markdown 知识库；同时支持调用下游子技能进行创作加工。

## 核心架构与功能

1. **统一单层平铺（Flat Structure）**：所有章节文件与 `README.md` 统一存放在同一级目录下，绝不产生层级混乱，避免多级子文件夹导致的路径断链。若书籍含有大卷/分部，自动体现在文件名与目录标记中（如 `01_第一部_第一章.md`）。
2. **绝对稳定的相对路径**：所有图片统一引用 `./assets/xxx.png`，上一章/下一章统一为 `./xx.md`，在 Obsidian、Notion 或本地 Markdown 查看器中零死链。
3. **智能去杂质与版权页过滤**：自动识别并过滤书籍中的版权声明（ISBN、免责声明）、出版社宣传页与失效的内部 XHTML 目录跳转，保持知识库纯粹（可用 `--keep-all` 显式保留）。
4. **YAML Frontmatter 元数据注入**：每章开头自动生成结构化 YAML 头信息（包含书名、作者、章节序号、中英文字数统计、预估阅读时间、标签），完美适配 Obsidian 与 Notion 属性视图。
5. **章节底部连续翻页导航**：每章末尾自动生成 `⬅️ 上一章 | 📑 返回目录 | ➡️ 下一章` 互联链接。
6. **插图与资源保留**：自动提取书籍内的配图到 `./assets/` 目录，并在 Markdown 中重写为干净的相对路径引用（`![](./assets/xxx.png)`）。
7. **自动化导航索引**：自动生成 `README.md` 与 `SUMMARY.md`。

---

## 🧩 挂载子技能 (Sub-skills)

本技能支持向下游扩展专业子技能。目前已内置：

### 1. `extract-insights` (4 类写作黄金原料提取)
- **定位**：拒绝无意义的全文摘要，专门从切分好的章节中挖掘自媒体与长文创作的 4 类黄金原料：
  - ⚡️ **反直觉认知 (Hook 灵感)**：打破常识误区，提炼 3 种爆款钩子。
  - 📖 **故事与微案例 (论据素材)**：具象人物冲突与破局案例。
  - 🛠️ **可落地微清单 (读者收藏向)**：三步流程法与避坑红线。
  - 💎 **高穿透金句 (社交配图)**：情绪共鸣强烈的金句与适用语境。
- **触发方式**：
  - 针对单章：“提取 `02_第一部_探索.md` 的黄金原料”
  - 批量建立原料库：“为这本解包好的书建立写作原料库”

---

## 执行命令

```bash
# 1. 主流程：标准平铺纯净提取 EPUB 电子书
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>"

# 2. 为已提取的书籍搭建写作原料库骨架
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/epub-to-markdown/scripts/extract_insights.py "<BOOK_DIR>"
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
├── 03_第二部_生活原则_拥抱现实.md
└── insights/               # 👈 写作原料库（调用子技能产生）
    ├── 00_全书爆款选题与反直觉库.md
    ├── 00_全书高穿透金句大全.md
    └── 02_第一部_我的历程_探索_原料卡.md
```
