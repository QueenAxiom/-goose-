"""Show Alan the files that changed, in copy-paste form. Read-only, confined to the repo."""
import os
import subprocess
from pathlib import Path

MAX_FILE_BYTES = 200_000
GIT_TIMEOUT_SECONDS = 20
DENIED_NAMES = (".git", ".env")  # any path part equal to these, or a file starting with ".env"
DENIED_PREFIXES = ("mission-control/data",)
STATUS_WORDS = {"??": "new", "A": "new", "D": "deleted"}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=GIT_TIMEOUT_SECONDS)


def _status_word(code: str) -> str:
    if code == "??":
        return "new"
    flags = code.replace(" ", "")
    return "deleted" if "D" in flags else "new" if flags.startswith("A") else "modified"


def changed_files(repo: Path) -> list:
    """Uncommitted changes: [{path, status}] with status new, modified or deleted."""
    out = _git(repo, "status", "--porcelain", "-z", "-uall").stdout
    entries, i, result = out.split("\0"), 0, []
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        code, path = entry[:2], entry[3:]
        if code[0] == "R" or code[1] == "R":
            i += 1  # renames carry the old path as a separate entry
        result.append({"path": path, "status": _status_word(code)})
    return result


def _fingerprint(repo: Path, rel: str) -> "tuple | None":
    try:
        st = (repo / rel).stat()
    except OSError:
        return None
    return (st.st_mtime_ns, st.st_size)


def snapshot(repo: Path) -> dict:
    return {f["path"]: _fingerprint(repo, f["path"]) for f in changed_files(repo)}


def changed_since(repo: Path, before: dict) -> list:
    """Files whose state differs from an earlier snapshot, i.e. what happened in between."""
    return [f for f in changed_files(repo) if before.get(f["path"], "absent") != _fingerprint(repo, f["path"])]


def _safe_relative(rel: str) -> str:
    cleaned = rel.replace("\\", "/").strip()
    parts = [p for p in cleaned.split("/") if p]
    if not parts or cleaned.startswith("/") or ":" in parts[0] or ".." in parts:
        raise ValueError("path not allowed")
    if any(p in DENIED_NAMES or p.startswith(".env") for p in parts):
        raise ValueError("path not allowed")
    normalized = "/".join(parts)
    if any(normalized == d or normalized.startswith(d + "/") for d in DENIED_PREFIXES):
        raise ValueError("path not allowed")
    return normalized


def read_file(repo: Path, rel: str) -> dict:
    """File content plus its diff, ready to copy. Refuses anything outside the repo, secrets, binaries, huge files."""
    normalized = _safe_relative(rel)
    full = (Path(repo) / normalized).resolve()
    if Path(repo).resolve() not in full.parents:
        raise ValueError("path not allowed")
    if not full.is_file():
        raise KeyError(normalized)
    if full.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("file is too large to show")
    raw = full.read_bytes()
    if b"\x00" in raw:
        raise ValueError("binary file")
    tracked = _git(repo, "ls-files", "--error-unmatch", normalized).returncode == 0
    diff = (_git(repo, "diff", "HEAD", "--no-color", "--", normalized).stdout if tracked
            else _git(repo, "diff", "--no-index", "--no-color", "--", os.devnull if os.name != "nt" else "/dev/null", normalized).stdout)
    content = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")  # LF keeps pasted text clean
    return {"path": normalized, "content": content, "diff": diff}
