# Book Distiller (书籍蒸馏器)

> Precise chapter-by-chapter EPUB extraction to clean, flat Markdown documents with modular sub-skills (extract-insights: 1-page executive summary + 4D raw materials + Obsidian graph + caching/incremental sync; book-review: review matrix planning + 4-stage modular mental flow menu + semantic slug naming + dual-file clean post and full provenance graph), smart noise filtering, YAML frontmatter, image assets, and structured indexes.

An Agent Skill for parsing and splitting `.epub` ebooks into clean, standalone Markdown chapters, preserving image assets and hierarchy, building `README.md` and `SUMMARY.md` catalogs for Obsidian, Notion, or GitBook, extracting creator insights with caching, generating a 1-page executive briefing memo, and orchestrating a multi-article content matrix pipeline with a 4-stage mental flow builder.

## ✨ Features

- **Strictly Flat Directory Structure**: All chapters are extracted side-by-side into a single folder. No confusing nested directories or broken relative links.
- **Modular Sub-skills (Advanced Creator Suite v3.1)**:
  - 📑 **`1-Page Executive Summary (全书一页纸决策简报)`**: Automatically generates `00_全书一页纸决策简报.md` containing the core thesis, top 3 contrarian truths, author's logic architecture (Mermaid flowchart), reader fit diagnosis (who should read vs who shouldn't), anchor quotes, and actionable creator angles.
  - ⚡️ **`extract-insights` (with Incremental Caching)**: Extracts Contrarian Hooks (with 1-5 ⭐ viral ratings and 🔥 Top 5 pinned topics), Concrete Stories/Cases, Actionable Checklists, High-resonance Quotes, Obsidian Concept Graph (`[[Wikilinks]]`), and Symptom Mapping. Automatically skips previously completed chapters and supports `--sync` incremental aggregation.
  - 🗺️ **`Review Matrix Planning`**: Automatically plans a 4-6 post strategic content matrix (`00_全书书评创作矩阵规划.md`) for the whole book covering viral hooks, mindset inversions, long-form essays, and actionable tools across Xiaohongshu, Threads, and WeChat.
  - 🧩 **`4-Stage Mental Flow Selector`**: Presents an inspiration menu across 4 key flow stages (Hook ➔ Inversion ➔ Action ➔ Ending), allowing creators to freely mix-and-match modular building blocks (e.g. `1B + 2A + 3A + 4A`).
  - 🏷️ **`Semantic Slug Dual-file Output`**: 
    - `review_{platform}_{slug}_{timestamp}.md`: 100% clean, publish-ready post with human-readable semantic topic slug.
    - `review_{platform}_{slug}_{timestamp}_provenance.md`: Standalone design provenance archive with Mermaid flow chart, source lineage table, and concept wikilinks.
- **Smart Noise & Copyright Filtering**: Automatically detects and skips publisher copyright pages, empty title pages, redundant in-book TOCs, and broken internal XHTML anchors. Use `--keep-all` if you prefer to retain them.
- **Sequential Indexing**: Consecutively numbers chapters (`01_xxx.md`, `02_xxx.md`) without missing-number gaps.
- **YAML Frontmatter Injection**: Embeds structured metadata into every chapter header (`book`, `author`, `chapter_index`, `word_count`, `read_time`, `tags`).
- **Prev / Next Chapter Navigation**: Adds bidirectional `⬅️ Previous Chapter | 📑 Table of Contents | ➡️ Next Chapter` links at the bottom of every page with rock-solid relative paths (`./01_xxx.md`).
- **Image & Asset Extraction**: Automatically exports book covers, diagrams, and illustrations to `./assets/` and updates relative paths (`![](./assets/xxx.png)`).

---

## 🧩 Sub-skills Ecosystem (子技能生态)

```mermaid
flowchart LR
    EPUB[EPUB eBook] --> Main[Book Distiller Engine]
    Main --> Chapters[Flat Markdown Chapters]
    Chapters --> S1[Sub-skill: extract-insights]
    S1 --> Brief[00_全书一页纸决策简报.md]
    S1 --> Master[insights/ Master Libraries (Cached)]
    Master --> S2[Sub-skill: book-review]
    Chapters --> S2
    S2 --> Matrix[Review Matrix: 4-6 Topics Planning]
    Matrix --> Menu[4-Stage Flow Modular Menu]
    Menu --> Custom[Creator Mix & Match]
    Custom --> Post[review_platform_slug.md: Clean Post]
    Custom --> Prov[review_platform_slug_provenance.md: Full Provenance]
```

---

## 🚀 Installation & Setup

### 1. Requirements

- Python 3.10+
- Dependencies: `pip install ebooklib beautifulsoup4 markdownify lxml`

### 2. Manual CLI Usage

```bash
# 1. Standard flat clean extraction
python3 scripts/extract_chapters.py "/path/to/book.epub"

# 2. Setup the 4 master insights libraries and generate the 1-page executive summary
python3 scripts/extract_insights.py "/path/to/extracted_book_folder"

# 3. Plan the 4-6 review topics matrix for the entire book
python3 scripts/generate_review.py "/path/to/extracted_book_folder" --matrix

# 4. Generate post with semantic slug and 4-stage flow combination
python3 scripts/generate_review.py "/path/to/extracted_book_folder" --platform xhs --topic "精力管理与停止内耗" --combo "1B+2A+3A+4A"
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
├── README.md                                                 # Book metadata and clickable table of contents
├── SUMMARY.md                                                # Sidebar index (Obsidian / GitBook compatible)
├── 00_全书一页纸决策简报.md                                    # 👈 1-page executive briefing memo
├── assets/                                                   # Extracted images, illustrations, and cover
├── 01_Introduction.md
├── 02_Part1_My_Journey_Crossing_the_Threshold.md
├── 03_Part2_Life_Principles_Embrace_Reality.md
├── insights/                                                 # 👈 Sub-skill: extract-insights (Incremental Caching)
│   ├── 00_全书爆款选题与反直觉库.md
│   ├── 00_全书高穿透金句大全.md
│   ├── 00_读者现实痛点与对号入座索引.md
│   ├── 00_全书核心概念与思维模型图谱.md
│   └── 02_Part1_My_Journey_原料卡.md
└── reviews/                                                  # 👈 Sub-skill: book-review (Review Matrix & Flows)
    ├── 00_全书书评创作矩阵规划.md                               # 👈 4-6 topics content planning matrix
    ├── flow_menu_20261006_120000.md                          # 👈 4-Stage Flow Modular Menu
    ├── review_xhs_精力管理与停止内耗_20261006_120000.md          # 👈 Clean post with semantic topic slug
    └── review_xhs_精力管理与停止内耗_20261006_120000_provenance.md # 👈 Full design provenance & Mermaid graph
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
