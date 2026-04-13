---
month_id: "<% tp.date.now('YYYY-MM') %>"
year: "<% tp.date.now('YYYY') %>"
tags: [monthly, progress]
progress_review_last_date: ""
progress_review_interval_days: 7
---

# 月報: <% tp.date.now('YYYY-MM') %>

## 今月の主要目標

- [ ]

## 今月やること

- [ ]

## 今月の成果物

- [ ]

## いまは着手しないこと

- [ ]

## 週次進捗管理

- 最終実施日: `progress_review_last_date`
- [ ] 進捗管理を実施したら、月報 frontmatter の `progress_review_last_date` を今日の日付に更新する
