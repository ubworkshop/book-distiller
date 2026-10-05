# epub-to-markdown

> Precise chapter-by-chapter EPUB extraction to clean, flat Markdown documents with smart noise filtering, YAML frontmatter, image assets, and structured indexes.

An Agent Skill for parsing and splitting `.epub` ebooks into clean, standalone Markdown chapters, preserving image assets and hierarchy, and building `README.md` and `SUMMARY.md` catalogs for Obsidian, Notion, or GitBook.

## ✨ Features

- **Strictly Flat Directory Structure**: All chapters are extracted side-by-side into a single folder. No confusing nested directories or broken relative links.
- **Smart Noise & Copyright Filtering**: Automatically detects and skips publisher copyright pages, empty title pages, redundant in-book TOCs, and broken internal XHTML anchors. Use `--keep-all` if you prefer to retain them.
- **Sequential Indexing**: Consecutively numbers chapters (`01_xxx.md`, `02_xxx.md`) without missing-number gaps.
- **Volume & Section Identification**: If a book has parts/volumes, section names are cleanly incorporated into filenames (e.g. `02_Part1_My_Journey_Chapter1.md`) without creating subfolders.
- **YAML Frontmatter Injection**: Embeds structured metadata into every chapter header (`book`, `author`, `chapter_index`, `word_count`, `read_time`, `tags`) — tailored for Obsidian and Notion property databases.
- **Prev / Next Chapter Navigation**: Adds bidirectional `⬅️ Previous Chapter | 📑 Table of Contents | ➡️ Next Chapter` links at the bottom of every page with rock-solid relative paths (`./01_xxx.md`).
- **Image & Asset Extraction**: Automatically exports book covers, diagrams, and illustrations to `./assets/` and updates relative paths (`![](./assets/xxx.png)`).
- **Clean Markdown Formatting**: Strips inline styles, redundant scripts, and HTML tags while retaining standard headings (ATX), blockquotes, lists, and bold/italic text.
- **Automated Catalog Indexes**:
  - `README.md`: Contains book metadata (title, author, description) and a clickable table of contents.
  - `SUMMARY.md`: Compatible with GitBook and mdBook sidebar navigation.

## 🚀 Installation & Setup

### 1. Requirements

- Python 3.10+
- Dependencies: `pip install ebooklib beautifulsoup4 markdownify lxml`

### 2. Manual CLI Usage

```bash
# Standard flat clean extraction (filters out copyright noise)
python3 scripts/extract_chapters.py "/path/to/book.epub"

# Retain all pages including publisher front/back matter
python3 scripts/extract_chapters.py "/path/to/book.epub" --keep-all

# Custom output directory
python3 scripts/extract_chapters.py "/path/to/book.epub" -o "./my_book_notes"

# Skip image extraction (text only)
python3 scripts/extract_chapters.py "/path/to/book.epub" --no-images
```

### 3. Agent Skill Integration

Clone this repository into your agent's skill directory:

```bash
# For Antigravity / Claude Code
git clone https://github.com/ubworkshop/epub-to-markdown.git ~/.gemini/config/skills/epub-to-markdown
```

Then trigger via natural language:
- *"Extract all chapters from this book: `Principles.epub`"*
- *"Convert this EPUB into markdown files by chapter"*

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
└── ...
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
