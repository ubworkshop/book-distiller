---
name: book-distiller/extract-insights
description: 从 book-distiller 提取出来的章节 Markdown 文档中，精准提炼供自媒体与内容创作使用的 4 类"黄金原料"（反直觉认知、故事微案例、可落地微清单、高穿透金句）。支持断点续传与增量合并、Obsidian 概念双链图谱生成、自媒体爆款潜力评分（🔥Top选题排序）与读者现实痛点对号入座索引。拒绝平庸的全文大意总结，直接输出为可写成 Threads、小红书图文、公众号长文的高价值素材卡片与全书灵感库。触发场景：用户提到"提取黄金原料"、"提取写作素材"、"提炼章节洞察"、"批量提取全书原料"、"断点续传提取"、"增量同步总库"、"extract insights"等。
---

# 章节黄金原料提取子技能 (Sub-skill: extract-insights v3.0 断点续传与增量版)

本子技能作为 `book-distiller` 的专属创作下游，专注于将电子书的各个独立章节（`.md`）深度萃取为**高价值的创作者素材卡片与全书灵感图谱库**。

## 核心能力

1. **⚡️ 4+2 黄金原料提炼**：
   - ⚡️ **反直觉认知与爆款评级**（1~5 星爆款潜质打分）
   - 📖 **故事与微案例**（论据素材）
   - 🛠️ **可落地微清单**（读者收藏向）
   - 💎 **穿透金句**（配图与发帖金句）
   - 🎯 **读者现实痛点对号入座**
   - 🧠 **概念双链图谱**（Obsidian `[[概念双链]]`）
2. **🔄 断点续传与增量缓存 (Caching & Incremental Extraction)**：
   - 自动检测已有原料卡，跳过已完成章节，避免重复消耗资源；
   - 支持 `--sync` 一键从所有已有原料卡中去重增量汇聚更新四大全书总库！

---

## 常用终端命令

```bash
# 1. 为书籍目录初始化写作原料库与章节卡片（自动断点续传跳过已完成卡片）
python3 scripts/extract_insights.py "/path/to/book_output"

# 2. 强制覆盖所有卡片重新生成
python3 scripts/extract_insights.py "/path/to/book_output" --force

# 3. 仅增量同步汇总已有卡片至四大总库
python3 scripts/extract_insights.py "/path/to/book_output" --sync
```
