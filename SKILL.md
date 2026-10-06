---
name: book-distiller
description: Book Distiller (书籍蒸馏器) - 电子书章节拆解、黄金原料萃取与多平台书评创作引擎。将 EPUB 电子书按章节精确提取并切分为单层平铺的独立 Markdown 文档。支持挂载子技能（extract-insights 提取 4 类写作黄金原料、全书一页纸决策简报、断点续传与增量合并；book-review 提供"全书书评创作矩阵规划"、"四段心流自由搭配菜单"与"语义化主题 Slug 命名"，并输出独立血统溯源图谱）。智能过滤版权与无意义杂质、自动注入 YAML Frontmatter、章节翻页导航、配图提取，并生成 README.md 和 SUMMARY.md 索引目录。当用户提到"book-distiller"、"书籍蒸馏"、"提取epub"、"epub转markdown"、"一页纸简报"、"书评矩阵"、"挑选心流"、"四段心流"、"写读后感"、"小红书书评"、"血统溯源"等需求时触发。
---

# Book Distiller (书籍蒸馏器 v3.1 全书决策简报与矩阵创作版)

**从电子书章节拆解、黄金原料萃取、全书一页纸决策简报到多平台书评创作矩阵的一体化引擎。**

将 EPUB 电子书按章节结构自动解包、清洗，并转成一套规范的单层平铺独立 Markdown 知识库；向下游串联完整的创作者流水线，实现从**书籍切分 ➔ 4D黄金原料挖掘(断点续传) ➔ 00_全书一页纸决策简报 ➔ 全书书评创作矩阵 ➔ 四段心流积木自由搭配 ➔ 语义化 Slug 纯净正文与独立溯源图谱**的完整闭环。

---

## 核心架构与功能

1. **统一单层平铺（Flat Structure）**：所有章节文件与 `README.md` 统一存放在同一级目录下，绝不产生层级混乱，避免多级子文件夹导致的路径断链。若书籍含有大卷/分部，自动体现在文件名与目录标记中（如 `01_第一部_第一章.md`）。
2. **绝对稳定的相对路径**：所有图片统一引用 `./assets/xxx.png`，上一章/下一章统一为 `./xx.md`，在 Obsidian、Notion 或本地 Markdown 查看器中零死链。
3. **智能去杂质与版权页过滤**：自动识别并过滤书籍中的版权声明（ISBN、免责声明）、出版社宣传页与失效的内部 XHTML 目录跳转，保持知识库纯粹（可用 `--keep-all` 显式保留）。
4. **YAML Frontmatter 元数据注入**：每章开头自动生成结构化 YAML 头信息（包含书名、作者、章节序号、中英文字数统计、预估阅读时间、标签），完美适配 Obsidian 与 Notion 属性视图。
5. **章节底部连续翻页导航**：每章末尾自动生成 `⬅️ 上一章 | 📑 返回目录 | ➡️ 下一章` 互联链接。
6. **插图与资源保留**：自动提取书籍内的配图到 `./assets/` 目录，并在 Markdown 中重写为干净的相对路径引用（`![](./assets/xxx.png)`）。
7. **自动化导航索引**：自动生成 `README.md` 与 `SUMMARY.md`。

---

## 🧩 挂载子技能体系 (Sub-skills Ecosystem)

```mermaid
flowchart TD
    EPUB[原始 EPUB 电子书] --> Main[Book Distiller 核心引擎]
    Main --> Chapters[单层平铺章节 Markdown]
    Chapters --> S1[Sub-skill: extract-insights]
    S1 --> Brief[📑 00_全书一页纸决策简报.md]
    S1 --> Insights[insights/ 四大黄金原料总库 (断点续传)]
    Insights --> S2[Sub-skill: book-review]
    Chapters --> S2
    S2 --> Matrix[00_全书书评创作矩阵规划.md]
    Matrix --> Menu[🧩 四段心流积木自由搭配菜单]
    Menu --> Selection[创作者挑选心流组合]
    Selection --> Reviews[平台纯净正文 review_platform_slug.md]
    Selection --> Provenance[🧬 独立血统溯源 review_platform_slug_provenance.md]
```

### 1. `extract-insights` (4+2 黄金原料提取 · 一页纸决策简报版)
- **📑 00_全书一页纸决策简报 (1-Page Executive Summary)**：
  - 📌 一句话本质判词（表面聊什么 vs 底层本质重构了什么）；
  - ⚡️ 三大最具穿透力的反常识断言；
  - 🧠 作者底层逻辑推导闭环（Mermaid 架构流程图）；
  - 🎯 读者适合度诊断（谁该立刻读 vs 谁读了是浪费时间）；
  - 💎 全书灵魂锚点金句与自媒体发帖行动指引。
- **4+2 黄金原料提取**：反直觉认知(带爆款打分)、故事微案例、落地微清单、穿透金句、痛点映射、Obsidian 概念双链。
- **断点续传与增量合并**：自动跳过已完成章节，支持 `--sync` 一键去重汇聚更新四大总库与决策简报。

### 2. `book-review` (全书书评矩阵 · 四段心流自由拼配)
- **🗺️ 全书书评创作矩阵 (Review Matrix)**：一键规划全书 4~6 篇差异化发帖选题（引流爆款篇、认知觉醒篇、深度长文篇、工具实操篇）。
- **🧩 四段心流自由搭配菜单 (Flow Modular Menu)**：Hook痛点 / 认知反转 / 极简解法 / 灵魂收尾。
- **🏷️ 语义化主题 Slug 双文件分离交付**：
  - 纯净正文：`review_{platform}_{slug}_{timestamp}.md`
  - 独立溯源图谱：`review_{platform}_{slug}_{timestamp}_provenance.md`

---

## 执行命令

```bash
# 1. 主流程：标准平铺纯净提取 EPUB 电子书
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/book-distiller/scripts/extract_chapters.py "<EPUB_FILE_PATH>" -o "<OUTPUT_DIR>"

# 2. 为已提取的书籍搭建写作原料库并生成全书一页纸决策简报 (extract-insights)
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/book-distiller/scripts/extract_insights.py "<BOOK_DIR>"

# 3. 为整本书生成书评创作矩阵规划 (book-review)
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/book-distiller/scripts/generate_review.py "<BOOK_DIR>" --matrix

# 4. 生成语义化主题 Slug 双文件读后感草稿
~/.agent-reach-venv/bin/python3 ~/.gemini/config/skills/book-distiller/scripts/generate_review.py "<BOOK_DIR>" --platform xhs --topic "精力管理与停止内耗" --combo "1B+2A+3A+4A"
```

## 典型输出目录结构

```text
输出目录/
├── README.md                                                 # 书籍元数据与完整正文平铺清单
├── SUMMARY.md                                                # 导航树索引
├── 00_全书一页纸决策简报.md                                    # 👈 3分钟俯瞰全书破局逻辑与反常识断言
├── assets/                                                   # 提取出的全部插图、封面
├── 01_导论.md
├── 02_第一部_我的历程_探索.md
├── insights/                                                 # 👈 写作黄金原料库（支持断点续传与增量更新）
│   ├── 00_全书爆款选题与反直觉库.md
│   ├── 00_全书高穿透金句大全.md
│   ├── 00_读者现实痛点与对号入座索引.md
│   ├── 00_全书核心概念与思维模型图谱.md
│   └── 02_第一部_我的历程_探索_原料卡.md
└── reviews/                                                  # 👈 书评创作矩阵库
    ├── 00_全书书评创作矩阵规划.md                               # 👈 全书 4~6 篇选题矩阵规划表
    ├── flow_menu_20261006.md                                 # 👈 四段心流积木备选菜单
    ├── review_xhs_精力管理与停止内耗_20261006.md                 # 👈 语义化 Slug 纯净正文
    └── review_xhs_精力管理与停止内耗_20261006_provenance.md      # 👈 语义化 Slug 独立溯源图谱
```
