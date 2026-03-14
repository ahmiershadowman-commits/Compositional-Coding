"""
SQLite persistence layer — Build Contract Phase 1 / our Phase E.

Single database file; all tables in one schema. The store is append-heavy;
updates are minimal (resolution flags, branch closure, proposal status).

Memory classes: working, episodic, semantic, procedural.
  working   → live context and pointers for the current branch
  episodic  → traces of actions, probes, revisions, decisions
  semantic  → distilled abstractions, invariants, reusable discriminators
  procedural → skills, workflows, critic rules, calibration policies

Memory flow: working → evaluate → distill/archive/discard.
Episodic becomes semantic only through explicit distillation gate (Phase E).
Geometry metadata stays separate from content — retrieval lenses are derived
indexes, not conflated with the records they index.

Zero new dependencies — stdlib sqlite3 only.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator


DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "frontier.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id   TEXT PRIMARY KEY,
    created_at   TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE IF NOT EXISTS branches (
    branch_id        TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL REFERENCES sessions(session_id),
    parent_branch_id TEXT,
    branch_type      TEXT,
    branch_intent    TEXT,
    created_at       TEXT NOT NULL,
    open             INTEGER NOT NULL DEFAULT 1,
    resolution       TEXT
);

CREATE TABLE IF NOT EXISTS frontier_states (
    state_id         TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL REFERENCES sessions(session_id),
    branch_id        TEXT NOT NULL REFERENCES branches(branch_id),
    serialized_state TEXT NOT NULL,
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_records (
    record_id    TEXT PRIMARY KEY,
    class        TEXT NOT NULL CHECK (class IN ('working', 'episodic', 'semantic', 'procedural')),
    branch_id    TEXT NOT NULL REFERENCES branches(branch_id),
    content      TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    used_count   INTEGER NOT NULL DEFAULT 0,
    contradictory INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_memory_class   ON memory_records (class);
CREATE INDEX IF NOT EXISTS idx_memory_branch  ON memory_records (branch_id);

CREATE TABLE IF NOT EXISTS evidence_records (
    evidence_id  TEXT PRIMARY KEY,
    description  TEXT NOT NULL,
    source_ref   TEXT,
    confidence   REAL NOT NULL,
    branch_id    TEXT NOT NULL REFERENCES branches(branch_id),
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id   TEXT PRIMARY KEY,
    description  TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',
    branch_id    TEXT NOT NULL REFERENCES branches(branch_id),
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS critic_findings (
    finding_id          TEXT PRIMARY KEY,
    critic_name         TEXT NOT NULL,
    code                TEXT NOT NULL,
    severity            TEXT NOT NULL,
    blocking            INTEGER NOT NULL DEFAULT 0,
    subject_ids         TEXT NOT NULL,
    message             TEXT NOT NULL,
    suggested_next_move TEXT,
    evidence_refs       TEXT NOT NULL DEFAULT '[]',
    resolved            INTEGER NOT NULL DEFAULT 0,
    branch_id           TEXT NOT NULL REFERENCES branches(branch_id),
    created_at          TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_findings_blocking ON critic_findings (blocking, resolved);

CREATE TABLE IF NOT EXISTS action_proposals (
    proposal_id              TEXT PRIMARY KEY,
    action_type              TEXT NOT NULL,
    payload_ref              TEXT NOT NULL,
    rationale                TEXT NOT NULL,
    frame_id                 TEXT NOT NULL,
    expected_evidence_gain   REAL NOT NULL,
    expected_irreversibility REAL NOT NULL,
    touched_constraints      TEXT NOT NULL DEFAULT '[]',
    touched_anomalies        TEXT NOT NULL DEFAULT '[]',
    fallback_path            TEXT,
    status                   TEXT NOT NULL DEFAULT 'pending',
    branch_id                TEXT NOT NULL REFERENCES branches(branch_id),
    created_at               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gaps (
    gap_id             TEXT PRIMARY KEY,
    gap_type           TEXT NOT NULL,
    issue_level        TEXT NOT NULL,
    loop_stage         TEXT NOT NULL,
    mode               TEXT NOT NULL,
    frame_id           TEXT,
    pressure_snapshot  TEXT NOT NULL,
    missed_cue         TEXT NOT NULL,
    observed_behavior  TEXT NOT NULL,
    better_behavior    TEXT NOT NULL,
    proposed_support   TEXT,
    recurrence_risk    REAL NOT NULL,
    branch_id          TEXT NOT NULL REFERENCES branches(branch_id),
    created_at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_gaps_recurrence ON gaps (recurrence_risk DESC);

CREATE TABLE IF NOT EXISTS events (
    event_id    TEXT PRIMARY KEY,
    event_type  TEXT NOT NULL,
    payload     TEXT NOT NULL,
    branch_id   TEXT,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_type   ON events (event_type);
CREATE INDEX IF NOT EXISTS idx_events_branch ON events (branch_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


class Store:
    """
    SQLite-backed persistence for the frontier cognition runtime.

    One Store per session. Not thread-safe — use one instance per thread
    or add locking if sharing across threads.

    The store never reasons or routes. It persists, retrieves, and emits
    events. Cognitive logic stays in the runtime modules.
    """

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def create_session(self, description: str = "") -> str:
        sid = _new_id("sess_")
        with self._tx() as c:
            c.execute(
                "INSERT INTO sessions (session_id, created_at, description) VALUES (?, ?, ?)",
                (sid, _now(), description),
            )
        return sid

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Branches
    # ------------------------------------------------------------------

    def create_branch(
        self,
        session_id: str,
        branch_type: str,
        branch_intent: str,
        parent_branch_id: str | None = None,
    ) -> str:
        bid = _new_id("br_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO branches
                   (branch_id, session_id, parent_branch_id, branch_type, branch_intent, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (bid, session_id, parent_branch_id, branch_type, branch_intent, _now()),
            )
        self.emit("branch_forked", {"branch_id": bid, "intent": branch_intent}, branch_id=bid)
        return bid

    def close_branch(self, branch_id: str, resolution: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE branches SET open = 0, resolution = ? WHERE branch_id = ?",
                (resolution, branch_id),
            )
        self.emit("branch_closed", {"resolution": resolution}, branch_id=branch_id)

    def get_open_branches(self, session_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM branches WHERE session_id = ? AND open = 1", (session_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Frontier state snapshots
    # ------------------------------------------------------------------

    def save_state(self, session_id: str, branch_id: str, state: Any) -> str:
        sid = _new_id("st_")
        if hasattr(state, "__dataclass_fields__"):
            serialized = json.dumps(asdict(state), default=str)
        elif isinstance(state, dict):
            serialized = json.dumps(state, default=str)
        else:
            serialized = json.dumps(str(state))
        with self._tx() as c:
            c.execute(
                """INSERT INTO frontier_states
                   (state_id, session_id, branch_id, serialized_state, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (sid, session_id, branch_id, serialized, _now()),
            )
        self.emit("state_hydrated", {"state_id": sid}, branch_id=branch_id)
        return sid

    def load_latest_state(self, branch_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            """SELECT serialized_state FROM frontier_states
               WHERE branch_id = ? ORDER BY created_at DESC LIMIT 1""",
            (branch_id,),
        ).fetchone()
        return json.loads(row["serialized_state"]) if row else None

    # ------------------------------------------------------------------
    # Memory records
    # ------------------------------------------------------------------

    def add_memory(
        self,
        branch_id: str,
        memory_class: str,
        content: dict[str, Any],
    ) -> str:
        rid = _new_id("mem_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO memory_records
                   (record_id, class, branch_id, content, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (rid, memory_class, branch_id, json.dumps(content, default=str), _now()),
            )
        return rid

    def get_memories(
        self,
        branch_id: str,
        memory_class: str,
        exclude_contradictory: bool = True,
    ) -> list[dict[str, Any]]:
        q = "SELECT * FROM memory_records WHERE branch_id = ? AND class = ?"
        params: list[Any] = [branch_id, memory_class]
        if exclude_contradictory:
            q += " AND contradictory = 0"
        q += " ORDER BY created_at"
        rows = self._conn.execute(q, params).fetchall()
        return [dict(r) for r in rows]

    def increment_memory_use(self, record_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE memory_records SET used_count = used_count + 1 WHERE record_id = ?",
                (record_id,),
            )

    def mark_contradictory(self, record_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE memory_records SET contradictory = 1 WHERE record_id = ?",
                (record_id,),
            )

    # ------------------------------------------------------------------
    # Critic findings
    # ------------------------------------------------------------------

    def add_finding(
        self,
        branch_id: str,
        critic_name: str,
        code: str,
        severity: str,
        blocking: bool,
        subject_ids: list[str],
        message: str,
        suggested_next_move: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> str:
        fid = _new_id("find_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO critic_findings
                   (finding_id, critic_name, code, severity, blocking,
                    subject_ids, message, suggested_next_move, evidence_refs,
                    branch_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fid, critic_name, code, severity, int(blocking),
                    json.dumps(subject_ids), message, suggested_next_move,
                    json.dumps(evidence_refs or []), branch_id, _now(),
                ),
            )
        self.emit(
            "critic_finding_issued",
            {"finding_id": fid, "code": code, "blocking": blocking},
            branch_id=branch_id,
        )
        return fid

    def resolve_finding(self, finding_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE critic_findings SET resolved = 1 WHERE finding_id = ?",
                (finding_id,),
            )

    def get_blocking_findings(self, branch_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM critic_findings
               WHERE branch_id = ? AND blocking = 1 AND resolved = 0
               ORDER BY created_at""",
            (branch_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Action proposals
    # ------------------------------------------------------------------

    def add_proposal(
        self,
        branch_id: str,
        action_type: str,
        payload_ref: str,
        rationale: str,
        frame_id: str,
        expected_evidence_gain: float,
        expected_irreversibility: float,
        touched_constraints: list[str] | None = None,
        touched_anomalies: list[str] | None = None,
        fallback_path: str | None = None,
        proposal_id: str | None = None,
    ) -> str:
        pid = proposal_id or _new_id("prop_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO action_proposals
                   (proposal_id, action_type, payload_ref, rationale, frame_id,
                    expected_evidence_gain, expected_irreversibility,
                    touched_constraints, touched_anomalies, fallback_path,
                    branch_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pid, action_type, payload_ref, rationale, frame_id,
                    expected_evidence_gain, expected_irreversibility,
                    json.dumps(touched_constraints or []),
                    json.dumps(touched_anomalies or []),
                    fallback_path, branch_id, _now(),
                ),
            )
        self.emit("proposal_created", {"proposal_id": pid, "action_type": action_type}, branch_id=branch_id)
        return pid

    def commit_proposal(self, proposal_id: str, branch_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE action_proposals SET status = 'committed' WHERE proposal_id = ?",
                (proposal_id,),
            )
        self.emit("commitment_made", {"proposal_id": proposal_id}, branch_id=branch_id)

    def block_proposal(self, proposal_id: str, branch_id: str, reason: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE action_proposals SET status = 'blocked' WHERE proposal_id = ?",
                (proposal_id,),
            )
        self.emit("proposal_blocked", {"proposal_id": proposal_id, "reason": reason}, branch_id=branch_id)

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    def add_evidence(
        self,
        branch_id: str,
        description: str,
        confidence: float,
        source_ref: str | None = None,
    ) -> str:
        eid = _new_id("ev_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO evidence_records
                   (evidence_id, description, source_ref, confidence, branch_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (eid, description, source_ref, confidence, branch_id, _now()),
            )
        self.emit("evidence_promoted", {"evidence_id": eid}, branch_id=branch_id)
        return eid

    # ------------------------------------------------------------------
    # Anomalies
    # ------------------------------------------------------------------

    def add_anomaly(self, branch_id: str, description: str) -> str:
        aid = _new_id("anom_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO anomalies (anomaly_id, description, branch_id, created_at)
                   VALUES (?, ?, ?, ?)""",
                (aid, description, branch_id, _now()),
            )
        self.emit("anomaly_registered", {"anomaly_id": aid}, branch_id=branch_id)
        return aid

    def resolve_anomaly(self, anomaly_id: str) -> None:
        with self._tx() as c:
            c.execute(
                "UPDATE anomalies SET status = 'resolved' WHERE anomaly_id = ?",
                (anomaly_id,),
            )

    def get_open_anomalies(self, branch_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM anomalies WHERE branch_id = ? AND status = 'open'",
            (branch_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Gaps
    # ------------------------------------------------------------------

    def add_gap(
        self,
        branch_id: str,
        gap_type: str,
        issue_level: str,
        loop_stage: str,
        mode: str,
        missed_cue: str,
        observed_behavior: str,
        better_behavior: str,
        recurrence_risk: float,
        frame_id: str | None = None,
        pressure_snapshot: dict[str, float] | None = None,
        proposed_support: str | None = None,
    ) -> str:
        gid = _new_id("gap_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO gaps
                   (gap_id, gap_type, issue_level, loop_stage, mode, frame_id,
                    pressure_snapshot, missed_cue, observed_behavior, better_behavior,
                    proposed_support, recurrence_risk, branch_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    gid, gap_type, issue_level, loop_stage, mode, frame_id,
                    json.dumps(pressure_snapshot or {}),
                    missed_cue, observed_behavior, better_behavior,
                    proposed_support, recurrence_risk, branch_id, _now(),
                ),
            )
        self.emit("gap_recorded", {"gap_id": gid, "recurrence_risk": recurrence_risk}, branch_id=branch_id)
        return gid

    def get_high_recurrence_gaps(self, threshold: float = 0.6) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM gaps WHERE recurrence_risk >= ? ORDER BY recurrence_risk DESC",
            (threshold,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def emit(
        self,
        event_type: str,
        payload: dict[str, Any],
        branch_id: str | None = None,
    ) -> str:
        eid = _new_id("evt_")
        with self._tx() as c:
            c.execute(
                """INSERT INTO events (event_id, event_type, payload, branch_id, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (eid, event_type, json.dumps(payload, default=str), branch_id, _now()),
            )
        return eid

    def get_events(
        self,
        branch_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        if branch_id and event_type:
            rows = self._conn.execute(
                "SELECT * FROM events WHERE branch_id = ? AND event_type = ? ORDER BY created_at",
                (branch_id, event_type),
            ).fetchall()
        elif branch_id:
            rows = self._conn.execute(
                "SELECT * FROM events WHERE branch_id = ? ORDER BY created_at",
                (branch_id,),
            ).fetchall()
        elif event_type:
            rows = self._conn.execute(
                "SELECT * FROM events WHERE event_type = ? ORDER BY created_at",
                (event_type,),
            ).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM events ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]
