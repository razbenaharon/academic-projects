"""Check tracked public files without printing matched identifiers or credentials.

Heuristic check, not an assurance about embedded pixels or hosting-service caches.
Notebook outputs and submission metadata must be absent in the published copy.
"""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"(?<![\w.])\d{9}(?![\w.])")
SECRET = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|"
    r"sk-(?:proj-)?[A-Za-z0-9_-]{32,}|AKIA[A-Z0-9]{16}|"
    r"AIza[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"
)
USER_PATH = re.compile(r"(?i)\b[a-z]:[\\/]+users[\\/]+[^\\/\s\"']+")


def valid_id(s):
    if len(set(s)) < 3:
        return False
    digits = [int(c) * (1 + i % 2) for i, c in enumerate(s)]
    return sum(x if x < 10 else x - 9 for x in digits) % 10 == 0


def inspect_text(name, text, problems):
    for kind, found in [
        ("possible personal identifier", any(valid_id(m.group()) for m in ID.finditer(text))),
        ("credential-shaped text", bool(SECRET.search(text))),
        ("local Windows user path", bool(USER_PATH.search(text))),
    ]:
        if found:
            problems.append((name, kind))
    if name.endswith(".py"):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Constant):
                continue
            value = node.value.value
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if isinstance(value, str) and len(value) >= 16 and any(
                re.search(r"(?:API_KEY|PASSWORD|SECRET|TOKEN)$", t, re.I) for t in targets
            ) and not any(x in value.lower() for x in ("example", "your-", "placeholder")):
                problems.append((name, f"literal credential candidate at line {node.lineno}"))


def main():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    problems = []
    checked = 0
    for name in filter(None, names):
        p = ROOT / name
        if not p.is_file():
            continue
        checked += 1
        if re.search(r"\d{9}", name):
            problems.append((name, "identifier-shaped filename"))
        if p.name.startswith(".env") and p.name != ".env.example":
            problems.append((name, "tracked environment file"))
        if p.suffix == ".pdf":
            try:
                import fitz
            except ImportError:
                problems.append((name, "PDF inspection requires PyMuPDF"))
                continue
            with fitz.open(p) as doc:
                inspect_text(name, "\n".join(page.get_text() for page in doc) + json.dumps(doc.metadata), problems)
            continue
        if p.suffix == ".pptx":
            with zipfile.ZipFile(p) as z:
                for item in z.namelist():
                    if item.endswith(".xml"):
                        inspect_text(name, z.read(item).decode("utf-8"), problems)
            continue
        try:
            text = p.read_text(encoding="utf-8-sig")
        except UnicodeError:
            continue
        inspect_text(name, text, problems)
        if p.suffix == ".ipynb":
            doc = json.loads(text)
            for cell in doc["cells"]:
                if cell.get("outputs") or cell.get("attachments") or cell.get("metadata"):
                    problems.append((name, "notebook output/attachment/cell metadata"))
                    break
            if any(k not in {"kernelspec", "language_info"} for k in doc.get("metadata", {})):
                problems.append((name, "nonstandard notebook metadata"))
    for name, reason in sorted(set(problems)):
        print(re.sub(r"\d{9}", "[redacted]", name) + ": " + reason)
    print(f"Checked {checked} tracked files; {len(set(problems))} findings.")
    return bool(problems)


if __name__ == "__main__":
    sys.exit(main())
