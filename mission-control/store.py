"""Tiny JSON-file store for Mission Control: leads, money figures, template approvals."""
import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from next_action import ACTION_IDS

log = logging.getLogger("mission-control.store")

STATUSES = ("new", "contacted", "replied", "call", "won", "lost")
TALKING = ("replied", "call", "won")
CALLED = ("call", "won")
MAX_FIELD_CHARS = 200
MAX_NOTES_CHARS = 2000
LEAD_FIELDS = ("business", "contact", "email", "notes")
MAX_ANSWER_CHARS = 8000
COUNCIL_ASKERS = ("Alan", "Axiom")
# topic -> gstack plan-review skill that suits it
COUNCIL_TOPICS = {"general": "/autoplan", "strategy": "/plan-ceo-review", "engineering": "/plan-eng-review",
                  "design": "/plan-design-review", "devex": "/plan-devex-review"}


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

    # ---- council questions ----
    def questions(self) -> list:
        return self._read("council.json", [])

    def add_question(self, fields: dict) -> dict:
        question = _clean_text(fields.get("question"), MAX_NOTES_CHARS)
        if not question:
            raise ValueError("question is required")
        if fields.get("asked_by") not in COUNCIL_ASKERS:
            raise ValueError("asked_by must be Alan or Axiom")
        if fields.get("topic") not in COUNCIL_TOPICS:
            raise ValueError("unknown topic")
        record = {
            "id": uuid.uuid4().hex[:10], "question": question, "asked_by": fields["asked_by"],
            "topic": fields["topic"], "status": "open", "answer": "", "answer_source": "", "created": _now(),
        }
        with self._lock:
            self._write("council.json", [record, *self.questions()])
        return record

    def answer_question(self, question_id: str, answer: str, source: str) -> dict:
        text = _clean_text(answer, MAX_ANSWER_CHARS)
        if not text:
            raise ValueError("answer is required")
        with self._lock:
            current = self.questions()
            if not any(q["id"] == question_id for q in current):
                raise KeyError(question_id)
            updated = [{**q, "status": "answered", "answer": text, "answer_source": _clean_text(source, 40), "answered": _now()}
                       if q["id"] == question_id else q for q in current]
            self._write("council.json", updated)
        return next(q for q in updated if q["id"] == question_id)

    def delete_question(self, question_id: str) -> None:
        with self._lock:
            self._write("council.json", [q for q in self.questions() if q["id"] != question_id])

    def asked_today(self) -> bool:
        today = datetime.now(timezone.utc).date().isoformat()
        return any(q["created"].startswith(today) for q in self.questions())

    def dismissed_today(self) -> bool:
        return self._read("council_prompt.json", {}).get("date") == datetime.now(timezone.utc).date().isoformat()

    def dismiss_today(self) -> None:
        with self._lock:
            self._write("council_prompt.json", {"date": datetime.now(timezone.utc).date().isoformat()})

    # ---- next-action bookkeeping ----
    def next_done(self) -> set:
        return set(self._read("next_done.json", []))

    def mark_next_done(self, action_id: str) -> None:
        if action_id not in ACTION_IDS:
            raise ValueError("unknown action")
        with self._lock:
            self._write("next_done.json", sorted(self.next_done() | {action_id}))

    def snooze(self, action_id: str) -> None:
        if action_id not in ACTION_IDS:
            raise ValueError("unknown action")
        today = datetime.now(timezone.utc).date().isoformat()
        with self._lock:
            self._write("snoozed.json", {**self._read("snoozed.json", {}), action_id: today})

    def snoozed_today(self) -> set:
        today = datetime.now(timezone.utc).date().isoformat()
        return {k for k, v in self._read("snoozed.json", {}).items() if v == today}

    # ---- daily route ----
    def merge_route(self, stops: list) -> list:
        """Today's route snapshot: starts with the first plan of the day, new stops are appended, none dropped."""
        today = datetime.now(timezone.utc).date().isoformat()
        with self._lock:
            saved = self._read("route.json", {})
            current = saved.get("stops", []) if saved.get("date") == today else []
            known = {s["key"] for s in current}
            merged = [*current, *({"key": k, "title": t} for k, t in stops if k not in known)]
            self._write("route.json", {"date": today, "stops": merged})
        return merged
