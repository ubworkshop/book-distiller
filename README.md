# epub-to-markdown

> Precise chapter-by-chapter EPUB extraction to clean, flat Markdown documents with modular sub-skills (e.g. 4-dimensional writing insights extraction), smart noise filtering, YAML frontmatter, image assets, and structured indexes.

An Agent Skill for parsing and splitting `.epub` ebooks into clean, standalone Markdown chapters, preserving image assets and hierarchy, and building `README.md` and `SUMMARY.md` catalogs for Obsidian, Notion, or GitBook.

## ✨ Features

- **Strictly Flat Directory Structure**: All chapters are extracted side-by-side into a single folder. No confusing nested directories or broken relative links.
- **Modular Sub-skills Support**: Built-in `subskills/extract-insights` to distill chapters into actionable raw materials for content creation (Hooks, Stories, Checklists, Golden Quotes).
- **Smart Noise & Copyright Filtering**: Automatically detects and skips publisher copyright pages, empty title pages, redundant in-book TOCs, and broken internal XHTML anchors. Use `--keep-all` if you prefer to retain them.
- **Sequential Indexing**: Consecutively numbers chapters (`01_xxx.md`, `02_xxx.md`) without missing-number gaps.
- **YAML Frontmatter Injection**: Embeds structured metadata into every chapter header (`book`, `author`, `chapter_index`, `word_count`, `read_time`, `tags`) — tailored for Obsidian and Notion property databases.
- **Prev / Next Chapter Navigation**: Adds bidirectional `⬅️ Previous Chapter | 📑 Table of Contents | ➡️ Next Chapter` links at the bottom of every page with rock-solid relative paths (`./01_xxx.md`).
- **Image & Asset Extraction**: Automatically exports book covers, diagrams, and illustrations to `./assets/` and updates relative paths (`![](./assets/xxx.png)`).

---

## 🧩 Sub-skills (子技能)

### `extract-insights` (4 类写作黄金原料提取)

Refuses generic summaries. Focuses purely on extracting high-yield creator assets from any extracted chapter `.md`:
1. ⚡️ **Contrarian Hooks (反直觉认知)**: Common misconception vs deep counter-intuitive insight + 3 social hook variations.
2. 📖 **Stories & Micro-cases (故事与微案例)**: Concrete character, conflict, key turning point, and core takeaway.
3. 🛠️ **Actionable Checklists (可落地微清单)**: 3-step execution framework + 1 "Never Do" boundary.
4. 💎 **Golden Quotes (高穿透金句)**: Emotionally resonant quotes with recommended social media usage contexts.

---

## 🚀 Installation & Setup

### 1. Requirements

- Python 3.10+
- Dependencies: `pip install ebooklib beautifulsoup4 markdownify lxml`

### 2. Manual CLI Usage

```bash
# 1. Standard flat clean extraction
python3 scripts/extract_chapters.py "/path/to/book.epub"

# 2. Retain all pages including publisher front/back matter
python3 scripts/extract_chapters.py "/path/to/book.epub" --keep-all

# 3. Setup insights workspace for an extracted book
python3 scripts/extract_insights.py "/path/to/extracted_book_folder"
```

### 3. Agent Skill Integration

Clone this repository into your agent's skill directory:

```bash
# For Antigravity / Claude Code
git clone https://github.com/ubworkshop/epub-to-markdown.git ~/.gemini/config/skills/epub-to-markdown
```

Then trigger via natural language:
- *"Extract all chapters from this book: `Principles.epub`"*
- *"Extract the 4 golden writing insights from `02_My_Journey.md`"*

## 📂 Output Structure

```text
Book_Notes/
├── README.md               # Book metadata and clickable table of contents
├── SUMMARY.md              # Sidebar index (Obsidian / GitBook compatible)
├── assets/                 # Extracted images, illustrations, and cover
│   ├── cover.jpg
│   └── figure_01.png
├── 01_Introduction.md
├── 02_Part1_My_Journey_Crossing_the_Threshold.md
├── 03_Part2_Life_Principles_Embrace_Reality.md
└── insights/               # 👈 Generated via extract-insights sub-skill
    ├── 00_全书爆款选题与反直觉库.md
    └── 00_全书高穿透金句大全.md
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
