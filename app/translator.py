from __future__ import annotations

import os
from textwrap import dedent
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - library optional during local runs
    OpenAI = None  # type: ignore

from .context import ChapterContext
from .prompt_loader import load_prompt_json


class TranslationAgent:
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
        self._prompt_config = load_prompt_json("Chinese-to-English")

    def translate(
        self,
        context: ChapterContext,
        *,
        novel_type: Optional[str] = None,
    ) -> str:
        prompt = self._build_prompt(context, novel_type)
        if self._client is None:
            return _fallback_translate(context.normalized_content, context.terminology_map)

        messages = [
            {
                "role": "system",
                "content": self._render_system_prompt(novel_type),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()

    def _render_system_prompt(self, novel_type: Optional[str]) -> str:
        config = self._prompt_config
        novel_type = novel_type or config.get("dependencies", {}).get("type", "fiction")
        description = config.get("description", "").format(type=novel_type)
        instructions = config.get("instructions", [])
        rendered_instructions = "\n".join(
            f"- {instruction.format(type=novel_type)}" for instruction in instructions
        )
        expected_output = config.get("expected_output", "")
        return dedent(
            f"""
            {description}

            {rendered_instructions}

            输出要求：{expected_output}
            """
        ).strip()

    def _build_prompt(self, context: ChapterContext, novel_type: Optional[str]) -> str:
        terminology_lines = _format_terminology(context.terminology_entries)
        summaries_text = _format_summaries(context.previous_summaries)
        expected = self._prompt_config.get("expected_output", "")
        return dedent(
            f"""
            ## 任务说明
            请将以下章节内容翻译为自然流畅的美式英语小说文风，遵循系统指令并满足“{expected}”。

            ## 项目信息
            - 项目ID：{context.project_id}
            - 章节ID：{context.chapter_id}
            - 章节标题：{context.chapter.title}

            ## 历史章节概要
            {summaries_text}

            ## 术语表（必须遵守）
            {terminology_lines}

            ## 待翻译正文（术语已替换为核准译法）
            {context.normalized_content}
            """
        ).strip()


def _format_terminology(entries: Sequence) -> str:
    if not entries:
        return "(无)"
    lines: List[str] = []
    for entry in entries:
        variants = ", ".join(entry.variants) if entry.variants else "无"
        lines.append(
            f"- {entry.source_term} -> {entry.approved_translation} (别名：{variants})"
        )
    return "\n".join(lines)


def _format_summaries(summaries: Sequence[Tuple[str, str]]) -> str:
    if not summaries:
        return "(无)"
    return "\n".join(
        f"- 章节 {chapter_id}：{summary}" for chapter_id, summary in summaries
    )


def _fallback_translate(text: str, terminology_map: Dict[str, str]) -> str:
    if not text:
        return text
    replacements: List[Tuple[str, str]] = sorted(
        terminology_map.items(), key=lambda item: len(item[0]), reverse=True
    )
    translated = text
    for source_term, translation in replacements:
        if not source_term:
            continue
        translated = translated.replace(source_term, translation)
    return translated
