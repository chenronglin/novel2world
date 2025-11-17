from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from .models import Chapter, TerminologyEntry
from .storage import SqliteStorage


@dataclass(slots=True)
class ChapterContext:
    project_id: str
    chapter_id: str
    chapter: Chapter
    normalized_content: str
    terminology_map: Dict[str, str]
    terminology_entries: List[TerminologyEntry]
    previous_summaries: List[Tuple[str, str]]


def load_chapter_context(
    storage: SqliteStorage,
    project_id: str,
    chapter_id: str,
    *,
    history_limit: int = 3,
) -> ChapterContext:
    chapter = storage.get_chapter(project_id, chapter_id)
    if chapter is None:
        raise ValueError(f"未找到章节：project_id={project_id}, chapter_id={chapter_id}")

    terminology_entries = _select_terminology_entries(
        storage.list_terminology(project_id),
        chapter.terminology_keys,
    )
    terminology_map = build_terminology_map(terminology_entries)
    normalized_content = apply_terminology_replacements(chapter.content, terminology_entries)
    previous_summaries = collect_previous_summaries(
        storage.list_chapters(project_id),
        chapter_id,
        history_limit,
    )

    return ChapterContext(
        project_id=project_id,
        chapter_id=chapter_id,
        chapter=chapter,
        normalized_content=normalized_content,
        terminology_map=terminology_map,
        terminology_entries=terminology_entries,
        previous_summaries=previous_summaries,
    )


def build_terminology_map(entries: Sequence[TerminologyEntry]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for entry in entries:
        translation = entry.approved_translation
        for term in _iter_source_terms(entry):
            normalized = term.strip()
            if not normalized:
                continue
            mapping[normalized] = translation
    return mapping


def apply_terminology_replacements(text: str, entries: Sequence[TerminologyEntry]) -> str:
    if not text or not entries:
        return text
    # 为避免较长术语被短术语抢先替换，先按长度倒序处理
    replacements: List[Tuple[str, str]] = []
    for entry in entries:
        translation = entry.approved_translation
        for term in _iter_source_terms(entry):
            replacements.append((term, translation))
    replacements.sort(key=lambda item: len(item[0]), reverse=True)

    normalized_text = text
    for source_term, translation in replacements:
        if not source_term:
            continue
        normalized_text = normalized_text.replace(source_term, translation)
    return normalized_text


def collect_previous_summaries(
    chapters: Sequence[Chapter],
    target_chapter_id: str,
    history_limit: int,
) -> List[Tuple[str, str]]:
    summaries: List[Tuple[str, str]] = []
    chapter_ids = [chapter.chapter_id for chapter in chapters]
    try:
        current_index = chapter_ids.index(target_chapter_id)
    except ValueError as exc:
        raise ValueError(f"章节列表中缺少目标章节：{target_chapter_id}") from exc

    start_index = max(0, current_index - history_limit)
    for chapter in chapters[start_index:current_index]:
        summaries.append((chapter.chapter_id, chapter.summary))
    return summaries


def _select_terminology_entries(
    entries: Iterable[TerminologyEntry],
    required_ids: Sequence[str],
) -> List[TerminologyEntry]:
    if not required_ids:
        return list(entries)
    required_set = set(required_ids)
    selected: List[TerminologyEntry] = []
    for entry in entries:
        if entry.entry_id in required_set or entry.source_term in required_set:
            selected.append(entry)
    return selected


def _iter_source_terms(entry: TerminologyEntry) -> Iterable[str]:
    yield entry.source_term
    for variant in entry.variants:
        yield variant
