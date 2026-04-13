# Obsidian 研究用ボールト（公開スターター）

GNN 関連の論文リスト [naganandy/graph-based-deep-learning-literature](https://github.com/naganandy/graph-based-deep-learning-literature) をローカルに置き、Obsidian 上で読書ノートを増やすための最小構成です。テンプレートと Python スクリプトだけを共有し、**`.obsidian`（プラグイン設定）は含めていません**。Community プラグインのインストールと設定は各自の環境で行ってください。

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

3. （任意）Templater を使う場合: Obsidian の **設定 → Community plugins** で **Templater** を有効化する。リポジトリにプラグインの設定 JSON は含めていません。

## ディレクトリの役割

| パス | 説明 |
|------|------|
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

## 月報の作り方（Templater 利用時）

1. Templater を有効化する。
2. コマンドパレットから Templater の「テンプレートを挿入」など、普段使っている手順で `Templates/Monthly_Note_Template.md` を適用する。
3. 生成した内容を `Daily_Notes/YYYY/YYYY-MM_MonthlyReview.md` として保存する（年フォルダがなければ作成する）。

`Monthly_Report_Package_Template.md` は `Research_Projects/進捗報告資料/YYYY/YYYY-MM/README.md` として使う想定です。該当する月のフォルダを自分で作ってからテンプレートを当ててください。

## 起動時に月報を自動で開く設定について

ボールト起動時に月報を作成・追記する Templater 用スクリプトは、プラグインと組み合わせた高度な設定になるため **このリポジトリには含めていません**。説明会や資料で案内するか、各自の環境で QuickAdd などと組み立ててください。

## クレジット

- 論文メタデータの出典: [naganandy/graph-based-deep-learning-literature](https://github.com/naganandy/graph-based-deep-learning-literature)
- 本リポジトリ内のテンプレート・スクリプトのライセンスは [LICENSE](LICENSE) に記載しています（文献リポジトリ本体とは別物です）。

## ライセンス

リポジトリ内の独自ファイルは MIT License（[LICENSE](LICENSE)）です。生成された論文ノートや個人の月報の内容の権利は、それぞれの作成者にあります。
