# Obsidian 研究用ボールト（公開スターター）

GNN 関連の論文リスト [naganandy/graph-based-deep-learning-literature](https://github.com/naganandy/graph-based-deep-learning-literature) をローカルに置き、Obsidian 上で読書ノートを増やすための最小構成です。**Community プラグイン「Templater」を `.obsidian` にバンドル済みで、テンプレートフォルダは `Templates/` に設定しています。**初回は Obsidian の信頼確認やコミュニティプラグインの有効化を求められることがあります。その他のプラグインは各自で追加してください。`workspace.json` など端末依存のファイルは `.gitignore` で除外しています。

## 前提

- Obsidian をインストール済みであること
- Python 3 が入っていること（`process_papers.py` / `refetch_bibtex.py` 用。標準ライブラリのみで動きます）
- Git が使えること（文献リポジトリの取得とスクリプト内の `git pull` 用）

## セットアップ

1. このリポジトリを clone し、**フォルダごと Obsidian の「ボールトとして開く」**で開く。
2. **同じボールトのルート**（`README.md` と並ぶ）に、文献リポジトリを clone する。

```bash
cd /path/to/このボールトのルート
git clone https://github.com/naganandy/graph-based-deep-learning-literature.git
```

フォルダ名は `graph-based-deep-learning-literature` のままにしてください（スクリプトがこの名前を参照します）。`.gitignore` で無視されるため、clone した文献はこの公開リポジトリにはコミットされません。

3. **設定 → コミュニティプラグイン** でセーフモードをオフにし、**Templater** が有効か確認する（無効ならオン）。バンドルしているバージョンは `.obsidian/plugins/templater-obsidian/manifest.json` の `version` を参照。

## ディレクトリの役割

| パス | 説明 |
|------|------|
| `.obsidian/` | Templater のみリポジトリに含む（`main.js` / `manifest.json` / `data.json` など）。作業レイアウト用の `workspace.json` は含めない |
| `Templates/Paper_Template.md` | 論文ノート生成時にスクリプトが読むテンプレート |
| `Templates/Monthly_Note_Template.md` | 月報用（Templater 構文あり） |
| `Templates/Monthly_Report_Package_Template.md` | 月次進捗報告資料フォルダ用インデックス（Templater 構文あり） |
| `Templates/Monthly_Note_Template_plain.md` | Templater なしの月報のたたき台 |
| `Papers/` | スクリプトが生成する論文ノートの出力先 |
| `Daily_Notes/YYYY/YYYY-MM_MonthlyReview.md` | 月報の置き場（ファイルは各自が作成） |
| `Research_Projects/進行中/` | 進行中プロジェクト用。月報テンプがここ配下の `.md` を列挙します |
| `Research_Projects/進捗報告資料/` | 月次発表用スライド・PDF 等の置き場（説明は `README.md`） |

## 論文ノートの生成

文献リポジトリを更新したあと、ボールトのルートで次を実行します。

```bash
python3 scripts/process_papers.py
```

- 文献側で `git pull` し、更新がなければ処理を終了します。
- 更新がある場合のみ、`Papers/` 以下に新規 Markdown を作成します。

BibTeX だけ既存ノートに補完したい場合（任意）:

```bash
python3 scripts/refetch_bibtex.py
```

## 月報の作り方（Templater）

1. コマンドパレットから Templater の「テンプレートの挿入」等で `Templates/Monthly_Note_Template.md` を適用する。
2. 生成した内容を `Daily_Notes/YYYY/YYYY-MM_MonthlyReview.md` として保存する（年フォルダがなければ作成する）。

`Monthly_Report_Package_Template.md` は `Research_Projects/進捗報告資料/YYYY/YYYY-MM/README.md` として使う想定です。該当する月のフォルダを自分で作ってからテンプレートを当ててください。

## 起動時に月報を自動で開く設定について

ボールト起動時に月報を作成・追記する Templater 用スクリプトは、プラグインと組み合わせた高度な設定になるため **このリポジトリには含めていません**。説明会や資料で案内するか、各自の環境で QuickAdd などと組み立ててください。

## クレジット

- 論文メタデータの出典: [naganandy/graph-based-deep-learning-literature](https://github.com/naganandy/graph-based-deep-learning-literature)
- Templater プラグイン: [SilentVoid13/Templater](https://github.com/SilentVoid13/Templater)（同棲ファイルの著作権はプラグイン作者側のライセンスに従います）
- 本リポジトリ内のテンプレート・スクリプト（Templater 除く）のライセンスは [LICENSE](LICENSE) に記載（文献リポジトリ本体とは別物）。

## ライセンス

リポジトリ内の独自ファイルは MIT License（[LICENSE](LICENSE)）です。生成された論文ノートや個人の月報の内容の権利は、それぞれの作成者にあります。
