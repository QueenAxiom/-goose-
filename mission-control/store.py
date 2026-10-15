"""Tiny JSON-file store for Mission Control: leads, money figures, template approvals."""
import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("mission-control.store")

STATUSES = ("new", "contacted", "replied", "call", "won", "lost")
TALKING = ("replied", "call", "won")
CALLED = ("call", "won")
MAX_FIELD_CHARS = 200
MAX_NOTES_CHARS = 2000
LEAD_FIELDS = ("business", "contact", "email", "notes")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _clean_text(value, limit: int) -> str:
    text = "" if value is None else str(value).strip()
    if len(text) > limit:
        raise ValueError(f"field too long (max {limit})")
    return text


class Store:
    def __init__(self, directory: Path):
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _read(self, name: str, default):
        try:
            return json.loads((self._dir / name).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return default
        except ValueError:
            log.error("corrupt store file %s; using empty default", name)
            return default

    def _write(self, name: str, data) -> None:
        tmp = self._dir / f"{name}.tmp"
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, self._dir / name)

    def leads(self) -> list:
        return self._read("leads.json", [])

    def add_lead(self, fields: dict) -> dict:
        business = _clean_text(fields.get("business"), MAX_FIELD_CHARS)
        if not business:
            raise ValueError("business is required")
        lead = {
            "id": uuid.uuid4().hex[:10],
            "business": business,
            "contact": _clean_text(fields.get("contact"), MAX_FIELD_CHARS),
            "email": _clean_text(fields.get("email"), MAX_FIELD_CHARS),
            "notes": _clean_text(fields.get("notes"), MAX_NOTES_CHARS),
            "status": "new",
            "created": _now(),
        }
        with self._lock:
            self._write("leads.json", [*self.leads(), lead])
        return lead

    def update_lead(self, lead_id: str, changes: dict) -> dict:
        patch = {}
        if "status" in changes:
            if changes["status"] not in STATUSES:
                raise ValueError("unknown status")
            patch["status"] = changes["status"]
        for key in LEAD_FIELDS:
            if key in changes:
                patch[key] = _clean_text(changes[key], MAX_NOTES_CHARS if key == "notes" else MAX_FIELD_CHARS)
        with self._lock:
            current = self.leads()
            if not any(l["id"] == lead_id for l in current):
                raise KeyError(lead_id)
            updated = [{**l, **patch, "updated": _now()} if l["id"] == lead_id else l for l in current]
            self._write("leads.json", updated)
        return next(l for l in updated if l["id"] == lead_id)

    def delete_lead(self, lead_id: str) -> None:
        with self._lock:
            self._write("leads.json", [l for l in self.leads() if l["id"] != lead_id])

    def set_money(self, mrr, cash) -> None:
        for value in (mrr, cash):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise ValueError("money values must be non-negative numbers")
        with self._lock:
            self._write("money.json", {"mrr": mrr, "cash": cash, "updated": _now()})

    def scoreboard(self) -> dict:
        leads = self.leads()
        money = self._read("money.json", {})
        return {
            "leads": len(leads),
            "conversations": sum(l["status"] in TALKING for l in leads),
            "calls": sum(l["status"] in CALLED for l in leads),
            "sales": sum(l["status"] == "won" for l in leads),
            "mrr": money.get("mrr", 0),
            "cash": money.get("cash", 0),
        }

    def approvals(self) -> dict:
        return self._read("approvals.json", {})

    def set_approval(self, template_id: str, approved: bool) -> None:
        with self._lock:
            self._write("approvals.json", {**self.approvals(), template_id: {"approved": bool(approved), "at": _now()}})

    def posts(self) -> list:
        return self._read("posts.json", [])

    def add_post(self, fields: dict) -> dict:
        record = {
            "id": uuid.uuid4().hex[:10],
            "platform": str(fields["platform"]),
            "text": str(fields["text"]),
            "post_id": str(fields.get("post_id", "")),
            "created": _now(),
            "deleted": False,
        }
        with self._lock:
            self._write("posts.json", [record, *self.posts()])
        return record

    def mark_post_deleted(self, record_id: str) -> None:
        with self._lock:
            self._write("posts.json", [{**p, "deleted": True} if p["id"] == record_id else p for p in self.posts()])

    def recent_duplicate(self, platform: str, text: str, seconds: int) -> bool:
        """True if the same text went to the same platform within the window and wasn't undone."""
        needle = " ".join(text.lower().split())
        cutoff = datetime.now(timezone.utc).timestamp() - seconds
        return any(
            p["platform"] == platform and not p["deleted"] and " ".join(p["text"].lower().split()) == needle
            and datetime.fromisoformat(p["created"]).timestamp() >= cutoff
            for p in self.posts()
        )
