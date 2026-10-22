# 🦥 SlothSort: Channel Your Inner Sloth

> **Autonomous, 100% Offline Local File Organizer powered by Open-Weight AI (`llama3.2:3b` via Ollama).**  
> *Built for the Hacktoberfest "Slow and Steady" Challenge.* 🌿

---

```
  .---.   _       ___ _      _   _   ___             _   
 /  _  \ | |     / __| |___ | |_| |_/ __| ___ _ _ _| |_ 
|  / \  || |__   \__ \ / _ \|  _| ' \__ \/ _ \ '_|  _|
|  \_/  || '_ \  |___/_\___/ \__|_||_|___/\___/_|  \__|
 \___/\_/|_.__/  🦥 Zero effort file organization 🦥
```

---

## 💡 The Problem: Digital Hoarding & Cluttered Inboxes
Every developer, student, and knowledge worker has a chaotic **Downloads** or **Inbox** folder filled with messy names like:
- `receipt_oct.txt`
- `db_assignment_notes.md`
- `script_dump.py`
- `IMG_20261014_9482.pdf`
- `unnamed_export (3).json`

Manually inspecting, renaming, and filing them is tedious. **SlothSort solves this by doing the work so you don't have to lift a finger.** Just drop files into `inbox/`, and SlothSort inspects their contents, smartly classifies them into clean directories, and generates descriptive snake_case names.

---

## 🛡️ Why Local AI & Open Innovation Matter

In the era of cloud API subscriptions and SaaS bloat, SlothSort takes a firm stance:

1. **🔒 100% Offline & Private**:
   Your bank statements, medical records, university notes, and private code never leave your computer. No data goes to external APIs.
2. **💰 ₹0 / $0 Forever (Zero API Costs)**:
   Runs entirely on local hardware using `llama3.2:3b` via Ollama. No monthly quotas, no billing alarms, no surprise tokens.
3. **⚡ Built for Real Laptops**:
   Optimized for everyday developer hardware (efficiently runs on 6 GB VRAM GPUs like RTX 3050 or CPUs with system RAM).
4. **🌱 Resilient Fallbacks**:
   Even if the local model is offline or unreachable, an intelligent heuristic rule engine ensures your files are never lost or unorganized.

---

## 📂 Category Taxonomy

SlothSort organizes your digital life into 6 defined buckets under `organized/`:

| Category | Typical Files |
| :--- | :--- |
| **`Invoices_and_Finance`** | AWS bills, grocery receipts, tax invoices, bank statements |
| **`Academics_and_Notes`** | Lecture slides, B-Tree notes, university assignments, study guides |
| **`Code_and_Dev`** | Python scripts, SQL dumps, shell scripts, JSON configs, source files |
| **`Identity_and_Docs`** | Resumes, certificates, licenses, identity scans |
| **`Media_and_Design`** | UI mockups, icons, screenshots, audio clips, video recordings |
| **`Misc`** | Everything else that needs a safe, temporary home |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (tested on Python 3.12, 3.13, 3.14)
- **Ollama**: Installed and running locally ([Download Ollama](https://ollama.com/download))

### 2. Pull the Local Model
In your terminal, pull the compact `llama3.2:3b` model:
```bash
ollama run llama3.2:3b
```
*(You can type `/bye` once the prompt loads. Ollama keeps the model ready in the background!)*

### 3. Setup Virtual Environment & Install Dependencies
Clone this repository and navigate to the project root:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## 🎮 How to Run SlothSort

### Mode 1: Batch Mode (`--batch`)
Process all cluttered files currently sitting inside `inbox/`:
```bash
python sloth_sort.py --batch
```
SlothSort scans every file in `inbox/`, extracts a content snippet, prompts the local model for strict JSON classification, and safely moves them into `organized/<Category>/<clean_snake_case_name>`.

### Mode 2: Watcher Daemon Mode (`--watch`)
Leave SlothSort running in the background. As soon as you save or download any file into `inbox/`, it automatically sorts it in real-time:
```bash
python sloth_sort.py --watch
```
*(Press `Ctrl+C` anytime to return the sloth to slumber!)*

---

## 🧪 Included Sample Test Files

The repository comes pre-populated with mock test files in `inbox/`:
- `inbox/receipt_oct.txt` -> Organizes to `organized/Invoices_and_Finance/aws_cloud_web_services_october_invoice.txt`
- `inbox/db_assignment_notes.md` -> Organizes to `organized/Academics_and_Notes/cs_401_btree_indexing_assignment_notes.md`
- `inbox/script_dump.py` -> Organizes to `organized/Code_and_Dev/bubble_sort_demo.py`

---

## 🏗️ Architecture & Extensibility

```
SlothSort/
├── inbox/                  # Drop cluttered files here
├── organized/              # Clean categorized destination
│   ├── Invoices_and_Finance/
│   ├── Academics_and_Notes/
│   ├── Code_and_Dev/
│   ├── Identity_and_Docs/
│   ├── Media_and_Design/
│   └── Misc/
├── sloth_sort.py           # Core agent pipeline (Extract -> Prompt -> Move)
├── requirements.txt        # Minimal, clean dependencies
├── .gitignore              # Ignores venv, caches, inbox/organized contents
└── README.md               # Documentation & Hacktoberfest guide
```

### Content Extractors
- **PDF Documents**: Uses `pypdf` to extract first-page text (up to 800 chars) for zero-latency analysis.
- **Code & Text**: Supports `.txt`, `.md`, `.py`, `.sql`, `.json`, `.csv`, `.sh`, `.yml`, `.html`, `.css`, and more.
- **Binary / Media**: Gracefully falls back to filename and metadata signals.

---

## 🦥 The Sloth Philosophy
> *"Why spend 10 minutes renaming files every week when a local 3B model can do it for free while you take a nap?"*

Happy Hacktoberfest! 🎃 Contributions, PRs, and new extractors are welcome!
