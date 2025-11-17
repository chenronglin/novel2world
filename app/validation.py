from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore

from .models import TerminologyEntry
from .prompt_loader import load_prompt_json


@dataclass(slots=True)
class TermConsistencyIssue:
    entry_id: str
    source_term: str
    approved_translation: str
    required_count: int
    translated_count: int
    variants: List[str]


@dataclass(slots=True)
class ConsistencyReport:
    terminology_ok: bool
    terminology_issues: List[TermConsistencyIssue]
    judge_decision: Optional[str]

    @property
    def overall_ok(self) -> bool:
        if not self.terminology_ok:
            return False
        if self.judge_decision is None:
            return True
        return self.judge_decision.upper() == "YES"


def validate_terminology_counts(
    source_text: str,
    translated_text: str,
    entries: Sequence[TerminologyEntry],
) -> ConsistencyReport:
    issues: List[TermConsistencyIssue] = []
    for entry in entries:
        source_terms = [entry.source_term, *entry.variants]
        required_count = _count_any(source_text, source_terms)
        translated_count = translated_text.count(entry.approved_translation)
        if required_count > translated_count:
            issues.append(
                TermConsistencyIssue(
                    entry_id=entry.entry_id,
                    source_term=entry.source_term,
                    approved_translation=entry.approved_translation,
                    required_count=required_count,
                    translated_count=translated_count,
                    variants=list(entry.variants),
                )
            )
    return ConsistencyReport(
        terminology_ok=not issues,
        terminology_issues=issues,
        judge_decision=None,
    )


class ConsistencyJudge:
    def __init__(
        self,
        *,
        model: str = "gpt-5-mini",
        client: Optional[OpenAI] = None,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if client is not None:
            self._client = client
        elif OpenAI is not None and api_key:
            self._client = OpenAI(api_key=api_key)
        else:
            self._client = None
        self.model = model
        self._prompt_config = load_prompt_json("judeg")

    def judge(
        self,
        source_text: str,
        translated_text: str,
        target_language: str = "English",
    ) -> str:
        if self._client is None:
            return "YES"

        system_prompt = self._prompt_config.get("description", "")
        instructions = "\n".join(self._prompt_config.get("instructions", []))
        user_content = _build_judge_prompt(
            source_text,
            translated_text,
            target_language,
        )
        response = self._client.chat.completions.create(
            model=self.model,
            temperature=0,
            max_tokens=4,
            messages=[
                {"role": "system", "content": system_prompt + "\n" + instructions},
                {"role": "user", "content": user_content},
            ],
        )
        decision = response.choices[0].message.content.strip().upper()
        return "YES" if decision == "YES" else "NO"


def evaluate_consistency(
    source_text: str,
    translated_text: str,
    entries: Sequence[TerminologyEntry],
    *,
    judge: Optional[ConsistencyJudge] = None,
    target_language: str = "English",
) -> ConsistencyReport:
    base_report = validate_terminology_counts(source_text, translated_text, entries)
    if judge is None:
        return base_report
    decision = judge.judge(source_text, translated_text, target_language)
    return ConsistencyReport(
        terminology_ok=base_report.terminology_ok,
        terminology_issues=base_report.terminology_issues,
        judge_decision=decision,
    )


def _build_judge_prompt(
    source_text: str,
    translated_text: str,
    target_language: str,
) -> str:
    template = load_prompt_json("judeg")
    expected_output = template.get("expected_output", "")
    return (
        f"目标语言：{target_language}\n"
        f"请根据指令判断译文是否合格，仅回复 'YES' 或 'NO'。\n"
        f"原文：\n{source_text}\n\n译文：\n{translated_text}\n\n输出要求：{expected_output}"
    )


def _count_any(text: str, patterns: Iterable[str]) -> int:
    counter = 0
    for pattern in patterns:
        if not pattern:
            continue
        counter += text.count(pattern)
    return counter
