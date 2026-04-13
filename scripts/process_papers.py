import os
import re
from datetime import datetime # Added for last_updated
import subprocess # subprocessモジュールをインポート
import argparse # argparseモジュールをインポート
from category_normalization_rules import CATEGORY_NORMALIZATION_MAP # 外部ルールをインポート
# shutil is not used, os.makedirs is sufficient

# --- 設定箇所 ---
# Obsidian Vault のルート（このリポジトリを vault として開いたときは変更不要）
OBSIDIAN_VAULT_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# クローンしたリポジトリのルートパス
REPO_ROOT_PATH = os.path.join(OBSIDIAN_VAULT_BASE_PATH, "graph-based-deep-learning-literature")
# 論文を格納するObsidian内のディレクトリ
PAPERS_DIR_OBSIDIAN = os.path.join(OBSIDIAN_VAULT_BASE_PATH, "Papers")
# 論文ノートのテンプレートファイル
PAPER_TEMPLATE_PATH = os.path.join(OBSIDIAN_VAULT_BASE_PATH, "Templates", "Paper_Template.md")
# --- 設定箇所ここまで ---

# GitHubリポジトリのベースURL (パス変換用)
GITHUB_REPO_BASE_URL = "https://github.com/naganandy/graph-based-deep-learning-literature/blob/master/"
GITHUB_REPO_BASE_URL_ESCAPED = re.escape(GITHUB_REPO_BASE_URL) # Pre-escaped URL

PAPER_LINK_REGEX = re.compile(
    rf"(^-\s*\[(?P<title_from_list>.+?)\]\((?:{GITHUB_REPO_BASE_URL_ESCAPED})?"
    rf"(?P<paper_readme_repo_path>conference-publications/folders/years/\d{{4}}(?:_and_Earlier)?/publications_([a-zA-Z0-9_-]+?)/+([a-zA-Z0-9_-]+?)/README\.md)\))"
)

# --- Helper functions from refetch_bibtex.py ---
def extract_bibtex_from_repo_readme(readme_content):
    """Extracts BibTeX from a ```bibtex ... ``` code block in repository README content."""
    if not readme_content:
        return None
    # Regex to find BibTeX block, looking for @type{key, ... entry
    # First, try the standard markdown code block
    standard_block_match = re.search(r"```(?:bibtex)?\s*\n(@(?:inproceedings|article|book|misc|unpublished)\{[^\}]+\}[^`]*?)\n```", readme_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if standard_block_match:
        return standard_block_match.group(1).strip()

    # If standard block fails, try to find a raw BibTeX entry that might not be in a perfectly formed block
    # This is more greedy and looks for any line starting with @type{key... and captures until its balancing }
    # It assumes the BibTeX entry is reasonably well-formed itself.
    # Modified to be less greedy and handle nested braces better, common in BibTeX.
    # This regex looks for a structure like @type{key, ... fields ... }
    # It tries to match balanced curly braces for the main entry.
    raw_bibtex_match = re.search(
        r"^(@(?:inproceedings|incollection|article|book|misc|unpublished)\s*\{[^\s,]+?,.*?^\})",
        readme_content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    if raw_bibtex_match:
        return raw_bibtex_match.group(0).strip() # group(0) to get the whole match

    return None

def is_bibtex_valid(bibtex_str):
    """Checks if the BibTeX string appears to be a valid, non-empty entry."""
    if not bibtex_str or not bibtex_str.strip():
        return False
    # Simple check: starts with @, contains {, }, and is of reasonable length
    s = bibtex_str.strip()
    return s.startswith("@") and "{" in s and "}" in s and len(s) > 15
# --- End of helper functions ---

# --- グローバル変数 ---
DEBUG_YEAR_TARGET = None
DEBUG_LOG_FILE_HANDLER = None

def debug_print(message, year_of_message=None):
    """デバッグ年が指定され、かつ現在のメッセージの年と一致する場合、ファイルに書き出す。それ以外はコンソールに出力。"""
    global DEBUG_YEAR_TARGET, DEBUG_LOG_FILE_HANDLER
    if DEBUG_YEAR_TARGET and DEBUG_LOG_FILE_HANDLER and year_of_message and str(year_of_message) == str(DEBUG_YEAR_TARGET):
        DEBUG_LOG_FILE_HANDLER.write(f"{message}\\n")
    elif not DEBUG_YEAR_TARGET: # デバッグ年指定がない場合はコンソールに
        print(message)
    # デバッグ年指定があり、年が一致しない場合は何も出力しない (コンソールをクリーンに保つため)

def check_repo_updates():
    """graph-based-deep-learning-literatureリポジトリをgit pullし、更新があったか確認する"""
    print(f"リポジトリ {REPO_ROOT_PATH} の更新を確認しています...")
    try:
        result = subprocess.run(
            ['git', 'pull'],
            cwd=REPO_ROOT_PATH,
            capture_output=True,
            text=True,
            check=False # エラー時も処理を続けられるように
        )
        if result.returncode != 0:
            print(f"[警告] git pull の実行に失敗しました。エラーコード: {result.returncode}")
            print(f"  stdout: {result.stdout.strip()}")
            print(f"  stderr: {result.stderr.strip()}")
            print("  論文処理を続行しますが、リポジトリが最新でない可能性があります。")
            return True # エラーの場合は続行させる (手動更新されている可能性もあるため)

        output = result.stdout.strip()

        if "Already up to date." in output or "更新はありません。" in output : # 日本語環境も考慮
            print("  リポジトリは既に最新です。論文処理はスキップします。")
            return False
        else:
            print("  リポジトリが更新されました。論文処理を開始します。")
            return True
            
    except FileNotFoundError:
        # このエラーは中間READMEが存在しない場合など、ある程度予想されるため、警告レベルに留める
        return None
    except Exception as e:
        print(f"[エラー] git pull 実行中に予期せぬエラーが発生しました: {e}")
        print("  論文処理を続行しますが、リポジトリが最新でない可能性があります。")
        return True # その他のエラーの場合も続行
    
    # 上記のいずれの条件にも当てはまらない場合 (通常は発生しないはずだが念のため)
    return True 

def sanitize_filename(name, for_tag=False):
    """ファイル名やタグとして不適切な文字を除去・置換する"""
    name = str(name) 
    name = re.sub(r'[\\/:*?"<>|\r\n]', '', name)
    if for_tag:
        name = name.lower().replace(" ", "-").replace("&", "and")
    else:
        name = name.replace(" ", "_").replace("&", "and")
    return name[:150]

def read_file_content(file_path):
    """ファイルの内容を読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # UnicodeDecodeErrorはdebug_printではなく、通常のprintで常に表示する
        print(f"[警告] UTF-8でデコードできませんでした: {file_path}。latin-1を試みます。")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e_alt:
            print(f"[エラー] 代替エンコーディングでも読み込み失敗 ({file_path}): {e_alt}")
            return None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[エラー] ファイル読み込み中にエラー ({file_path}): {e}")
        return None

def parse_bibtex_simple(bibtex_string):
    """簡易的なBibTeXパーサー (正規表現ベース)"""
    data = {'title': '', 'authors': '', 'year': '', 'conference_raw': '', 'raw_bibtex': bibtex_string or ''}
    if not bibtex_string:
        return data
    bib_content_lower = str(bibtex_string).lower() # For most extractions

    title_match = re.search(r'title\s*=\s*[\{"](.+?)[\}"]\s*,', bib_content_lower, re.DOTALL)
    if title_match:
        data['title'] = title_match.group(1).strip().replace("\n", " ")
    author_match = re.search(r'author\s*=\s*[\{"](.+?)[\}"]\s*,', bib_content_lower, re.DOTALL)
    if author_match:
        data['authors'] = author_match.group(1).strip().replace("\n", " ")
    year_match = re.search(r'year\s*=\s*[\"{](.+?)[\"}]\s*,?', bib_content_lower)
    if year_match:
        data['year'] = year_match.group(1).strip()
    booktitle_match = re.search(r'booktitle\s*=\s*[\"{](.+?)[\"}]\s*,', bib_content_lower, re.DOTALL)
    if booktitle_match:
        data['conference_raw'] = booktitle_match.group(1).strip().replace("\n", " ")
    return data

def get_paper_links(paper_readme_content):
    """論文READMEから関連リンク (ACM, OpenReviewなど) を抽出"""
    links = {'acm': '', 'openreview': '', 'pdf': ''}
    if not paper_readme_content:
        return links
    paper_readme_content_str = str(paper_readme_content) # Ensure it's a string
    acm_match = re.search(r'\[acm\]\((https?://dl\.acm\.org/.+?)\)', paper_readme_content_str, re.IGNORECASE)
    if acm_match:
        links['acm'] = acm_match.group(1)
    openreview_match = re.search(r'\[openreview\]\((https?://openreview\.net/.+?)\)', paper_readme_content_str, re.IGNORECASE)
    if openreview_match:
        links['openreview'] = openreview_match.group(1)
    pdf_match = re.search(r'\[pdf\]\((https?://.+?\.pdf)\)', paper_readme_content_str, re.IGNORECASE)
    if pdf_match:
        links['pdf'] = pdf_match.group(1)
    return links

def normalize_category(raw_category_name):
    """カテゴリ名を正規化マップに基づいて正規化する。マップにない場合は整形して返す。"""
    if not raw_category_name or not isinstance(raw_category_name, str):
        return "Uncategorized"
    
    lower_name = raw_category_name.lower().strip()
    
    # 正規化マップでの完全一致を試みる
    if lower_name in CATEGORY_NORMALIZATION_MAP:
        return CATEGORY_NORMALIZATION_MAP[lower_name]
    
    # マップにない場合は、元の名前を整形して返す (例: 先頭大文字、アンダースコアをスペースに)
    # Markdownリンクを除去 (例: "Category [details](...)" -> "Category")
    name_no_link = re.sub(r'\s*\[.*\]\(.*\)', '', raw_category_name).strip()
    if not name_no_link:
        return "Uncategorized" # リンク除去後空なら未分類
    
    # 単純なタイトルケース化や不要語除去など、より高度な整形もここに追加可能
    # ここでは、区切り文字をスペースに統一し、タイトルケースっぽくする
    words = re.split(r'[\s_-]+', name_no_link) # スペース、アンダースコア、ハイフンで分割
    # 各単語の先頭を大文字に (ただし "and", "or", "of", "the", "in", "on", "for" などは小文字のままにしたい場合、追加処理が必要)
    # 簡単のため、ここでは全てタイトルケースにする
    formatted_name = " ".join([word.capitalize() for word in words if word])
    return formatted_name if formatted_name else "Uncategorized"

def get_conference_details(main_conf_readme_path_unused): # main_conf_readme_path is no longer used directly
    """
    ディレクトリ構造をスキャンして、各会議・年ごとの中間READMEへの情報リストを生成する。
    "2017_and_Earlier" ディレクトリは現在の処理ロジックと異なるためスキップする。
    """
    # この関数の最初のprintは、年指定に関わらず表示してよい
    print("ディレクトリ構造から会議情報を収集しています...")
    conference_links = []
    years_base_path = os.path.join(REPO_ROOT_PATH, "conference-publications", "folders", "years")
    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
        debug_print(f"[DEBUG] get_conference_details: years_base_path = {years_base_path}", "general")

    if not os.path.isdir(years_base_path):
        print(f"[エラー] 年ディレクトリが見つかりません: {years_base_path}")
        return []

    for year_dir_name in os.listdir(years_base_path):
        if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
            debug_print(f"[DEBUG] get_conference_details: Processing year_dir_name = {year_dir_name}", year_dir_name)
        if year_dir_name == "2017_and_Earlier":
            # この情報も年指定に関わらず表示
            print(f"[情報] '{year_dir_name}' ディレクトリは特殊な構造のため、この関数ではスキップします。")
            continue
        
        if not (year_dir_name.isdigit() and len(year_dir_name) == 4):
            if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                debug_print(f"[DEBUG] get_conference_details: スキップ (年ディレクトリ名として期待される形式ではありません): {year_dir_name}", year_dir_name)
            continue

        current_year_path = os.path.join(years_base_path, year_dir_name)
        if not os.path.isdir(current_year_path):
            if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                debug_print(f"[DEBUG] get_conference_details: スキップ (パスがディレクトリではありません): {current_year_path}", year_dir_name)
            continue

        for conf_pub_dir_name in os.listdir(current_year_path):
            if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                debug_print(f"[DEBUG] get_conference_details:   Processing conf_pub_dir_name = {conf_pub_dir_name} in {year_dir_name}", year_dir_name)
            if conf_pub_dir_name.startswith("publications_"):
                conf_pub_dir_path = os.path.join(current_year_path, conf_pub_dir_name)
                if not os.path.isdir(conf_pub_dir_path):
                    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                        debug_print(f"[DEBUG] get_conference_details:   スキップ (会議発行物パスがディレクトリではありません): {conf_pub_dir_path}", year_dir_name)
                    continue

                intermediate_readme_repo_path = \
                    f"conference-publications/folders/years/{year_dir_name}/{conf_pub_dir_name}/README.md"
                intermediate_readme_local_path = os.path.join(REPO_ROOT_PATH, intermediate_readme_repo_path)

                if os.path.isfile(intermediate_readme_local_path):
                    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                        debug_print(f"[DEBUG] get_conference_details:     中間README発見: {intermediate_readme_local_path}", year_dir_name)
                    match_key = re.match(r"publications_([a-zA-Z0-9]+)", conf_pub_dir_name)
                    conf_key = match_key.group(1) if match_key else conf_pub_dir_name.replace("publications_", "")
                    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                        debug_print(f"[DEBUG] get_conference_details:       conf_key = {conf_key}", year_dir_name)
                    
                    conf_name_candidate = re.sub(r'\d{2,4}$', '', conf_key) 
                    if not conf_name_candidate: 
                        conf_name_candidate = conf_key
                    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                        debug_print(f"[DEBUG] get_conference_details:       conf_name_candidate = {conf_name_candidate}", year_dir_name)

                    conf_name = conf_name_candidate.upper()
                    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                        debug_print(f"[DEBUG] get_conference_details:       conf_name (final) = {conf_name}", year_dir_name)

                    conference_links.append({
                        'name': conf_name, 
                        'year': year_dir_name, 
                        'key_from_path': conf_key, 
                        'readme_path': intermediate_readme_repo_path 
                    })
                else:
                    if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                        debug_print(f"[DEBUG] get_conference_details:     中間READMEが見つかりません (スキップ): {intermediate_readme_local_path}", year_dir_name)
            else:
                if DEBUG_YEAR_TARGET: # DEBUG_YEAR_TARGETが設定されている場合のみデバッグ出力
                    debug_print(f"[DEBUG] get_conference_details:   スキップ (会議発行物ディレクトリ名が 'publications_' で始まりません): {conf_pub_dir_name}", year_dir_name)
    
    conference_links.sort(key=lambda x: (x['year'], x['name']), reverse=True)
    print(f"ディレクトリ構造から {len(conference_links)} 件の会議情報を収集しました。") # これは常に表示
    return conference_links

def process_legacy_papers(template_content):
    """
    Processes papers from the "2017_and_Earlier" directory.
    This directory has a different structure (direct paper folders).
    """
    print("\n処理中のレガシー論文 (2017年以前)...")
    legacy_papers_base_path = os.path.join(REPO_ROOT_PATH, "conference-publications", "folders", "years", "2017_and_Earlier")
    if not os.path.isdir(legacy_papers_base_path):
        print(f"[情報] レガシー論文ディレクトリが見つかりません: {legacy_papers_base_path}")
        return 0

    processed_legacy_count = 0
    default_category_name = "Legacy" # For older papers

    for paper_folder_name in os.listdir(legacy_papers_base_path):
        paper_dir_local_path = os.path.join(legacy_papers_base_path, paper_folder_name)
        if not os.path.isdir(paper_dir_local_path):
            continue

        paper_readme_local_path = os.path.join(paper_dir_local_path, "README.md")
        paper_readme_relative_path = f"conference-publications/folders/years/2017_and_Earlier/{paper_folder_name}/README.md"
        
        paper_readme_content = read_file_content(paper_readme_local_path)
        if not paper_readme_content:
            continue

        current_time_iso = datetime.now().strftime("%Y-%m-%d") # For created_date and last_updated

        # Infer conference and year from folder name (e.g., "gcn_iclr17", "molecular_gcn_2016", "gnn_ijcnn05")
        conf_name_inferred = "UnknownConf"
        year_inferred = "UnknownYear"
        title_part_from_folder = paper_folder_name

        # Regex to capture (name_part)_conference_year(2 or 4 digits)
        # e.g. chebnet_neurips16 -> ('chebnet', 'neurips', '16')
        # e.g. molecular_gcn_2016 -> ('molecular_gcn', 'gcn', '2016') - careful with greedy name_part
        # Let's try a simpler approach: split by '_', last part is conf+year, second last is conf if multiple parts, rest is title_part
        parts = paper_folder_name.split('_')
        if len(parts) >= 2: # Need at least something_confYY
            conf_year_part = parts[-1] # e.g., "iclr17", "neurips16", "ijcnn05", "cvpr17", "emnlp17", "icml16" also "2016" for molecular_gcn_2016
            
            year_match_short = re.search(r'(\d{2})$', conf_year_part) # ends with 2 digits (e.g. 16, 17, 05)
            year_match_long = re.search(r'(\d{4})$', conf_year_part) # ends with 4 digits (e.g. 2016)

            if year_match_long:
                year_inferred = year_match_long.group(1)
                conf_name_inferred_candidate = conf_year_part[:-4] # Part before the 4-digit year
                if not conf_name_inferred_candidate and len(parts) > 1: # If conf_year_part was only year (e.g. "2016")
                    conf_name_inferred_candidate = parts[-2] # then conf is the part before, e.g. "gcn" in "molecular_gcn_2016"
                conf_name_inferred = conf_name_inferred_candidate.upper() if conf_name_inferred_candidate else "UnknownConf"
                title_part_from_folder = "_".join(parts[:-1]) if len(parts) > 1 else parts[0]


            elif year_match_short:
                year_suffix = year_match_short.group(1)
                if year_suffix == "05": # Special case for gnn_ijcnn05
                    year_inferred = "2005"
                elif int(year_suffix) <= 50 : # YY format like 16, 17, up to 50 (arbitrary cut-off for 20xx)
                    year_inferred = "20" + year_suffix
                else: # Should not happen often for old papers, e.g. 98 for 1998
                    year_inferred = "19" + year_suffix 
                
                conf_name_inferred_candidate = conf_year_part[:-2] # Part before the 2-digit year e.g. "iclr" from "iclr17"
                if not conf_name_inferred_candidate and len(parts) > 1:
                     conf_name_inferred_candidate = parts[-2]
                conf_name_inferred = conf_name_inferred_candidate.upper() if conf_name_inferred_candidate else "UnknownConf"
                title_part_from_folder = "_".join(parts[:-1]) if len(parts) > 1 else parts[0]
            else: # No year found in last part, maybe it's just conf like "ecc"
                conf_name_inferred = conf_year_part.upper()
                year_inferred = "UnknownYear" # Or try to find year in previous parts. For now, this is fine.
                title_part_from_folder = "_".join(parts[:-1])

        if conf_name_inferred == "UnknownConf" and len(parts) == 1: # e.g. foldername is just "gnn_tnn09" with no clear conference like "tnn"
             # Try to extract from folder name directly if structure is very different
            m = re.match(r'([a-zA-Z0-9]+)_([a-zA-Z]+)(\d{2})', paper_folder_name) # e.g. gcn_iclr17
            if m:
                title_part_from_folder = m.group(1)
                conf_name_inferred = m.group(2).upper()
                year_suffix = m.group(3)
                year_inferred = "20" + year_suffix if year_suffix != "05" else "2005"
            else: # final fallback if no structure matched well
                title_part_from_folder = paper_folder_name

        # Use the new BibTeX extraction logic
        bibtex_string = extract_bibtex_from_repo_readme(paper_readme_content)
        if not is_bibtex_valid(bibtex_string):
            debug_print(f"    [Legacy DEBUG] Invalid or missing BibTeX in {paper_readme_local_path}. BibTeX string: '{bibtex_string}'", "Legacy")
            bibtex_string = "" # Ensure bibtex_string is empty if not valid for parse_bibtex_simple
        else:
            debug_print(f"    [Legacy DEBUG] Valid BibTeX found in {paper_readme_local_path}.", "Legacy")
            
        bib_data = parse_bibtex_simple(bibtex_string) # bibtex_string is now the raw string from repo

        paper_title = bib_data['title']
        if not paper_title:
            h1_match = re.search(r"^#\s+(.+)", paper_readme_content, re.MULTILINE)
            if h1_match:
                paper_title = h1_match.group(1).strip()
            else:
                paper_title = title_part_from_folder.replace("_", " ").capitalize()
        
        paper_authors = bib_data['authors']
        paper_year_from_bib = bib_data['year'] if bib_data['year'] else year_inferred
        if paper_year_from_bib == "UnknownYear" and bib_data['year']: # bib_data['year'] might be empty string
            paper_year_from_bib = bib_data['year']

        paper_links = get_paper_links(paper_readme_content)

        sanitized_conf_name_for_path = sanitize_filename(conf_name_inferred)
        sanitized_category_for_path = sanitize_filename(default_category_name)
        sanitized_title_for_path = sanitize_filename(paper_title)

        obsidian_category_dir = os.path.join(PAPERS_DIR_OBSIDIAN, str(paper_year_from_bib), sanitized_conf_name_for_path, sanitized_category_for_path)
        os.makedirs(obsidian_category_dir, exist_ok=True)
        obsidian_paper_filepath = os.path.join(obsidian_category_dir, f"{sanitized_title_for_path}.md")
        
        if os.path.exists(obsidian_paper_filepath):
            # すでにノートが存在する場合はスキップ
            # debug_print(f"    [Legacy DEBUG] 既存ノートがあるためスキップ: {obsidian_paper_filepath}", "Legacy")
            continue

        github_paper_readme_full_url = GITHUB_REPO_BASE_URL + paper_readme_relative_path

        tags_list = ['gnn', 'legacy']
        tags_list.append(sanitize_filename(conf_name_inferred, for_tag=True))
        if paper_year_from_bib != "UnknownYear":
            tags_list.append(sanitize_filename(conf_name_inferred, for_tag=True) + str(paper_year_from_bib))
        tags_list.append(sanitize_filename(default_category_name, for_tag=True))
        
        unique_sorted_tags = sorted(list(set(filter(None, tags_list)))) # Filter out None or empty strings
        tags_string_for_template = ", ".join([f'{tag}' for tag in unique_sorted_tags])

        filled_template = template_content
        filled_template = filled_template.replace("{{title}}", paper_title.replace('"', '\\\\"'))
        filled_template = filled_template.replace("{{conference}}", conf_name_inferred)
        filled_template = filled_template.replace("{{year}}", str(paper_year_from_bib))
        filled_template = filled_template.replace("{{category}}", default_category_name)
        filled_template = filled_template.replace("{{auto_generated_tags}}", tags_string_for_template)
        filled_template = filled_template.replace("{{authors}}", paper_authors.replace('"', '\\\\"'))
        filled_template = filled_template.replace("{{link_to_repo_readme}}", github_paper_readme_full_url)
        filled_template = filled_template.replace("{{link_to_pdf}}", paper_links.get('pdf', ''))
        filled_template = filled_template.replace("{{link_to_acm}}", paper_links.get('acm', ''))
        filled_template = filled_template.replace("{{bibtex}}", bib_data['raw_bibtex'])
        filled_template = filled_template.replace("{{date}}", current_time_iso)
        filled_template = filled_template.replace("{{last_updated}}", current_time_iso)
        
        try:
            with open(obsidian_paper_filepath, 'w', encoding='utf-8') as f:
                f.write(filled_template)
            processed_legacy_count += 1
            if processed_legacy_count % 20 == 0:
                 print(f"    ... {processed_legacy_count} 件のレガシー論文を処理 ...")
        except Exception as e:
            print(f"    [エラー] レガシー論文ファイル書き込み中にエラー ({obsidian_paper_filepath}): {e}")

    print(f"レガシー論文処理完了。{processed_legacy_count} 件のノートを作成/更新しました。")
    return processed_legacy_count

def process_papers(template_content, debug_year=None): # debug_year引数を追加
    """論文処理のメイン関数"""
    global DEBUG_YEAR_TARGET, DEBUG_LOG_FILE_HANDLER
    if debug_year and DEBUG_LOG_FILE_HANDLER is None: # debug_yearが指定されているがファイルハンドラがない場合（通常はないはず）
        log_filename = f"debug_log_{debug_year}.txt"
        DEBUG_LOG_FILE_HANDLER = open(log_filename, "w", encoding="utf-8")
        print(f"デバッグログを {log_filename} に出力します。")


    if not os.path.exists(REPO_ROOT_PATH):
        print(f"[エラー] クローンされたリポジトリが見つかりません: {REPO_ROOT_PATH}")
        return 0 # 戻り値をintに
    if not os.path.exists(PAPER_TEMPLATE_PATH):
        print(f"[エラー] 論文テンプレートが見つかりません: {PAPER_TEMPLATE_PATH}")
        return 0 # 戻り値をintに

    print("\n主要な論文処理を開始します...")
    main_conf_readme_file = os.path.join(REPO_ROOT_PATH, "conference-publications", "README.md")
    conferences = get_conference_details(main_conf_readme_file)
    if not conferences:
        print("[情報] ディレクトリ構造スキャンから処理対象の会議が見つかりませんでした。")
        return 0 # 戻り値をintに

    processed_papers_count = 0

    for conf_info in conferences:
        conf_name = conf_info['name']
        conf_year = conf_info['year']

        # デバッグ対象年が指定されていて、現在の会議の年と一致しない場合はスキップ
        if DEBUG_YEAR_TARGET and str(conf_year) != str(DEBUG_YEAR_TARGET):
            continue
        
        current_year_for_debug = conf_year # debug_print に渡す年情報

        if not conf_info.get('readme_path'):
            print(f"[警告] {conf_name} {conf_year} のREADMEパスが空です。スキップします。")
            continue
        intermediate_readme_local_path = os.path.join(REPO_ROOT_PATH, conf_info['readme_path'])
        # 論文単位の README が無いケース（例: AAAI 2026 のように、タイトルだけ箇条書き）でも
        # 生成したノートの参照元として conference README を使えるようにする
        intermediate_readme_full_url = GITHUB_REPO_BASE_URL + conf_info['readme_path']
        
        # この会議処理開始のメッセージは、デバッグ対象年ならログファイルへ、そうでなければコンソールへ
        if DEBUG_YEAR_TARGET and str(conf_year) == str(DEBUG_YEAR_TARGET):
            debug_print(f"\n処理中の会議: {conf_name} {conf_year} (ファイル: {intermediate_readme_local_path})", current_year_for_debug)
        elif not DEBUG_YEAR_TARGET:
            print(f"\n処理中の会議: {conf_name} {conf_year} (ファイル: {intermediate_readme_local_path})")


        intermediate_content = read_file_content(intermediate_readme_local_path)
        if not intermediate_content:
            # debug_print(f"[情報] {intermediate_readme_local_path} の読み込みをスキップしました。", current_year_for_debug)
            continue

        current_raw_category_from_heading = "Uncategorized"
        current_normalized_category = "Uncategorized"
        paper_counter_for_this_conference = 0

        for line_num, line in enumerate(intermediate_content.splitlines()):
            category_heading_match = re.match(r"^#+\s+(.+)", line)
            if category_heading_match:
                raw_category_name = category_heading_match.group(1).strip()
                if not (raw_category_name.lower().startswith("publications in") or \
                        raw_category_name.lower().startswith("http") or \
                        re.match(r"^\[.*\]\(.*\)$", raw_category_name) or \
                        raw_category_name.lower() in ["contents", "overview"]):
                    current_raw_category_from_heading = raw_category_name
                    current_normalized_category = normalize_category(raw_category_name)
                else:
                    pass 
                continue

            paper_match = PAPER_LINK_REGEX.match(line)
            if paper_match:
                paper_counter_for_this_conference += 1
                debug_print(f"    [DEBUG line {line_num+1}] 論文リンクマッチ成功: {line.strip()}", current_year_for_debug)
                title_from_list = paper_match.group("title_from_list").strip()
                paper_readme_relative_path = paper_match.group("paper_readme_repo_path").strip()
                paper_readme_local_path = os.path.join(REPO_ROOT_PATH, paper_readme_relative_path)
                debug_print(f"      [DEBUG] paper_readme_local_path: {paper_readme_local_path}", current_year_for_debug)
                paper_readme_content = read_file_content(paper_readme_local_path)
                
                if not paper_readme_content:
                    debug_print(f"      [DEBUG] 論文README読み込み失敗 (スキップ): {paper_readme_local_path}", current_year_for_debug)
                    continue
                else:
                    debug_print(f"      [DEBUG] 論文README読み込み成功.", current_year_for_debug)
                
                current_time_iso = datetime.now().strftime("%Y-%m-%d")

                # Use new BibTeX extraction
                bibtex_string = extract_bibtex_from_repo_readme(paper_readme_content)
                if not is_bibtex_valid(bibtex_string):
                    debug_print(f"      [DEBUG] Invalid or missing BibTeX in {paper_readme_local_path}. BibTeX string was: '{bibtex_string}'", current_year_for_debug)
                    bibtex_string = "" # Ensure bibtex_string is empty if not valid, for parse_bibtex_simple
                else:
                    debug_print(f"      [DEBUG] Valid BibTeX successfully extracted from {paper_readme_local_path}.", current_year_for_debug)

                bib_data = parse_bibtex_simple(bibtex_string) # bibtex_string is now the raw string from repo
                debug_print(f"      [DEBUG] BibTeXパース結果: title='{bib_data['title'][:30]}...', authors='{bib_data['authors'][:30]}...', year='{bib_data['year']}'", current_year_for_debug)
                
                paper_title = bib_data['title'] if bib_data['title'] else title_from_list
                if not paper_title:
                    debug_print(f"      [DEBUG] paper_titleが空です。スキップします。 (元リスト名: {title_from_list})", current_year_for_debug)
                    continue
                else:
                    debug_print(f"      [DEBUG] 確定した論文タイトル: {paper_title[:50]}...", current_year_for_debug)

                paper_authors = bib_data['authors']
                paper_year_from_bib = bib_data['year'] if bib_data['year'] else conf_year
                paper_links = get_paper_links(paper_readme_content)

                sanitized_conf_name_for_path = sanitize_filename(conf_name, for_tag=False)
                sanitized_normalized_category_for_path = sanitize_filename(current_normalized_category if current_normalized_category != "Uncategorized" else "Miscellaneous", for_tag=False)
                sanitized_title_for_path = sanitize_filename(paper_title, for_tag=False)

                obsidian_category_dir = os.path.join(PAPERS_DIR_OBSIDIAN, str(paper_year_from_bib), sanitized_conf_name_for_path, sanitized_normalized_category_for_path)
                os.makedirs(obsidian_category_dir, exist_ok=True)
                obsidian_paper_filepath = os.path.join(obsidian_category_dir, f"{sanitized_title_for_path}.md")
                debug_print(f"      [DEBUG] 生成Obsidianパス: {obsidian_paper_filepath}", current_year_for_debug)
                github_paper_readme_full_url = GITHUB_REPO_BASE_URL + paper_readme_relative_path

                if os.path.exists(obsidian_paper_filepath):
                    # すでにノートが存在する場合はスキップ
                    # debug_print(f"      [DEBUG] 既存ノートがあるためスキップ: {obsidian_paper_filepath}", current_year_for_debug)
                    continue

                tags_list = ['gnn']
                tags_list.append(sanitize_filename(conf_name, for_tag=True))
                tags_list.append(sanitize_filename(conf_name, for_tag=True) + str(paper_year_from_bib))
                if current_normalized_category and current_normalized_category != "Uncategorized":
                    tags_list.append(sanitize_filename(current_normalized_category, for_tag=True))
                if current_raw_category_from_heading and current_raw_category_from_heading != "Uncategorized" and sanitize_filename(current_raw_category_from_heading, for_tag=True) != sanitize_filename(current_normalized_category, for_tag=True):
                    tags_list.append(sanitize_filename(current_raw_category_from_heading, for_tag=True))
                
                unique_sorted_tags = sorted(list(set(tags_list)))
                tags_string_for_template = ", ".join([f'{tag}' for tag in unique_sorted_tags])

                filled_template = template_content
                filled_template = filled_template.replace("{{title}}", paper_title.replace('"', '\\"'))
                filled_template = filled_template.replace("{{conference}}", conf_name)
                filled_template = filled_template.replace("{{year}}", str(paper_year_from_bib))
                filled_template = filled_template.replace("{{category}}", current_normalized_category if current_normalized_category else "Uncategorized")
                filled_template = filled_template.replace("{{auto_generated_tags}}", tags_string_for_template)
                
                filled_template = filled_template.replace("{{authors}}", paper_authors.replace('"', '\\"'))
                filled_template = filled_template.replace("{{link_to_repo_readme}}", github_paper_readme_full_url)
                filled_template = filled_template.replace("{{link_to_pdf}}", paper_links.get('pdf', ''))
                filled_template = filled_template.replace("{{link_to_acm}}", paper_links.get('acm', ''))
                filled_template = filled_template.replace("{{bibtex}}", bib_data['raw_bibtex'])
                filled_template = filled_template.replace("{{date}}", current_time_iso)
                filled_template = filled_template.replace("{{last_updated}}", current_time_iso)
                
                try:
                    with open(obsidian_paper_filepath, 'w', encoding='utf-8') as f:
                        f.write(filled_template)
                    processed_papers_count += 1
                    debug_print(f"      [DEBUG] ファイル書き込み成功: {obsidian_paper_filepath}", current_year_for_debug)
                except Exception as e:
                    # このエラーは常にコンソールに出す
                    print(f"      [エラー] ファイル書き込みエラー ({obsidian_paper_filepath}): {e}")
                
                continue  # 既存のGitHub内READMEマッチの処理はここまで

            # ここからは、個別フォルダが無く README に外部リンクのみが列挙されるケースを処理
            # 例: "- [Title](https://nips.cc/...)"
            generic_link_match = re.match(r"^[-*]\s*\[(?P<title>.+?)\]\((?P<url>https?://[^\s)]+)\)", line.strip())
            if generic_link_match:
                title_from_list = generic_link_match.group("title").strip()
                external_url = generic_link_match.group("url").strip()

                # GitHub内READMEリンクの場合は上の正規表現で処理されるので、ここでは外部URLのみ扱う
                if external_url.startswith(GITHUB_REPO_BASE_URL):
                    continue

                paper_counter_for_this_conference += 1
                debug_print(f"    [DEBUG line {line_num+1}] 一般リンク検出: title='{title_from_list[:60]}', url='{external_url}'", current_year_for_debug)

                current_time_iso = datetime.now().strftime("%Y-%m-%d")

                # 外部リンクから分かる範囲の付随リンクを推測
                paper_links = {'acm': '', 'openreview': '', 'pdf': ''}
                if re.search(r"openreview\.net", external_url, re.IGNORECASE):
                    paper_links['openreview'] = external_url
                elif re.search(r"\.pdf($|\?)", external_url, re.IGNORECASE):
                    paper_links['pdf'] = external_url
                # それ以外は情報源として source とみなし、テンプレートの repo_readme に格納

                paper_title = title_from_list
                paper_authors = ""
                paper_year_from_bib = conf_year

                sanitized_conf_name_for_path = sanitize_filename(conf_name, for_tag=False)
                sanitized_normalized_category_for_path = sanitize_filename(current_normalized_category if current_normalized_category != "Uncategorized" else "Miscellaneous", for_tag=False)
                sanitized_title_for_path = sanitize_filename(paper_title, for_tag=False)

                obsidian_category_dir = os.path.join(PAPERS_DIR_OBSIDIAN, str(paper_year_from_bib), sanitized_conf_name_for_path, sanitized_normalized_category_for_path)
                os.makedirs(obsidian_category_dir, exist_ok=True)
                obsidian_paper_filepath = os.path.join(obsidian_category_dir, f"{sanitized_title_for_path}.md")
                debug_print(f"      [DEBUG] 生成Obsidianパス(一般リンク): {obsidian_paper_filepath}", current_year_for_debug)

                if os.path.exists(obsidian_paper_filepath):
                    # すでにノートが存在する場合はスキップ
                    continue

                tags_list = ['gnn']
                tags_list.append(sanitize_filename(conf_name, for_tag=True))
                tags_list.append(sanitize_filename(conf_name, for_tag=True) + str(paper_year_from_bib))
                if current_normalized_category and current_normalized_category != "Uncategorized":
                    tags_list.append(sanitize_filename(current_normalized_category, for_tag=True))
                if current_raw_category_from_heading and current_raw_category_from_heading != "Uncategorized" and sanitize_filename(current_raw_category_from_heading, for_tag=True) != sanitize_filename(current_normalized_category, for_tag=True):
                    tags_list.append(sanitize_filename(current_raw_category_from_heading, for_tag=True))

                unique_sorted_tags = sorted(list(set(tags_list)))
                tags_string_for_template = ", ".join([f'{tag}' for tag in unique_sorted_tags])

                filled_template = template_content
                filled_template = filled_template.replace("{{title}}", paper_title.replace('"', '\\"'))
                filled_template = filled_template.replace("{{conference}}", conf_name)
                filled_template = filled_template.replace("{{year}}", str(paper_year_from_bib))
                filled_template = filled_template.replace("{{category}}", current_normalized_category if current_normalized_category else "Uncategorized")
                filled_template = filled_template.replace("{{auto_generated_tags}}", tags_string_for_template)

                filled_template = filled_template.replace("{{authors}}", paper_authors.replace('"', '\\"'))
                # 情報源URLは repo_readme の欄に保存（既存テンプレ仕様に合わせる）
                filled_template = filled_template.replace("{{link_to_repo_readme}}", external_url)
                filled_template = filled_template.replace("{{link_to_pdf}}", paper_links.get('pdf', ''))
                filled_template = filled_template.replace("{{link_to_acm}}", paper_links.get('acm', ''))
                filled_template = filled_template.replace("{{bibtex}}", "")
                filled_template = filled_template.replace("{{date}}", current_time_iso)
                filled_template = filled_template.replace("{{last_updated}}", current_time_iso)

                try:
                    with open(obsidian_paper_filepath, 'w', encoding='utf-8') as f:
                        f.write(filled_template)
                    processed_papers_count += 1
                    debug_print(f"      [DEBUG] ファイル書き込み成功(一般リンク): {obsidian_paper_filepath}", current_year_for_debug)
                except Exception as e:
                    print(f"      [エラー] ファイル書き込みエラー (一般リンク: {obsidian_paper_filepath}): {e}")

            # ここからは、README に「- 論文タイトル」形式（リンク無しの箇条書き）だけが列挙されるケースを処理
            # 例: AAAI 2026 の README では、論文への URL が無いため PAPER_LINK_REGEX / generic_link_match に引っかからない
            if paper_counter_for_this_conference is not None:
                bullet_title_match = re.match(r"^[-*]\s+(?!\[)(?P<title>.+?)\s*$", line.strip())
                if bullet_title_match:
                    title_from_list = bullet_title_match.group("title").strip()

                    # "通常のリンク形式" を誤って拾わないようにする
                    if not title_from_list or title_from_list.startswith("http"):
                        continue

                    paper_counter_for_this_conference += 1
                    current_time_iso = datetime.now().strftime("%Y-%m-%d")

                    paper_title = title_from_list
                    paper_authors = ""
                    paper_year_from_bib = conf_year
                    paper_links = {'acm': '', 'openreview': '', 'pdf': ''}

                    sanitized_conf_name_for_path = sanitize_filename(conf_name, for_tag=False)
                    sanitized_normalized_category_for_path = sanitize_filename(
                        current_normalized_category if current_normalized_category != "Uncategorized" else "Miscellaneous",
                        for_tag=False
                    )
                    sanitized_title_for_path = sanitize_filename(paper_title, for_tag=False)

                    obsidian_category_dir = os.path.join(
                        PAPERS_DIR_OBSIDIAN,
                        str(paper_year_from_bib),
                        sanitized_conf_name_for_path,
                        sanitized_normalized_category_for_path
                    )
                    os.makedirs(obsidian_category_dir, exist_ok=True)
                    obsidian_paper_filepath = os.path.join(obsidian_category_dir, f"{sanitized_title_for_path}.md")

                    if os.path.exists(obsidian_paper_filepath):
                        continue

                    tags_list = ['gnn']
                    tags_list.append(sanitize_filename(conf_name, for_tag=True))
                    tags_list.append(sanitize_filename(conf_name, for_tag=True) + str(paper_year_from_bib))
                    if current_normalized_category and current_normalized_category != "Uncategorized":
                        tags_list.append(sanitize_filename(current_normalized_category, for_tag=True))
                    if current_raw_category_from_heading and current_raw_category_from_heading != "Uncategorized" and sanitize_filename(current_raw_category_from_heading, for_tag=True) != sanitize_filename(current_normalized_category, for_tag=True):
                        tags_list.append(sanitize_filename(current_raw_category_from_heading, for_tag=True))

                    unique_sorted_tags = sorted(list(set(tags_list)))
                    tags_string_for_template = ", ".join([f'{tag}' for tag in unique_sorted_tags])

                    filled_template = template_content
                    filled_template = filled_template.replace("{{title}}", paper_title.replace('"', '\\"'))
                    filled_template = filled_template.replace("{{conference}}", conf_name)
                    filled_template = filled_template.replace("{{year}}", str(paper_year_from_bib))
                    filled_template = filled_template.replace("{{category}}", current_normalized_category if current_normalized_category else "Uncategorized")
                    filled_template = filled_template.replace("{{auto_generated_tags}}", tags_string_for_template)
                    filled_template = filled_template.replace("{{authors}}", paper_authors.replace('"', '\\"'))
                    # URL が無いので、参照元は conference README にする
                    filled_template = filled_template.replace("{{link_to_repo_readme}}", intermediate_readme_full_url)
                    filled_template = filled_template.replace("{{link_to_pdf}}", paper_links.get('pdf', ''))
                    filled_template = filled_template.replace("{{link_to_acm}}", paper_links.get('acm', ''))
                    filled_template = filled_template.replace("{{bibtex}}", "")
                    filled_template = filled_template.replace("{{date}}", current_time_iso)
                    filled_template = filled_template.replace("{{last_updated}}", current_time_iso)

                    try:
                        with open(obsidian_paper_filepath, 'w', encoding='utf-8') as f:
                            f.write(filled_template)
                        processed_papers_count += 1
                        debug_print(f"      [DEBUG] ファイル書き込み成功(リンク無し箇条書き): {obsidian_paper_filepath}", current_year_for_debug)
                    except Exception as e:
                        print(f"      [エラー] ファイル書き込みエラー(リンク無し箇条書き: {obsidian_paper_filepath}): {e}")
            
        if intermediate_content and paper_counter_for_this_conference > 0:
             debug_print(f"  --- {conf_name} {conf_year} 処理試行: {paper_counter_for_this_conference}件の論文リンクを検出 --- ", current_year_for_debug)

    print(f"\n主要な論文処理完了。{processed_papers_count} 件の論文ノートを作成/更新しました。") # これは常に表示
    return processed_papers_count

def collect_existing_pairs_in_papers():
    """Papers 配下に既に存在する (year, conf_folder_name) の組を返す。"""
    existing_pairs = set()
    if os.path.isdir(PAPERS_DIR_OBSIDIAN):
        for year_name in os.listdir(PAPERS_DIR_OBSIDIAN):
            if year_name.isdigit() and len(year_name) == 4:
                year_path = os.path.join(PAPERS_DIR_OBSIDIAN, year_name)
                if os.path.isdir(year_path):
                    for conf_name in os.listdir(year_path):
                        conf_path = os.path.join(year_path, conf_name)
                        if os.path.isdir(conf_path):
                            # conf_name は既に sanitize 済みのフォルダ名になる
                            existing_pairs.add((year_name, conf_name))
    return existing_pairs

def collect_repo_pairs_for_missing_conferences():
    """
    リポジトリ側のディレクトリ構造から、(year, conf_folder_name) を収集する。
    - conf_folder_name は Papers で使っている sanitize_filename(conf_name, for_tag=False) と同じ形にする
    - 例: Papers/2026/ICLR が無いなら、(2026, 'ICLR') が返る
    """
    repo_pairs = set()
    years_base_path = os.path.join(REPO_ROOT_PATH, "conference-publications", "folders", "years")
    if not os.path.isdir(years_base_path):
        return repo_pairs

    for year_dir_name in os.listdir(years_base_path):
        if year_dir_name == "2017_and_Earlier":
            continue
        if not (year_dir_name.isdigit() and len(year_dir_name) == 4):
            continue

        current_year_path = os.path.join(years_base_path, year_dir_name)
        if not os.path.isdir(current_year_path):
            continue

        for conf_pub_dir_name in os.listdir(current_year_path):
            if not conf_pub_dir_name.startswith("publications_"):
                continue
            conf_pub_dir_path = os.path.join(current_year_path, conf_pub_dir_name)
            if not os.path.isdir(conf_pub_dir_path):
                continue

            intermediate_readme_repo_path = (
                f"conference-publications/folders/years/{year_dir_name}/{conf_pub_dir_name}/README.md"
            )
            intermediate_readme_local_path = os.path.join(REPO_ROOT_PATH, intermediate_readme_repo_path)
            if not os.path.isfile(intermediate_readme_local_path):
                continue

            match_key = re.match(r"publications_([a-zA-Z0-9]+)", conf_pub_dir_name)
            conf_key = match_key.group(1) if match_key else conf_pub_dir_name.replace("publications_", "")

            conf_name_candidate = re.sub(r"\d{2,4}$", "", conf_key)
            if not conf_name_candidate:
                conf_name_candidate = conf_key
            conf_name = conf_name_candidate.upper()

            repo_pairs.add((year_dir_name, sanitize_filename(conf_name, for_tag=False)))

    return repo_pairs

def run_dry_run():
    """リポジトリを最新にして、新規追加される会議（年・会議名）を表示する。ファイルは作成しない。"""
    print("--- dry-run: リポジトリを最新に取得し、追加予定の会議のみ表示します ---")
    check_repo_updates()

    if not os.path.isdir(REPO_ROOT_PATH):
        print(f"[エラー] リポジトリが見つかりません: {REPO_ROOT_PATH}")
        return

    conferences = get_conference_details(None)
    if not conferences:
        print("[情報] リポジトリから会議一覧を取得できませんでした。")
        return

    existing_pairs = set()
    if os.path.isdir(PAPERS_DIR_OBSIDIAN):
        for year_name in os.listdir(PAPERS_DIR_OBSIDIAN):
            if year_name.isdigit() and len(year_name) == 4:
                year_path = os.path.join(PAPERS_DIR_OBSIDIAN, year_name)
                if os.path.isdir(year_path):
                    for conf_name in os.listdir(year_path):
                        conf_path = os.path.join(year_path, conf_name)
                        if os.path.isdir(conf_path):
                            existing_pairs.add((year_name, conf_name))

    new_conferences = [
        c for c in conferences
        if (c["year"], sanitize_filename(c["name"], for_tag=False)) not in existing_pairs
    ]
    new_conferences.sort(key=lambda x: (x["year"], x["name"]))

    if not new_conferences:
        print("\n新規追加される会議はありません。（リポジトリの内容は既に Papers に反映済みです）")
        return

    print(f"\n新規追加される会議 (リポジトリにあり、Papers にまだないもの): 計 {len(new_conferences)} 件\n")
    current_year = None
    for c in new_conferences:
        if c["year"] != current_year:
            current_year = c["year"]
            print(f"  [{current_year}年]")
        print(f"    - {c['name']}")
    print("\n--- dry-run 終了。実際にノートを作成するには --dry-run を付けずに実行してください。 ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GNN論文情報を処理しObsidianノートを生成するスクリプト")
    parser.add_argument("--debug-year", type=str, help="指定した年の処理ログをファイルに出力します (例: 2019)")
    parser.add_argument("--dry-run", action="store_true", help="リポジトリを最新にして、新規追加される会議(年・会議名)のみ表示し、ファイルは作成しない")
    args = parser.parse_args()

    if args.dry_run:
        run_dry_run()
        exit(0)

    DEBUG_YEAR_TARGET = args.debug_year
    if DEBUG_YEAR_TARGET:
        log_filename = f"debug_log_{DEBUG_YEAR_TARGET}.txt"
        try:
            DEBUG_LOG_FILE_HANDLER = open(log_filename, "w", encoding="utf-8")
            print(f"デバッグモード: {DEBUG_YEAR_TARGET}年の処理ログを {log_filename} に出力します。")
        except Exception as e:
            print(f"[エラー] デバッグログファイル ({log_filename}) を開けませんでした: {e}")
            DEBUG_LOG_FILE_HANDLER = None # 念のためNoneに設定
            DEBUG_YEAR_TARGET = None # デバッグファイル出力は無効化

    print("論文処理スクリプトを開始します...")

    repo_updated = check_repo_updates()
    if repo_updated is False:
        # リポジトリが最新でも、Papers 側に未反映の会議があれば生成する
        existing_pairs = collect_existing_pairs_in_papers()
        repo_pairs = collect_repo_pairs_for_missing_conferences()
        missing_pairs = sorted(list(repo_pairs - existing_pairs), key=lambda x: (x[0], x[1]))

        if not missing_pairs:
            print("リポジトリ更新がないため、論文処理を終了します。（Papers に未反映の会議がありません）")
            if DEBUG_LOG_FILE_HANDLER:
                DEBUG_LOG_FILE_HANDLER.close()
                print(f"デバッグログファイル {log_filename} を閉じました。")
            exit(0)

        missing_years = sorted(list(set([p[0] for p in missing_pairs])))
        print(f"リポジトリ更新がなくても、Papers に未反映の会議があるため処理を続行します。対象年: {', '.join(missing_years)}")

    # テンプレートファイルの読み込み
    if not os.path.exists(PAPER_TEMPLATE_PATH):
        print(f"[エラー] 論文テンプレートファイルが見つかりません: {PAPER_TEMPLATE_PATH}")
        print("スクリプトを終了します。")
        if DEBUG_LOG_FILE_HANDLER: DEBUG_LOG_FILE_HANDLER.close()
        exit()
    template_content = read_file_content(PAPER_TEMPLATE_PATH)
    if template_content is None:
        print("[エラー] 論文テンプレートの読み込みに失敗しました。")
        print("スクリプトを終了します。")
        if DEBUG_LOG_FILE_HANDLER: DEBUG_LOG_FILE_HANDLER.close()
        exit()
    
    if not DEBUG_YEAR_TARGET: # デバッグモードでない場合のみ通常情報を表示
        print(f"使用するObsidian Vaultベースパス: {OBSIDIAN_VAULT_BASE_PATH}")
        print(f"参照する論文リポジトリパス: {REPO_ROOT_PATH}")
        print(f"論文ノート出力先ディレクトリ: {PAPERS_DIR_OBSIDIAN}")
        print(f"論文テンプレートパス: {PAPER_TEMPLATE_PATH}")

    # メインの論文処理 (debug_yearを渡す)
    processed_count = process_papers(template_content, DEBUG_YEAR_TARGET)
    # レガシー論文の処理 (デバッグ年の影響を受けない)
    processed_legacy_count = process_legacy_papers(template_content)

    total_processed = processed_count + processed_legacy_count
    print(f"\n処理完了。合計 {total_processed} 件の論文情報に基づいてノートを生成/更新しました。")
    if total_processed > 0:
        print(f"生成されたノートは {PAPERS_DIR_OBSIDIAN} 以下にあります。")
    else:
        print("処理対象の新しい論文情報はありませんでした。")

    if DEBUG_LOG_FILE_HANDLER:
        DEBUG_LOG_FILE_HANDLER.close()
        print(f"デバッグログファイル {log_filename} を閉じました。")

    print("論文処理スクリプトを終了します。") 