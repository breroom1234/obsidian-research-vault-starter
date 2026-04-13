# Obsidian 研究用ボールト（公開スターター）

GNN 関連の論文リスト [naganandy/graph-based-deep-learning-literature](https://github.com/naganandy/graph-based-deep-learning-literature) をローカルに置き、Obsidian 上で読書ノートを増やすための最小構成です。Community プラグイン `Templater` は `.obsidian` に含めてあり、テンプレートフォルダは `Templates/` に設定済みです。初回は Obsidian 側で信頼確認やコミュニティプラグインの有効化を求められることがあります。`workspace.json` など端末依存のファイルは含めていません。

## 前提

- Obsidian をインストール済みであること
- Python 3 が入っていること
- Git が使えること

`process_papers.py` と `refetch_bibtex.py` は標準ライブラリのみで動きます。

## セットアップ

1. このリポジトリを clone し、フォルダごと Obsidian のボールトとして開く。
2. 同じボールトのルートに、文献リポジトリを clone する。

```bash
cd /path/to/このボールトのルート
git clone https://github.com/naganandy/graph-based-deep-learning-literature.git
```

フォルダ名は `graph-based-deep-learning-literature` のままにしてください。`scripts/process_papers.py` がこの名前を前提に参照します。`.gitignore` で無視されるため、clone した文献はこの公開リポジトリにはコミットされません。

3. Obsidian の `設定 -> コミュニティプラグイン` でセーフモードをオフにし、`Templater` が有効か確認する。

バンドルしている Templater のバージョンは `.obsidian/plugins/templater-obsidian/manifest.json` の `version` を参照してください。

## ディレクトリの役割

| パス | 説明 |
|------|------|
| `.obsidian/` | `Templater` の最小設定のみを含む。`workspace.json` など端末依存ファイルは含めない |
| `Templates/Paper_Template.md` | 論文ノート生成時にスクリプトが読むテンプレート |
| `Templates/Monthly_Note_Template.md` | 月報用テンプレート（Templater 構文あり） |
| `Templates/Monthly_Note_Template_plain.md` | Templater なしでも使える月報のたたき台 |
| `Papers/` | スクリプトが生成する論文ノートの出力先 |
| `Daily_Notes/YYYY/YYYY-MM_MonthlyReview.md` | 月報の置き場 |

## 論文ノートの生成

文献リポジトリを更新したあと、ボールトのルートで次を実行します。

```bash
python3 scripts/process_papers.py
```

- 文献側で `git pull` し、更新がなければ処理を終了します。
- 更新がある場合のみ、`Papers/` 以下に新規 Markdown を作成します。

BibTeX だけ既存ノートに補完したい場合:

```bash
python3 scripts/refetch_bibtex.py
```

## 月報の作り方

1. コマンドパレットから Templater のテンプレート挿入を実行し、`Templates/Monthly_Note_Template.md` を適用する。
2. 生成した内容を `Daily_Notes/YYYY/YYYY-MM_MonthlyReview.md` として保存する。

## 起動時に月報を自動で開く設定について

起動時に月報を自動作成・追記する Templater 用スクリプトは、このリポジトリには含めていません。必要なら説明会用資料や各自の QuickAdd 設定などで追加してください。

## クレジット

- 論文メタデータの出典: [naganandy/graph-based-deep-learning-literature](https://github.com/naganandy/graph-based-deep-learning-literature)
- Templater プラグイン: [SilentVoid13/Templater](https://github.com/SilentVoid13/Templater)
- このリポジトリ内の独自テンプレートとスクリプトのライセンスは [LICENSE](LICENSE) に記載しています

## ライセンス

このリポジトリ内の独自ファイルは MIT License（[LICENSE](LICENSE)）です。生成された論文ノートや個人の月報の内容の権利は、それぞれの作成者にあります。
