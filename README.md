# epub-to-markdown

> Precise chapter-by-chapter EPUB extraction to clean Markdown documents with YAML frontmatter, nested directories, image assets, and structured indexes.

An Agent Skill for parsing and splitting `.epub` ebooks into clean, standalone Markdown chapters, preserving image assets and hierarchy, and building `README.md` and `SUMMARY.md` catalogs for Obsidian, Notion, or GitBook.

## ✨ Features

- **Smart Chapter Extraction**: Splits content following the EPUB Spine reading order without cutting chapters in half.
- **Nested Directory Structure (`--nested`)**: Automatically detects book parts, volumes, and sections, grouping chapters into dedicated subfolders.
- **YAML Frontmatter Injection**: Embeds structured metadata into every chapter header (`book`, `author`, `chapter_index`, `word_count`, `read_time`, `tags`) — tailored for Obsidian and Notion property databases.
- **Prev / Next Chapter Navigation**: Adds bidirectional `⬅️ Previous Chapter | 📑 Table of Contents | ➡️ Next Chapter` links at the bottom of every page.
- **Image & Asset Extraction**: Automatically exports book covers, diagrams, and illustrations to `assets/` and updates relative paths (`![](./assets/xxx.png)` or `![](../assets/xxx.png)`).
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
# Standard flat extraction (creates a folder named after the book in the current directory)
python3 scripts/extract_chapters.py "/path/to/book.epub"

# Multi-level nested directory mode (groups by Parts/Volumes)
python3 scripts/extract_chapters.py "/path/to/book.epub" --nested

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
- *"Convert this EPUB into markdown files by chapter with nested folders"*

## 📂 Output Structure

```text
Book_Notes/
├── README.md               # Book metadata and clickable table of contents
├── SUMMARY.md              # Sidebar index (Obsidian / GitBook compatible)
├── assets/                 # Extracted images, illustrations, and cover
│   ├── cover.jpg
│   └── figure_01.png
├── Part_01_Where_I_Am_Coming_From/
│   ├── 01_My_Call_to_Adventure.md
│   └── 02_Crossing_the_Threshold.md
├── Part_02_Life_Principles/
│   ├── 03_Embrace_Reality.md
│   └── 04_Use_the_5-Step_Process.md
└── 00_Front_Matter.md
```

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
