from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from .models import (
    Chapter,
    Project,
    TerminologyEntry,
    TranslationResult,
    TranslationStage,
    utc_now,
)


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"


def _ensure_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return _ensure_timezone(dt).isoformat()


def _from_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _json_dump(data) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _json_load(data: Optional[str], default):
    if data is None:
        return default
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return default


class SqliteStorage:
    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._ensure_schema()

    def __enter__(self) -> "SqliteStorage":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    def _ensure_schema(self) -> None:
        cursor = self._conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                metadata TEXT
            );

            CREATE TABLE IF NOT EXISTS chapters (
                project_id TEXT NOT NULL,
                chapter_id TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT DEFAULT '',
                content TEXT NOT NULL,
                characters TEXT,
                terminology_keys TEXT,
                metadata TEXT,
                PRIMARY KEY (project_id, chapter_id),
                FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS terminology_entries (
                entry_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                source_term TEXT NOT NULL,
                approved_translation TEXT NOT NULL,
                variants TEXT,
                part_of_speech TEXT,
                notes TEXT,
                metadata TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS translation_results (
                project_id TEXT NOT NULL,
                chapter_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                content TEXT NOT NULL,
                validation TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (project_id, chapter_id, stage),
                FOREIGN KEY (project_id, chapter_id)
                    REFERENCES chapters(project_id, chapter_id) ON DELETE CASCADE
            );
            """
        )
        self._conn.commit()

    # Projects
    def upsert_project(self, project: Project) -> None:
        self._conn.execute(
            """
            INSERT INTO projects (project_id, name, description, source_language, target_language, metadata)
            VALUES (:project_id, :name, :description, :source_language, :target_language, :metadata)
            ON CONFLICT(project_id) DO UPDATE SET
                name=excluded.name,
                description=excluded.description,
                source_language=excluded.source_language,
                target_language=excluded.target_language,
                metadata=excluded.metadata
            """,
            {
                "project_id": project.project_id,
                "name": project.name,
                "description": project.description,
                "source_language": project.source_language,
                "target_language": project.target_language,
                "metadata": _json_dump(project.metadata),
            },
        )
        self._conn.commit()

    def get_project(self, project_id: str) -> Optional[Project]:
        row = self._conn.execute(
            "SELECT * FROM projects WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if not row:
            return None
        return Project(
            project_id=row["project_id"],
            name=row["name"],
            description=row["description"],
            source_language=row["source_language"],
            target_language=row["target_language"],
            metadata=_json_load(row["metadata"], {}),
        )

    def list_projects(self) -> List[Project]:
        rows = self._conn.execute("SELECT * FROM projects ORDER BY project_id").fetchall()
        return [
            Project(
                project_id=row["project_id"],
                name=row["name"],
                description=row["description"],
                source_language=row["source_language"],
                target_language=row["target_language"],
                metadata=_json_load(row["metadata"], {}),
            )
            for row in rows
        ]

    # Chapters
    def upsert_chapter(self, chapter: Chapter) -> None:
        self._conn.execute(
            """
            INSERT INTO chapters (
                project_id, chapter_id, title, summary, content,
                characters, terminology_keys, metadata
            ) VALUES (
                :project_id, :chapter_id, :title, :summary, :content,
                :characters, :terminology_keys, :metadata
            ) ON CONFLICT(project_id, chapter_id) DO UPDATE SET
                title=excluded.title,
                summary=excluded.summary,
                content=excluded.content,
                characters=excluded.characters,
                terminology_keys=excluded.terminology_keys,
                metadata=excluded.metadata
            """,
            {
                "project_id": chapter.project_id,
                "chapter_id": chapter.chapter_id,
                "title": chapter.title,
                "summary": chapter.summary,
                "content": chapter.content,
                "characters": _json_dump(chapter.characters),
                "terminology_keys": _json_dump(chapter.terminology_keys),
                "metadata": _json_dump(chapter.metadata),
            },
        )
        self._conn.commit()

    def get_chapter(self, project_id: str, chapter_id: str) -> Optional[Chapter]:
        row = self._conn.execute(
            """
            SELECT * FROM chapters
            WHERE project_id = ? AND chapter_id = ?
            """,
            (project_id, chapter_id),
        ).fetchone()
        if not row:
            return None
        return Chapter(
            project_id=row["project_id"],
            chapter_id=row["chapter_id"],
            title=row["title"],
            summary=row["summary"],
            content=row["content"],
            characters=_json_load(row["characters"], []),
            terminology_keys=_json_load(row["terminology_keys"], []),
            metadata=_json_load(row["metadata"], {}),
        )

    def list_chapters(self, project_id: str) -> List[Chapter]:
        rows = self._conn.execute(
            "SELECT * FROM chapters WHERE project_id = ? ORDER BY chapter_id",
            (project_id,),
        ).fetchall()
        return [
            Chapter(
                project_id=row["project_id"],
                chapter_id=row["chapter_id"],
                title=row["title"],
                summary=row["summary"],
                content=row["content"],
                characters=_json_load(row["characters"], []),
                terminology_keys=_json_load(row["terminology_keys"], []),
                metadata=_json_load(row["metadata"], {}),
            )
            for row in rows
        ]

    # Terminology
    def upsert_terminology_entry(self, entry: TerminologyEntry) -> None:
        self._conn.execute(
            """
            INSERT INTO terminology_entries (
                entry_id, project_id, source_term, approved_translation,
                variants, part_of_speech, notes, metadata
            ) VALUES (
                :entry_id, :project_id, :source_term, :approved_translation,
                :variants, :part_of_speech, :notes, :metadata
            ) ON CONFLICT(entry_id) DO UPDATE SET
                project_id=excluded.project_id,
                source_term=excluded.source_term,
                approved_translation=excluded.approved_translation,
                variants=excluded.variants,
                part_of_speech=excluded.part_of_speech,
                notes=excluded.notes,
                metadata=excluded.metadata
            """,
            {
                "entry_id": entry.entry_id,
                "project_id": entry.project_id,
                "source_term": entry.source_term,
                "approved_translation": entry.approved_translation,
                "variants": _json_dump(entry.variants),
                "part_of_speech": entry.part_of_speech,
                "notes": entry.notes,
                "metadata": _json_dump(entry.metadata),
            },
        )
        self._conn.commit()

    def list_terminology(self, project_id: str) -> List[TerminologyEntry]:
        rows = self._conn.execute(
            """
            SELECT * FROM terminology_entries
            WHERE project_id = ?
            ORDER BY source_term
            """,
            (project_id,),
        ).fetchall()
        return [
            TerminologyEntry(
                entry_id=row["entry_id"],
                project_id=row["project_id"],
                source_term=row["source_term"],
                approved_translation=row["approved_translation"],
                variants=_json_load(row["variants"], []),
                part_of_speech=row["part_of_speech"],
                notes=row["notes"],
                metadata=_json_load(row["metadata"], {}),
            )
            for row in rows
        ]

    # Translation results
    def upsert_translation_result(self, result: TranslationResult) -> None:
        now_iso = _to_iso(utc_now())
        created_iso = _to_iso(result.created_at)
        self._conn.execute(
            """
            INSERT INTO translation_results (
                project_id, chapter_id, stage, content,
                validation, metadata, created_at, updated_at
            ) VALUES (
                :project_id, :chapter_id, :stage, :content,
                :validation, :metadata, :created_at, :updated_at
            ) ON CONFLICT(project_id, chapter_id, stage) DO UPDATE SET
                content=excluded.content,
                validation=excluded.validation,
                metadata=excluded.metadata,
                updated_at=excluded.updated_at
            """,
            {
                "project_id": result.project_id,
                "chapter_id": result.chapter_id,
                "stage": result.stage.value,
                "content": result.content,
                "validation": _json_dump(result.validation),
                "metadata": _json_dump(result.metadata),
                "created_at": created_iso,
                "updated_at": now_iso,
            },
        )
        self._conn.commit()

    def list_translation_results(self, project_id: str, chapter_id: str) -> List[TranslationResult]:
        rows = self._conn.execute(
            """
            SELECT * FROM translation_results
            WHERE project_id = ? AND chapter_id = ?
            ORDER BY created_at
            """,
            (project_id, chapter_id),
        ).fetchall()
        return [self._row_to_translation_result(row) for row in rows]

    def get_translation_result(
        self,
        project_id: str,
        chapter_id: str,
        stage: TranslationStage | str,
    ) -> Optional[TranslationResult]:
        stage_value = stage.value if isinstance(stage, TranslationStage) else stage
        row = self._conn.execute(
            """
            SELECT * FROM translation_results
            WHERE project_id = ? AND chapter_id = ? AND stage = ?
            """,
            (project_id, chapter_id, stage_value),
        ).fetchone()
        if not row:
            return None
        return self._row_to_translation_result(row)

    def delete_translation_results(self, project_id: str, chapter_id: str) -> None:
        self._conn.execute(
            "DELETE FROM translation_results WHERE project_id = ? AND chapter_id = ?",
            (project_id, chapter_id),
        )
        self._conn.commit()

    def _row_to_translation_result(self, row: sqlite3.Row) -> TranslationResult:
        created_at = _from_iso(row["created_at"]) or utc_now()
        updated_at = _from_iso(row["updated_at"]) or created_at
        return TranslationResult(
            project_id=row["project_id"],
            chapter_id=row["chapter_id"],
            stage=TranslationStage(row["stage"]),
            content=row["content"],
            validation=_json_load(row["validation"], {}),
            metadata=_json_load(row["metadata"], {}),
            created_at=created_at,
            updated_at=updated_at,
        )

    # Utilities
    def attach_projects(self, projects: Iterable[Project]) -> None:
        for project in projects:
            self.upsert_project(project)

    def attach_chapters(self, chapters: Iterable[Chapter]) -> None:
        for chapter in chapters:
            self.upsert_chapter(chapter)

    def attach_terminology(self, entries: Iterable[TerminologyEntry]) -> None:
        for entry in entries:
            self.upsert_terminology_entry(entry)
