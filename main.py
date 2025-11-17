from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.context import load_chapter_context
from app.storage import SqliteStorage
from app.translator import TranslationAgent
from app.validation import ConsistencyJudge, evaluate_consistency


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="novel-translation",
        description="AI辅助中文长篇小说英译命令行工具",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    translate_parser = subparsers.add_parser(
        "translate-chapter",
        help="翻译指定章节并输出一致性校验结果",
    )
    translate_parser.add_argument("--project", required=True, help="项目ID")
    translate_parser.add_argument("--chapter", required=True, help="章节ID")
    translate_parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="可选，自定义sqlite数据库路径",
    )
    translate_parser.add_argument(
        "--history",
        type=int,
        default=3,
        help="前置章节概要数量（默认3章）",
    )
    translate_parser.add_argument(
        "--novel-type",
        default=None,
        help="小说类型，用于提示词，如 werewolf",
    )
    translate_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="翻译结果保存路径（JSON）",
    )

    return parser


def handle_translate_chapter(args: argparse.Namespace) -> int:
    with SqliteStorage(args.db) as storage:
        context = load_chapter_context(
            storage,
            args.project,
            args.chapter,
            history_limit=args.history,
        )

        translator = TranslationAgent()
        translated_text = translator.translate(context, novel_type=args.novel_type)

        judge = ConsistencyJudge()
        report = evaluate_consistency(
            context.chapter.content,
            translated_text,
            context.terminology_entries,
            judge=judge,
        )

        payload = {
            "project_id": context.project_id,
            "chapter_id": context.chapter_id,
            "translated_text": translated_text,
            "terminology_ok": report.terminology_ok,
            "terminology_issues": [
                {
                    "entry_id": issue.entry_id,
                    "source_term": issue.source_term,
                    "approved_translation": issue.approved_translation,
                    "required_count": issue.required_count,
                    "translated_count": issue.translated_count,
                    "variants": issue.variants,
                }
                for issue in report.terminology_issues
            ],
            "judge_decision": report.judge_decision,
            "overall_ok": report.overall_ok,
        }

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))

        return 0 if report.overall_ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "translate-chapter":
        return handle_translate_chapter(args)

    parser.error("未知命令")
    return 2


if __name__ == "__main__":
    sys.exit(main())
