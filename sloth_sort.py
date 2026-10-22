#!/usr/bin/env python3
"""
SlothSort: The Autonomous, 100% Offline Local File Organizer
Hacktoberfest "Slow and Steady" Challenge

Channel your inner sloth: Drop any cluttered file into `inbox/`,
and SlothSort uses a local open-weight model (llama3.2:3b via Ollama)
to inspect the file content, smartly classify it, rename it cleanly,
and file it away into `organized/` — with 0 API costs and 100% privacy.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

# Ensure stdout and stderr handle utf-8 characters smoothly on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)

# ---------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------
INBOX_DIR = Path("inbox")
ORGANIZED_DIR = Path("organized")

CATEGORIES = [
    "Invoices_and_Finance",
    "Academics_and_Notes",
    "Code_and_Dev",
    "Identity_and_Docs",
    "Media_and_Design",
    "Misc",
]

DEFAULT_MODEL = "llama3.2:3b"

# Banner & Sloth Quotes
SLOTH_BANNER = f"""
{Fore.GREEN}  .---.   _     {Fore.YELLOW}  ___ _      _   _   ___             _   
{Fore.GREEN} /  _  \\ | |    {Fore.YELLOW} / __| |___ | |_| |_/ __| ___ _ _ _| |_ 
{Fore.GREEN}|  / \\  || |__  {Fore.YELLOW} \\__ \\ / _ \\|  _| ' \\__ \\/ _ \\ '_|  _|
{Fore.GREEN}|  \\_/  || '_ \\ {Fore.YELLOW} |___/_\\___/ \\__|_||_|___/\\___/_|  \\__|
{Fore.GREEN} \\___/\\_/|_.__/ {Fore.CYAN} 🦥  Channel your inner sloth: Slow & Steady 🦥
"""

SLOTH_QUOTES = [
    "Why rush? A clean directory is a marathon, not a sprint.",
    "Moving slowly, thinking deeply, sorting accurately.",
    "Channeling total sloth energy: Zero effort required from you.",
    "No cloud subscriptions, no data leaks, no human intervention.",
    "Resting peacefully while open-weight AI does the heavy lifting.",
]


def log_sloth(msg: str, color=Fore.CYAN):
    print(f"{Fore.GREEN}[🦥 SlothSort]{Style.RESET_ALL} {color}{msg}{Style.RESET_ALL}")


def log_step(action: str, detail: str):
    print(f"  {Fore.YELLOW}↳ {action}:{Style.RESET_ALL} {detail}")


# ---------------------------------------------------------
# Content Extractor
# ---------------------------------------------------------
def extract_file_snippet(file_path: Path) -> Tuple[str, str]:
    """
    Extracts up to 800-1000 characters from supported file formats.
    Returns:
        (content_snippet, extraction_method)
    """
    ext = file_path.suffix.lower()

    # 1. PDF extraction using pypdf
    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            if len(reader.pages) > 0:
                first_page_text = reader.pages[0].extract_text() or ""
                snippet = first_page_text.strip()[:800]
                if snippet:
                    return snippet, "pypdf (first page)"
            return "[PDF empty or unextractable text]", "pypdf (empty)"
        except Exception as e:
            return f"[PDF extraction failed: {e}]", "pypdf (error)"

    # 2. Text-based file extraction
    text_extensions = {
        ".txt", ".md", ".json", ".csv", ".py", ".sql", ".html", ".css",
        ".js", ".ts", ".sh", ".bash", ".yml", ".yaml", ".xml", ".log",
        ".rst", ".toml", ".ini", ".conf", ".c", ".cpp", ".h", ".java",
        ".rs", ".go", ".env", ".tex"
    }

    if ext in text_extensions:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                snippet = f.read(1000).strip()
                if snippet:
                    return snippet, f"text reader ({ext})"
                return "[Empty text file]", "text reader"
        except Exception as e:
            return f"[Text extraction failed: {e}]", "text reader (error)"

    # 3. Fallback for binary / unsupported formats
    return f"[Binary or unsupported format '{ext}'. Relying on filename.]", "filename-only"


# ---------------------------------------------------------
# Fallback Heuristics (When LLM is unreachable or errors)
# ---------------------------------------------------------
def sanitize_snake_case(filename: str) -> str:
    """Generate a clean snake_case filename, preserving original extension."""
    path = Path(filename)
    stem = path.stem.lower()
    ext = path.suffix.lower()

    # Replace spaces and punctuation with underscores
    clean_stem = re.sub(r"[^\w\d]+", "_", stem).strip("_")
    if not clean_stem:
        clean_stem = "file"
    return f"{clean_stem}{ext}"


def rule_based_fallback(file_path: Path, content_snippet: str) -> Dict[str, str]:
    """Deterministic rule-based classification fallback."""
    name_lower = file_path.name.lower()
    content_lower = content_snippet.lower()
    combined = f"{name_lower} {content_lower}"
    ext = file_path.suffix.lower()

    # Rule 1: Code and Dev
    code_exts = {".py", ".js", ".ts", ".sql", ".html", ".css", ".sh", ".java", ".cpp", ".c", ".rs", ".go"}
    if ext in code_exts or any(k in combined for k in ["def ", "class ", "import ", "function ", "select ", "insert into"]):
        return {
            "category": "Code_and_Dev",
            "clean_name": sanitize_snake_case(file_path.name),
            "reason": "File extension or content matches software development source code."
        }

    # Rule 2: Invoices and Finance
    finance_keywords = ["invoice", "receipt", "bill", "tax", "gst", "subtotal", "payment", "due date", "paid", "amount"]
    if any(k in combined for k in finance_keywords):
        return {
            "category": "Invoices_and_Finance",
            "clean_name": sanitize_snake_case(file_path.name),
            "reason": "Keywords indicate a financial transaction, bill, or invoice."
        }

    # Rule 3: Academics and Notes
    academic_keywords = ["assignment", "lecture", "homework", "exam", "syllabus", "notes", "algorithm", "cs ", "b-tree", "chapter"]
    if any(k in combined for k in academic_keywords):
        return {
            "category": "Academics_and_Notes",
            "clean_name": sanitize_snake_case(file_path.name),
            "reason": "Keywords suggest academic study material or lecture notes."
        }

    # Rule 4: Identity and Docs
    id_keywords = ["passport", "license", "aadhaar", "ssn", "resume", "curriculum vitae", "certificate", "id_card", "identification"]
    if any(k in combined for k in id_keywords):
        return {
            "category": "Identity_and_Docs",
            "clean_name": sanitize_snake_case(file_path.name),
            "reason": "Keywords relate to personal identity or official credentials."
        }

    # Rule 5: Media and Design
    media_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".mp4", ".mov", ".mp3", ".wav", ".psd", ".ai"}
    if ext in media_exts:
        return {
            "category": "Media_and_Design",
            "clean_name": sanitize_snake_case(file_path.name),
            "reason": "File extension indicates media or visual graphic asset."
        }

    # Default: Misc
    return {
        "category": "Misc",
        "clean_name": sanitize_snake_case(file_path.name),
        "reason": "Standard fallback classification."
    }


# ---------------------------------------------------------
# Ollama LLM Classifier
# ---------------------------------------------------------
def classify_with_ollama(file_path: Path, content_snippet: str, model: str = DEFAULT_MODEL) -> Dict[str, str]:
    """
    Invokes the local Ollama LLM to classify and name the file.
    Demands strict JSON output with defined categories.
    Falls back gracefully if Ollama is unreachable.
    """
    categories_str = ", ".join([f'"{c}"' for c in CATEGORIES])

    system_prompt = (
        "You are SlothSort, an intelligent file organization agent. "
        "Your task is to analyze an incoming file's name and its content snippet, "
        "categorize it into EXACTLY ONE of the allowed categories, and suggest a clean descriptive snake_case filename.\n\n"
        f"Allowed categories: [{categories_str}].\n\n"
        "Rules:\n"
        "1. 'category' must be verbatim one of the allowed categories.\n"
        "2. 'clean_name' must be in descriptive_snake_case and MUST preserve the original file extension.\n"
        "3. 'reason' must be a concise, one-line justification.\n"
        "4. Respond with valid JSON only. No explanations, no markdown ticks."
    )

    user_prompt = (
        f"File Name: {file_path.name}\n"
        f"File Extension: {file_path.suffix}\n"
        f"Content Snippet:\n\"\"\"\n{content_snippet}\n\"\"\"\n\n"
        "Provide JSON output:"
    )

    try:
        import ollama

        # Request JSON response from local Ollama model
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
            options={"temperature": 0.1}
        )

        raw_output = response["message"]["content"]
        data = json.loads(raw_output)

        # Validate category
        category = data.get("category", "").strip()
        if category not in CATEGORIES:
            # Try fuzzy match or default
            matched = [c for c in CATEGORIES if c.lower() in category.lower()]
            category = matched[0] if matched else "Misc"

        # Validate clean_name
        clean_name = data.get("clean_name", "").strip()
        if not clean_name:
            clean_name = sanitize_snake_case(file_path.name)
        else:
            # Ensure it retains original extension
            orig_ext = file_path.suffix.lower()
            if not clean_name.lower().endswith(orig_ext):
                clean_name = f"{Path(clean_name).stem}{orig_ext}"
            clean_name = sanitize_snake_case(clean_name)

        reason = data.get("reason", "Organized via local LLM analysis.").strip()

        return {
            "category": category,
            "clean_name": clean_name,
            "reason": reason,
            "source": f"Local Ollama ({model})"
        }

    except Exception as e:
        # Graceful fallback to deterministic rule engine
        fallback = rule_based_fallback(file_path, content_snippet)
        fallback["source"] = f"Heuristic Rule Engine (Ollama fallback: {type(e).__name__})"
        return fallback


# ---------------------------------------------------------
# Action & File Mover (Handles Collisions Safely)
# ---------------------------------------------------------
def move_and_organize_file(file_path: Path, organized_dir: Path, classification: Dict[str, str]) -> Path:
    """
    Safely moves and renames a file into organized/<category>/<clean_name>.
    Resolves naming collisions by appending a numeric counter.
    """
    category = classification["category"]
    clean_name = classification["clean_name"]

    target_dir = organized_dir / category
    target_dir.mkdir(parents=True, exist_ok=True)

    dest_path = target_dir / clean_name

    # Handle collision if file already exists
    if dest_path.exists():
        stem = Path(clean_name).stem
        ext = Path(clean_name).suffix
        counter = 1
        while dest_path.exists():
            dest_path = target_dir / f"{stem}_{counter}{ext}"
            counter += 1

    shutil.move(str(file_path), str(dest_path))
    return dest_path


# ---------------------------------------------------------
# Process a Single File
# ---------------------------------------------------------
def process_file(file_path: Path, organized_dir: Path = ORGANIZED_DIR, model: str = DEFAULT_MODEL):
    """Full pipeline for one file: Extract -> Classify -> Move."""
    if not file_path.is_file() or file_path.name.startswith("."):
        return None

    print(f"\n{Fore.MAGENTA}{'━' * 60}")
    log_sloth(f"Examining: {Fore.WHITE}{Style.BRIGHT}{file_path.name}")

    # 1. Content Extraction
    snippet, method = extract_file_snippet(file_path)
    log_step("Extraction", f"via {method} ({len(snippet)} chars)")

    # 2. Local AI Classification
    log_step("Classifying", f"with {Fore.GREEN}{model} (100% offline)...")
    classification = classify_with_ollama(file_path, snippet, model=model)

    log_step("Category", f"{Fore.GREEN}{classification['category']}")
    log_step("Clean Name", f"{Fore.YELLOW}{classification['clean_name']}")
    log_step("Reason", f"{Fore.WHITE}{classification['reason']}")
    log_step("Engine", f"{Fore.CYAN}{classification.get('source', 'Local')}")

    # 3. Safe File Movement
    dest = move_and_organize_file(file_path, organized_dir, classification)
    log_step("Filed to", f"{Fore.GREEN}{dest}")
    return dest


# ---------------------------------------------------------
# Mode: Batch Processing
# ---------------------------------------------------------
def run_batch_mode(inbox_dir: Path = INBOX_DIR, organized_dir: Path = ORGANIZED_DIR, model: str = DEFAULT_MODEL):
    """Processes all existing files currently sitting in inbox/."""
    inbox_dir.mkdir(parents=True, exist_ok=True)
    organized_dir.mkdir(parents=True, exist_ok=True)

    files = [f for f in inbox_dir.iterdir() if f.is_file() and not f.name.startswith(".")]

    if not files:
        log_sloth(f"Inbox is empty! Perfect sloth moment: nothing to do. 😴", color=Fore.YELLOW)
        return

    log_sloth(f"Found {len(files)} cluttered file(s) in '{inbox_dir}/'. Initiating batch sort...")

    processed_count = 0
    start_time = time.time()

    for file_path in files:
        dest = process_file(file_path, organized_dir, model=model)
        if dest:
            processed_count += 1

    elapsed = time.time() - start_time
    print(f"\n{Fore.GREEN}{'━' * 60}")
    log_sloth(
        f"Batch sorting complete! Successfully organized {processed_count} file(s) in {elapsed:.2f}s.",
        color=Fore.GREEN
    )
    print(f"{Fore.CYAN}Check your sorted files in: {organized_dir.resolve()}\n")


# ---------------------------------------------------------
# Mode: Watcher Daemon (Watchdog)
# ---------------------------------------------------------
def run_watch_mode(inbox_dir: Path = INBOX_DIR, organized_dir: Path = ORGANIZED_DIR, model: str = DEFAULT_MODEL):
    """Live-monitors inbox/ using watchdog and organizes files as they drop."""
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    inbox_dir.mkdir(parents=True, exist_ok=True)
    organized_dir.mkdir(parents=True, exist_ok=True)

    class SlothEventHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            file_path = Path(event.src_path)
            # Give file writer a moment to finish writing
            time.sleep(0.5)
            if file_path.exists():
                process_file(file_path, organized_dir, model=model)

    event_handler = SlothEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(inbox_dir), recursive=False)
    observer.start()

    log_sloth(f"Watcher Daemon ACTIVE on '{inbox_dir}/'. Drop any file in here to sort it!", color=Fore.GREEN)
    log_sloth("Press Ctrl+C anytime to stop.\n", color=Fore.YELLOW)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_sloth("\nStopping watcher daemon... Sloth is returning to slumber. 🦥", color=Fore.YELLOW)
        observer.stop()
    observer.join()


# ---------------------------------------------------------
# Main CLI Entrypoint
# ---------------------------------------------------------
def main():
    print(SLOTH_BANNER)

    parser = argparse.ArgumentParser(
        description="SlothSort: Autonomous 100% offline file organizer using local open-weight LLMs via Ollama."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--batch",
        action="store_true",
        help="Run batch mode: Sort all unorganized files currently in inbox/."
    )
    group.add_argument(
        "--watch",
        action="store_true",
        help="Run watcher daemon mode: Live-monitor inbox/ and sort files as they appear."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL})."
    )

    args = parser.parse_args()

    if args.batch:
        run_batch_mode(model=args.model)
    elif args.watch:
        run_watch_mode(model=args.model)


if __name__ == "__main__":
    main()
