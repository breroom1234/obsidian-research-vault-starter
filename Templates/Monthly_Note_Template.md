---
month_id: "<% tp.date.now('YYYY-MM') %>"
year: "<% tp.date.now('YYYY') %>"
tags: [monthly, progress]
progress_review_last_date: ""
progress_review_interval_days: 7
---

# 月報: <% tp.date.now('YYYY-MM') %>

## 🎯 今月の主要目標

- [ ]

## 今月アクティブにする project

<%*
const projectFiles = tp.app.vault.getMarkdownFiles()
  .filter(file => /^Research_Projects\/進行中\/[^/]+\/[^/]+\.md$/.test(file.path))
  .sort((a, b) => a.basename.localeCompare(b.basename, "ja"));

if (projectFiles.length === 0) {
  tR += "- [ ]";
} else {
  tR += projectFiles
    .map(file => `- [ ] [[${file.path.replace(/\.md$/, "")}|${file.basename}]]`)
    .join("\n");
}
%>

## 今月の成果物

- [ ]

## 今月の進捗報告資料

- [[Research_Projects/進捗報告資料/<% tp.date.now('YYYY') %>/<% tp.date.now('YYYY-MM') %>/README|<% tp.date.now('YYYY-MM') %> 進捗資料]]

## いまは着手しないこと

- [ ]

## 週次進捗管理（Cursor）

- 最終実施日: `progress_review_last_date`
- [ ] 進捗管理を実施したら、月報 frontmatter の `progress_review_last_date` を今日の日付に更新する
