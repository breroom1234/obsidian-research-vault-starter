import os
import re
from datetime import datetime
import sys # Added for sys.exit()

# --- Configuration ---
OBSIDIAN_VAULT_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAPERS_DIR_OBSIDIAN = os.path.join(OBSIDIAN_VAULT_BASE_PATH, "Papers")
REPO_ROOT_PATH = os.path.join(OBSIDIAN_VAULT_BASE_PATH, "graph-based-deep-learning-literature")
GITHUB_REPO_BASE_URL = "https://github.com/naganandy/graph-based-deep-learning-literature/blob/master/"
# --- Configuration End ---

def read_file_content(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        print(f"  [Warning] UTF-8 decoding failed for {file_path}. Trying latin-1.")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e_alt:
            print(f"  [Error] Failed to read {file_path} with alternative encoding: {e_alt}")
            return None
    except FileNotFoundError:
        print(f"  [Error] File not found: {file_path}")
        return None
    except Exception as e:
        print(f"  [Error] Could not read file {file_path}: {e}")
        return None

def write_file_content(file_path, content):
    """Writes content to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  [Error] Could not write to file {file_path}: {e}")
        return False

def parse_frontmatter_value(note_content, key):
    """Parses a specific key from the frontmatter of a Markdown note.
       Returns the value, or None if the key or frontmatter is not found.
    """
    if not note_content:
        return None

    # Split the content by '---' to isolate frontmatter
    # parts[0] is before the first '---'
    # parts[1] is the frontmatter content
    # parts[2] is after the second '---'
    parts = note_content.split("---", 2)
    frontmatter_text = None

    if len(parts) >= 3 and parts[0].strip() == "": # Ensure it starts with ---
        frontmatter_text = parts[1].strip() # .strip() to remove leading/trailing newlines of the block
    
    if not frontmatter_text:
        return None # Indicates no valid frontmatter block found by this method

    # Search for the key within the extracted frontmatter text
    # The key should be at the start of a line within the frontmatter block
    key_match = re.search(rf"^{key}:\s*(.*)", frontmatter_text, re.MULTILINE)
    if key_match:
        value = key_match.group(1).strip()
        # Optionally strip surrounding quotes from the value
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        return value
    
    return None # Key not found within the detected frontmatter

def parse_frontmatter_value_with_diagnostic(note_content, key, filepath_for_debug):
    """Wrapper for parse_frontmatter_value that adds diagnostic printing."""
    value = parse_frontmatter_value(note_content, key)
    if value is None:
        # Try to get frontmatter text again for diagnostics
        parts = note_content.split("---", 2)
        frontmatter_text_diag = None
        has_frontmatter_block = False

        if len(parts) >= 3 and parts[0].strip() == "":
            frontmatter_text_diag = parts[1].strip()
            has_frontmatter_block = True
        
        print(f"  [Warning] '{key}' not found in frontmatter of {os.path.basename(filepath_for_debug)}.")
        if has_frontmatter_block:
            print(f"    [Diagnostic] Frontmatter block detected. Content snippet (up to 300 chars):\n---\n{frontmatter_text_diag[:300]}...---")
            # Check if the key string (e.g., "link_to_repo_readme:") exists at all, even if not parsed
            if f"{key}:" not in frontmatter_text_diag:
                 print(f"    [Diagnostic] The exact key string '{key}:' was not found in the above frontmatter snippet.")
            else:
                 print(f"    [Diagnostic] The key '{key}:' appears to be in the frontmatter but was not parsed correctly by the regex (check for typos, extra spaces, or unusual formatting around the key).")
        else:
            print(f"    [Diagnostic] No valid frontmatter block (e.g., starting with '---' and having a closing '---') detected at the beginning of the file.")
            print(f"    [Diagnostic] File content snippet (first 300 chars):\n{note_content[:300]}...")
    return value

def extract_bibtex_from_obsidian_note(note_content):
    """Extracts BibTeX from the ## BibTeX code block in an Obsidian note."""
    if not note_content:
        return None
    # Regex to find BibTeX block, allowing for optional "bibtex" language specifier
    # 注意: r"\\s" は「空白」ではなくリテラル \s を探す。空白・改行は \s と \n を1本ずつ使う
    match = re.search(r"##\s*BibTeX\s*```(?:bibtex)?\s*\n(.*?)\n```", note_content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_bibtex_from_repo_readme(readme_content):
    """Extracts BibTeX from a ```bibtex ... ``` code block in repository README content."""
    if not readme_content:
        return None
    # Regex to find BibTeX block, looking for @type{key, ... entry
    # First, try the standard markdown code block
    standard_block_match = re.search(r"```(?:bibtex)?\s*\n(@(?:inproceedings|article|book|misc|unpublished)\{[^\}]+?\}.*?)\n```", readme_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if standard_block_match:
        return standard_block_match.group(1).strip()

    # If standard block fails, try to find a raw BibTeX entry that might not be in a perfectly formed block
    # This is more greedy and looks for any line starting with @type{key... and captures until its balancing }
    # It assumes the BibTeX entry is reasonably well-formed itself.
    raw_bibtex_match = re.search(r"^(@(?:inproceedings|incollection|article|book|misc|unpublished)\{[^\}]+\}(?:.|\s)*?\n\s*\})", readme_content, re.MULTILINE | re.IGNORECASE)
    if raw_bibtex_match:
        # print("    [Diagnostic] Found BibTeX using raw pattern match.") # Optional debug
        return raw_bibtex_match.group(1).strip()
    
    return None

def is_bibtex_valid(bibtex_str):
    """Checks if the BibTeX string appears to be a valid, non-empty entry."""
    if not bibtex_str or not bibtex_str.strip():
        return False
    # Simple check: starts with @, contains {, }, and is of reasonable length
    s = bibtex_str.strip()
    return s.startswith("@") and "{" in s and "}" in s and len(s) > 15

def update_bibtex_in_note_body(note_content, new_bibtex):
    """Replaces the BibTeX in the {{bibtex}} placeholder or the ## BibTeX code block."""
    if not note_content: return note_content

    new_bibtex_to_insert = new_bibtex.strip() if new_bibtex else ""
    updated_content = note_content
    bibtex_updated = False

    # 1. Try to replace {{bibtex}} placeholder first
    # repl に文字列を渡すと re が \s 等をエスケープとして解釈し bad escape になるため、callable で渡す
    placeholder_pattern = re.compile(r"\{\{bibtex\}\}")
    updated_content, n_subs_placeholder = placeholder_pattern.subn(lambda m: new_bibtex_to_insert, note_content)
    if n_subs_placeholder > 0:
        print(f"    Replaced {{bibtex}} placeholder (found {n_subs_placeholder} occurrence(s)).")
        bibtex_updated = True
    
    # 2. If placeholder not found/replaced, try to update existing ## BibTeX code block(s)
    if not bibtex_updated:
        bibtex_section_pattern = re.compile(r"(##\s*BibTeX\s*```(?:bibtex)?\s*\n)(.*?)(\n```)", re.DOTALL | re.IGNORECASE)
        # We want to replace the content of the *first* such block if it exists and is empty/invalid,
        # or ensure all are consistent if multiple exist.
        # For simplicity, subn will replace all. If the first one was targeted by `extract_bibtex_from_obsidian_note`
        # as being empty/invalid, this will effectively fill it.
        updated_content, n_subs_section = bibtex_section_pattern.subn(
            lambda m: m.group(1) + new_bibtex_to_insert + m.group(3), 
            note_content # Operate on original content if placeholder wasn't primary target
        )
        if n_subs_section > 0:
            print(f"    Updated content of {n_subs_section} ## BibTeX code block(s).")
            bibtex_updated = True

    # 3. If neither placeholder nor section was found/updated, and we have valid BibTeX to insert, append a new section.
    if not bibtex_updated and new_bibtex_to_insert:
        print("    BibTeX placeholder and code block not found. Appending new section.")
        # Ensure there are two newlines before appending, unless rstrip() already results in that.
        separator = "\n\n" if not note_content.endswith("\n\n") else ("\n" if not note_content.endswith("\n") else "")
        updated_content = note_content.rstrip() + separator + \
                          f"## BibTeX\n```bibtex\n{new_bibtex_to_insert}\n```\n"
        bibtex_updated = True # Technically, it was added
    elif not bibtex_updated and not new_bibtex_to_insert:
        # No update needed, no placeholder/section found, and new bibtex is empty.
        # This case means an empty bibtex was fetched for a note that has no bibtex section/placeholder.
        print("    No BibTeX section/placeholder found, and fetched BibTeX is empty. No changes to BibTeX body.")
        updated_content = note_content # Explicitly state no change to body content
        
    return updated_content

def update_frontmatter_field(note_content, key_to_update, new_value):
    """Updates a field in the frontmatter. Adds the field if it doesn't exist.
       Handles cases where frontmatter might be missing or malformed.
    """
    lines = note_content.splitlines(True) # Keep line endings
    
    if not lines: # Empty file
        # Create new frontmatter
        return f"---\n{key_to_update}: {new_value}\n---\n"

    output_lines = []
    
    first_marker_index = -1
    second_marker_index = -1

    # Check for existing frontmatter
    if lines[0].strip() == "---":
        first_marker_index = 0
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                second_marker_index = i
                break
    
    if first_marker_index == 0 and second_marker_index != -1:
        # Valid frontmatter found
        key_found_and_updated = False
        # Copy lines before frontmatter (should be none if first_marker_index is 0)
        output_lines.extend(lines[:first_marker_index])
        
        # Process existing frontmatter block
        frontmatter_lines = []
        for i in range(first_marker_index, second_marker_index + 1):
            line = lines[i]
            if i > first_marker_index and i < second_marker_index: # Inside the --- markers
                if line.strip().startswith(key_to_update + ":"):
                    # Indentation and original key format should be preserved as much as possible
                    # For simplicity, we replace the whole line.
                    # A more sophisticated approach would parse YAML to preserve comments/spacing.
                    leading_whitespace = re.match(r"^(\s*)", line).group(1)
                    frontmatter_lines.append(f"{leading_whitespace}{key_to_update}: {new_value}\n")
                    key_found_and_updated = True
                else:
                    frontmatter_lines.append(line)
            else: # The '---' markers themselves
                frontmatter_lines.append(line)

        if not key_found_and_updated:
            # Key was not found, add it before the closing '---'
            # Ensure the new key has a newline if the previous line doesn't end with one
            new_key_line = f"{key_to_update}: {new_value}\n"
            if frontmatter_lines[-2].endswith("\n"):
                 frontmatter_lines.insert(-1, new_key_line) # Insert before the last element (closing '---')
            else: # Should not happen if splitlines(True) is used, but as a safeguard
                 frontmatter_lines.insert(-1, "\n" + new_key_line)
                 
        output_lines.extend(frontmatter_lines)
        # Add rest of the file content
        output_lines.extend(lines[second_marker_index + 1:])
        
    else:
        # No valid frontmatter found at the beginning, or it's malformed.
        # Prepend a new frontmatter block.
        print(f"    [Info] No valid frontmatter found at the beginning of the file or it was malformed. Prepending new frontmatter for '{key_to_update}'.")
        output_lines.append("---\n")
        output_lines.append(f"{key_to_update}: {new_value}\n")
        output_lines.append("---\n")
        # Add all original lines after the new frontmatter
        # If the first line was '---' but no second '---' was found, it's part of original lines now.
        output_lines.extend(lines)
        
    return "".join(output_lines)


def main():
    print("Starting BibTeX refetch process...")
    processed_files = 0
    updated_files = 0
    error_files = 0
    updated_files_details = [] # Initialize updated_files_details
    bibtex_fetch_failed_papers = [] # List to store paths of papers where BibTeX fetch failed
    # Removed files_processed_this_run and max_files_to_test for full processing

    for root, _, files in os.walk(PAPERS_DIR_OBSIDIAN):
        processed_files += len(files) # Count all files found by os.walk for a more accurate total
        for filename in files:
            # Removed test limit check
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                # Removed general print(f"\nProcessing: {filepath}") for quieter operation
                action_taken = False # Initialize for each file
                update_reason = ''   # Initialize for each file

                note_content_original = read_file_content(filepath)
                if not note_content_original:
                    error_files += 1
                    continue
                
                # Removed files_processed_this_run increment as it's no longer used for limiting

                current_bibtex_in_note = extract_bibtex_from_obsidian_note(note_content_original)
                
                needs_update = not is_bibtex_valid(current_bibtex_in_note)
                if needs_update:
                    # Removed: print(f"  BibTeX in note is missing or invalid. Attempting to fetch.")
                    pass # Continue to fetching logic
                else:
                    # Removed: print(f"  BibTeX in note seems valid. Skipping fetch.")
                    continue # Skip this file silently if BibTeX is already valid

                repo_readme_link = parse_frontmatter_value_with_diagnostic(note_content_original, "link_to_repo_readme", filepath)
                
                if not repo_readme_link:
                    bibtex_fetch_failed_papers.append(filepath + " (Reason: link_to_repo_readme not found in frontmatter)")
                    continue
                
                repo_readme_link = repo_readme_link.strip()

                # Removed diagnostic repr() prints for URLs
                # print(f"    [Diagnostic] Comparing link: {repr(repo_readme_link)}")
                # print(f"    [Diagnostic] With base URL:   {repr(GITHUB_REPO_BASE_URL)}")

                if not repo_readme_link.startswith(GITHUB_REPO_BASE_URL):
                    # Keep this warning as it indicates a problem
                    print(f"  [Warning] '{os.path.basename(filepath)}': 'link_to_repo_readme' ({repo_readme_link}) does not start with the expected base URL ({GITHUB_REPO_BASE_URL}). Skipping.")
                    bibtex_fetch_failed_papers.append(filepath + f" (Reason: link_to_repo_readme does not start with expected base URL: {repo_readme_link})")
                    continue

                relative_repo_path = repo_readme_link.replace(GITHUB_REPO_BASE_URL, "")
                local_repo_readme_path = os.path.join(REPO_ROOT_PATH, relative_repo_path)

                repo_readme_content = read_file_content(local_repo_readme_path)
                if not repo_readme_content:
                    # This implies a read error, which is already counted in error_files if read_file_content returns None and prints an error.
                    # However, specifically for BibTeX fetching, this is a failure point.
                    print(f"  [Warning] '{os.path.basename(filepath)}': Could not read repository README for BibTeX: {local_repo_readme_path}")
                    bibtex_fetch_failed_papers.append(filepath + f" (Reason: Could not read repository README: {local_repo_readme_path})")
                    continue

                bibtex_from_repo = extract_bibtex_from_repo_readme(repo_readme_content)

                if not is_bibtex_valid(bibtex_from_repo):
                    # Keep this warning
                    print(f"  [Warning] '{os.path.basename(filepath)}': No valid BibTeX found in repository README: {local_repo_readme_path}")
                    bibtex_fetch_failed_papers.append(filepath + f" (Reason: No valid BibTeX found in repository README: {local_repo_readme_path})")
                    # Check if placeholder {{bibtex}} might still exist in note if original was empty
                    if "{{bibtex}}" in note_content_original:
                        print(f"    [{os.path.basename(filepath)}] Original note contains {{bibtex}} placeholder. Clearing it.")
                        updated_note_with_bibtex = update_bibtex_in_note_body(note_content_original, "")
                        final_content_to_write = update_frontmatter_field(updated_note_with_bibtex, "last_updated", datetime.now().strftime("%Y-%m-%d"))
                        if write_file_content(filepath, final_content_to_write):
                            if filepath not in (err.get('filepath') for err in updated_files_details): # Avoid double counting if already marked for other reasons
                                updated_files +=1
                                updated_files_details.append({'filepath': filepath, 'change': 'Cleared bibtex placeholder'})
                    continue

                # Keep update messages
                if current_bibtex_in_note and bibtex_from_repo.strip() == current_bibtex_in_note.strip():
                    print(f"  ['{os.path.basename(filepath)}'] Fetched BibTeX identical to existing (but initially deemed invalid). Updating 'last_updated'.")
                    final_content_to_write = update_frontmatter_field(note_content_original, "last_updated", datetime.now().strftime("%Y-%m-%d"))
                    action_taken = True
                    update_reason = 'Updated last_updated (BibTeX matched after fetch)'
                else:
                    print(f"  ['{os.path.basename(filepath)}'] Valid BibTeX fetched from repository. Updating note.")
                    updated_note_with_bibtex = update_bibtex_in_note_body(note_content_original, bibtex_from_repo)
                    final_content_to_write = update_frontmatter_field(updated_note_with_bibtex, "last_updated", datetime.now().strftime("%Y-%m-%d"))
                    action_taken = True
                    update_reason = 'Updated BibTeX and last_updated'

                if action_taken:
                    if write_file_content(filepath, final_content_to_write):
                        if filepath not in (upd.get('filepath') for upd in updated_files_details):
                             updated_files += 1
                             updated_files_details.append({'filepath': filepath, 'change': update_reason})
                    else:
                        error_files += 1
                        # error_files_details.append({'filepath': filepath, 'error': 'Write failed'})
            
    print(f"\n--- Summary ---")
    print(f"Total files scanned in PAPERS_DIR_OBSIDIAN: {processed_files}") # Renamed for clarity
    # print(f"Files updated or requiring attention: {len(updated_files_details)}")
    print(f"Files successfully updated: {updated_files}")
    # for item in updated_files_details:
    #     print(f"  - Updated: {item['filepath']} (Reason: {item['change']})")
    print(f"Files with errors (read/write/other critical): {error_files}")
    # for item in error_files_details:
    #     print(f"  - Error: {item['filepath']} (Reason: {item['error']})")
    print("BibTeX refetch process completed.")

    if bibtex_fetch_failed_papers:
        failed_list_filepath = os.path.join(OBSIDIAN_VAULT_BASE_PATH, "scripts", "bibtex_fetch_failed.txt")
        try:
            with open(failed_list_filepath, 'w', encoding='utf-8') as f_failed:
                f_failed.write("List of papers where BibTeX could not be fetched or was invalid:\n")
                for paper_path_reason in bibtex_fetch_failed_papers:
                    f_failed.write(f"{paper_path_reason}\n")
            print(f"\nA list of papers where BibTeX fetching failed has been saved to: {failed_list_filepath}")
        except Exception as e_write_failed:
            print(f"\n[Error] Could not write the list of failed BibTeX fetches to {failed_list_filepath}: {e_write_failed}")

if __name__ == "__main__":
    if not os.path.isdir(PAPERS_DIR_OBSIDIAN):
        print(f"[CRITICAL ERROR] Papers directory not found: {PAPERS_DIR_OBSIDIAN}")
        print("Please ensure the configuration at the top of the script is correct.")
    elif not os.path.isdir(REPO_ROOT_PATH):
        print(f"[CRITICAL ERROR] graph-based-deep-learning-literature repository path not found: {REPO_ROOT_PATH}")
        print("Please ensure the cloned repository exists at the configured path.")
    else:
        main() 