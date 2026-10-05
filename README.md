# Book Distiller (书籍蒸馏器)

> Precise chapter-by-chapter EPUB extraction to clean, flat Markdown documents with modular sub-skills (extract-insights: 4D raw materials + Obsidian graph; book-review: multi-platform high-resonance book reviews + full lineage & provenance connection graph), smart noise filtering, YAML frontmatter, image assets, and structured indexes.

An Agent Skill for parsing and splitting `.epub` ebooks into clean, standalone Markdown chapters, preserving image assets and hierarchy, building `README.md` and `SUMMARY.md` catalogs for Obsidian, Notion, or GitBook, extracting creator insights, and generating multi-platform book reviews with full design provenance.

## ✨ Features

- **Strictly Flat Directory Structure**: All chapters are extracted side-by-side into a single folder. No confusing nested directories or broken relative links.
- **Modular Sub-skills (Advanced Creator Suite v2.8)**:
  - ⚡️ **`extract-insights`**: Extracts Contrarian Hooks (with 1-5 ⭐ viral ratings and 🔥 Top 5 pinned topics), Concrete Stories/Cases, Actionable Checklists, High-resonance Quotes, Obsidian Concept Graph (`[[Wikilinks]]`), and Symptom Mapping.
  - ✍️ **`book-review`**: Weaves extracted raw materials into platform-native, high-resonance book reviews (Xiaohongshu visual cards, Threads 4-post threads, WeChat in-depth essays) with a calm, empathetic, anti-preachy voice.
  - 🧬 **Full Lineage & Provenance Blueprint (完整血统溯源与联系图谱)**: Accompanying every review is a Mermaid design connection graph, a source-lineage mapping table (tying hook, painpoint, inversion, checklist, and quote back to the exact book chapter and insights card), and Obsidian concept graph wikilinks.
- **Smart Noise & Copyright Filtering**: Automatically detects and skips publisher copyright pages, empty title pages, redundant in-book TOCs, and broken internal XHTML anchors. Use `--keep-all` if you prefer to retain them.
- **Sequential Indexing**: Consecutively numbers chapters (`01_xxx.md`, `02_xxx.md`) without missing-number gaps.
- **YAML Frontmatter Injection**: Embeds structured metadata into every chapter header (`book`, `author`, `chapter_index`, `word_count`, `read_time`, `tags`) — tailored for Obsidian and Notion property databases.
- **Prev / Next Chapter Navigation**: Adds bidirectional `⬅️ Previous Chapter | 📑 Table of Contents | ➡️ Next Chapter` links at the bottom of every page with rock-solid relative paths (`./01_xxx.md`).
- **Image & Asset Extraction**: Automatically exports book covers, diagrams, and illustrations to `./assets/` and updates relative paths (`![](./assets/xxx.png)`).

---

## 🧩 Sub-skills Ecosystem (子技能生态)

```mermaid
flowchart LR
    EPUB[EPUB eBook] --> Main[Book Distiller Engine]
    Main --> Chapters[Flat Markdown Chapters]
    Chapters --> S1[Sub-skill: extract-insights]
    S1 --> Master[insights/ Master Libraries]
    Master --> S2[Sub-skill: book-review]
    Chapters --> S2
    S2 --> Reviews[reviews/ Multi-platform Posts]
    S2 --> Provenance[🧬 Full Lineage & Provenance Graph]
```

### 1. `extract-insights` (写作黄金原料库与灵感总库)

Refuses generic summaries. Focuses purely on extracting high-yield creator assets from any extracted chapter `.md`:
1. ⚡️ **Contrarian Hooks (反直觉认知)**: Common misconception vs deep counter-intuitive insight + 3 social hook variations + **Viral Rating (1-5 ⭐)**.
2. 📖 **Stories & Micro-cases (故事与微案例)**: Concrete character, conflict, key turning point, and core takeaway.
3. 🛠️ **Actionable Checklists (可落地微清单)**: 3-step execution framework + 1 "Never Do" boundary.
4. 💎 **Golden Quotes (高穿透金句)**: Emotionally resonant quotes with recommended social media usage contexts.
5. 🔗 **Obsidian Wikilinks**: Embeds `[[Concept]]` links for interactive graph visualization.
6. 🎯 **Symptom Mapping**: Connects reader pain points directly to the book's chapter solutions.

### 2. `book-review` (高穿透读后感与完整血统溯源)

Transforms raw book material into ready-to-publish social media book reviews:
- 📱 **Xiaohongshu (RED)**: Dual-line hook title + relatable life struggle + 3 core epiphany points + aesthetic cards.
- 🧵 **Threads / X**: 4-post mental flow (1/4 Hook ➔ 2/4 Mindset Inversion ➔ 3/4 Actionable Habit ➔ 4/4 Warm Closing), strictly under 500 characters per post.
- 📰 **WeChat Official Account / Blog**: Deep reflective prose linking everyday scenarios to the book's foundational philosophy.
- 🧬 **Lineage & Provenance Blueprint**: Every review includes a Mermaid design graph, an element-by-element source lineage table, and concept wikilinks.

---

## 🚀 Installation & Setup

### 1. Requirements

- Python 3.10+
- Dependencies: `pip install ebooklib beautifulsoup4 markdownify lxml`

### 2. Manual CLI Usage

```bash
# 1. Standard flat clean extraction
python3 scripts/extract_chapters.py "/path/to/book.epub"

# 2. Setup the 4 master insights libraries for an extracted book
python3 scripts/extract_insights.py "/path/to/extracted_book_folder"

# 3. Generate book review scaffolding with full provenance graph
python3 scripts/generate_review.py "/path/to/extracted_book_folder" --platform all --topic "职场内耗与边界感"
```

### 3. Agent Skill Integration

Clone this repository into your agent's skill directory:

```bash
# For Antigravity / Claude Code
git clone https://github.com/ubworkshop/book-distiller.git ~/.gemini/config/skills/book-distiller
```

## 📂 Output Structure

```text
Book_Notes/
├── README.md                                 # Book metadata and clickable table of contents
├── SUMMARY.md                                # Sidebar index (Obsidian / GitBook compatible)
├── assets/                                   # Extracted images, illustrations, and cover
│   ├── cover.jpg
│   └── figure_01.png
├── 01_Introduction.md
├── 02_Part1_My_Journey_Crossing_the_Threshold.md
├── 03_Part2_Life_Principles_Embrace_Reality.md
├── insights/                                 # 👈 Sub-skill: extract-insights
│   ├── 00_全书爆款选题与反直觉库.md            # (含 🔥 Top 5 必爆黄金选题置顶)
│   ├── 00_全书高穿透金句大全.md                # (带社交发帖语境)
│   ├── 00_读者现实痛点与对号入座索引.md         # (现实烦恼 -> 章节解法映射)
│   ├── 00_全书核心概念与思维模型图谱.md         # (Obsidian [[概念双链]])
│   ├── 01_Introduction_原料卡.md
│   └── ...
└── reviews/                                  # 👈 Sub-skill: book-review
    ├── review_xhs_20261005_120000.md        # 小红书高赞图文 + 🧬 完整血统溯源
    ├── review_threads_20261005_120000.md    # Threads 4 帖心流 + 🧬 完整血统溯源
    └── review_wechat_20261005_120000.md     # 公众号深度随笔 + 🧬 完整血统溯源
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
