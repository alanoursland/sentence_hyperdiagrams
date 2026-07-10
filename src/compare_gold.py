"""Compare a generated annotation pass with a canonical gold pass."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from parts_of_thought.diagram import (
    Label,
    TokenAnnotation,
    merge_passes,
    parse_pass_file,
    validate,
)


@dataclass(frozen=True)
class LabelKey:
    """Structural label identity; confidence is deliberately excluded."""

    name: str
    child_curr: str | None
    child_prev: str | None
    index_prev: int | None
    parameter: int

    @classmethod
    def from_label(cls, label: Label) -> "LabelKey":
        return cls(
            name=label.name,
            child_curr=label.child_curr,
            child_prev=label.child_prev,
            index_prev=label.index_prev,
            parameter=label.parameter,
        )

    def to_line(self) -> str:
        return Label(
            name=self.name,
            child_curr=self.child_curr,
            child_prev=self.child_prev,
            index_prev=self.index_prev,
            parameter=self.parameter,
        ).to_line()


@dataclass(frozen=True)
class LabelDifference:
    index: int
    token: str
    label: LabelKey


@dataclass(frozen=True)
class ComparisonResult:
    gold_count: int
    generated_count: int
    matched_count: int
    missing: tuple[LabelDifference, ...]
    extra: tuple[LabelDifference, ...]
    invalid_references: tuple[str, ...]

    @property
    def precision(self) -> float:
        if self.generated_count == 0:
            return 1.0 if self.gold_count == 0 else 0.0
        return self.matched_count / self.generated_count

    @property
    def recall(self) -> float:
        if self.gold_count == 0:
            return 1.0
        return self.matched_count / self.gold_count


def _check_same_tokens(
    gold: list[TokenAnnotation],
    generated: list[TokenAnnotation],
) -> None:
    if len(gold) != len(generated):
        raise ValueError(
            f"Token count mismatch: gold has {len(gold)}, "
            f"generated has {len(generated)}"
        )
    for gold_ann, generated_ann in zip(gold, generated):
        if (gold_ann.index, gold_ann.token) != (
            generated_ann.index,
            generated_ann.token,
        ):
            raise ValueError(
                "Token mismatch: gold has "
                f"{gold_ann.index} {gold_ann.token!r}, generated has "
                f"{generated_ann.index} {generated_ann.token!r}"
            )


def _filtered_pass(
    annotations: Iterable[TokenAnnotation],
    min_weight: float,
) -> list[TokenAnnotation]:
    return [
        TokenAnnotation(
            index=ann.index,
            token=ann.token,
            labels=[label for label in ann.labels if label.weight >= min_weight],
        )
        for ann in annotations
    ]


def compare_annotations(
    gold: list[TokenAnnotation],
    generated: list[TokenAnnotation],
    *,
    context_passes: Iterable[list[TokenAnnotation]] = (),
    min_weight: float = 1.0,
) -> ComparisonResult:
    """Compare structural label identities and validate generated references."""
    if not 0.0 <= min_weight <= 1.0:
        raise ValueError("min_weight must be between 0.0 and 1.0")
    _check_same_tokens(gold, generated)

    filtered = _filtered_pass(generated, min_weight)
    missing: list[LabelDifference] = []
    extra: list[LabelDifference] = []
    matched_count = 0
    gold_count = 0
    generated_count = 0

    for gold_ann, generated_ann in zip(gold, filtered):
        gold_keys = {LabelKey.from_label(label) for label in gold_ann.labels}
        generated_keys = {
            LabelKey.from_label(label) for label in generated_ann.labels
        }
        gold_count += len(gold_keys)
        generated_count += len(generated_keys)
        matched_count += len(gold_keys & generated_keys)
        missing.extend(
            LabelDifference(gold_ann.index, gold_ann.token, key)
            for key in sorted(gold_keys - generated_keys, key=repr)
        )
        extra.extend(
            LabelDifference(gold_ann.index, gold_ann.token, key)
            for key in sorted(generated_keys - gold_keys, key=repr)
        )

    contexts = list(context_passes)
    combined = merge_passes([*contexts, filtered]) if contexts else filtered
    invalid_references = tuple(validate(combined))
    return ComparisonResult(
        gold_count=gold_count,
        generated_count=generated_count,
        matched_count=matched_count,
        missing=tuple(missing),
        extra=tuple(extra),
        invalid_references=invalid_references,
    )


def format_report(result: ComparisonResult, max_details: int = 50) -> str:
    """Render a concise human-readable comparison report."""
    lines = [
        f"Gold labels: {result.gold_count}",
        f"Generated labels: {result.generated_count}",
        f"Matched labels: {result.matched_count}",
        f"Precision: {result.precision:.3f}",
        f"Recall: {result.recall:.3f}",
        f"Missing labels: {len(result.missing)}",
    ]
    for item in result.missing[:max_details]:
        lines.append(f"  {item.index} {item.token}: {item.label.to_line()}")
    lines.append(f"Extra labels: {len(result.extra)}")
    for item in result.extra[:max_details]:
        lines.append(f"  {item.index} {item.token}: {item.label.to_line()}")
    lines.append(f"Invalid references: {len(result.invalid_references)}")
    for error in result.invalid_references[:max_details]:
        lines.append(f"  {error}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare a generated diagram pass with a gold pass."
    )
    parser.add_argument("--gold", required=True, help="Canonical gold pass")
    parser.add_argument("--generated", required=True, help="Generated pass")
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Supporting pass for reference validation; repeat as needed",
    )
    parser.add_argument(
        "--min-weight",
        type=float,
        default=1.0,
        help="Minimum generated-label confidence to score (default: 1.0)",
    )
    parser.add_argument("--max-details", type=int, default=50)
    args = parser.parse_args()

    result = compare_annotations(
        parse_pass_file(Path(args.gold)),
        parse_pass_file(Path(args.generated)),
        context_passes=[parse_pass_file(Path(path)) for path in args.context],
        min_weight=args.min_weight,
    )
    print(format_report(result, max_details=args.max_details))


if __name__ == "__main__":
    main()
