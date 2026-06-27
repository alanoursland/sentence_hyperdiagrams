"""Parse and write Parts of Thought diagram files.

A diagram file annotates a sentence with labels, one token per line.
See planning/diagram_format.md for the full specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Label:
    """A single label attached to a token.

    A leaf label has only a name. A linking label also specifies
    child_prev, child_curr, and index_prev to connect labels across
    tokens.
    """

    name: str
    child_prev: str | None = None
    child_curr: str | None = None
    index_prev: int | None = None
    parameter: int = 0
    weight: float = 1.0

    @property
    def is_leaf(self) -> bool:
        return self.child_prev is None

    def to_line(self) -> str:
        """Serialize to a diagram label line (without leading indent)."""
        if self.is_leaf:
            return self.name

        parts = [self.name, self.child_prev, self.child_curr,
                 str(self.index_prev)]

        if self.weight != 1.0:
            parts.append(str(self.parameter))
            parts.append(str(self.weight))
        elif self.parameter != 0:
            parts.append(str(self.parameter))

        return " ".join(parts)


@dataclass
class TokenAnnotation:
    """A token and its attached labels."""

    index: int
    token: str
    labels: list[Label] = field(default_factory=list)


def _parse_label(line: str) -> Label:
    """Parse a single label from a stripped, non-empty line."""
    parts = line.split()

    if len(parts) == 1:
        return Label(name=parts[0])

    if len(parts) < 4:
        raise ValueError(
            f"Label must have 1 field (leaf) or >= 4 fields (linking), "
            f"got {len(parts)}: {line!r}"
        )

    name = parts[0]
    child_prev = parts[1]
    child_curr = parts[2]
    index_prev = int(parts[3])
    parameter = int(parts[4]) if len(parts) > 4 else 0
    weight = float(parts[5]) if len(parts) > 5 else 1.0

    return Label(
        name=name,
        child_prev=child_prev,
        child_curr=child_curr,
        index_prev=index_prev,
        parameter=parameter,
        weight=weight,
    )


def _parse_token_line(line: str) -> tuple[int, str]:
    """Parse a token line like '3 on' into (index, token)."""
    parts = line.split(None, 1)
    if len(parts) != 2:
        raise ValueError(f"Token line must be '<index> <token>', got: {line!r}")
    return int(parts[0]), parts[1]


def parse_metadata(text: str) -> dict[str, str]:
    """Extract key-value metadata from comment lines.

    Metadata lines have the form: # key: value
    """
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") and ":" in line:
            content = line[1:].strip()
            key, _, value = content.partition(":")
            key = key.strip()
            value = value.strip()
            if key and value:
                metadata[key] = value
    return metadata


def parse_pass(text: str) -> list[TokenAnnotation]:
    """Parse a diagram pass file (or string) into token annotations.

    Returns a list of TokenAnnotation, one per token in the file.
    Tokens with no labels in this pass have an empty labels list.
    """
    annotations: list[TokenAnnotation] = []
    current: TokenAnnotation | None = None

    for raw_line in text.splitlines():
        # Skip blank lines and comments.
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Indented line = label on current token.
        if raw_line[0] in (" ", "\t"):
            if current is None:
                raise ValueError(
                    f"Label line before any token: {raw_line!r}"
                )
            current.labels.append(_parse_label(stripped))
        else:
            # Unindented line = new token.
            index, token = _parse_token_line(stripped)
            current = TokenAnnotation(index=index, token=token)
            annotations.append(current)

    return annotations


def parse_pass_file(path: str | Path) -> list[TokenAnnotation]:
    """Parse a diagram pass file from disk."""
    return parse_pass(Path(path).read_text(encoding="utf-8"))


def parse_tokens(text: str) -> list[TokenAnnotation]:
    """Parse a tokens-only file (no labels) into token annotations."""
    return parse_pass(text)


def parse_tokens_file(path: str | Path) -> list[TokenAnnotation]:
    """Parse a tokens-only file from disk."""
    return parse_tokens(Path(path).read_text(encoding="utf-8"))


def write_pass(annotations: list[TokenAnnotation],
               metadata: dict[str, str] | None = None) -> str:
    """Serialize token annotations to diagram format."""
    lines: list[str] = []

    if metadata:
        for key, value in metadata.items():
            lines.append(f"# {key}: {value}")
        lines.append("")

    for ann in annotations:
        lines.append(f"{ann.index} {ann.token}")
        for label in ann.labels:
            lines.append(f"  {label.to_line()}")

    # Trailing newline.
    lines.append("")
    return "\n".join(lines)


def write_pass_file(path: str | Path,
                    annotations: list[TokenAnnotation],
                    metadata: dict[str, str] | None = None) -> None:
    """Write token annotations to a diagram file on disk."""
    Path(path).write_text(
        write_pass(annotations, metadata), encoding="utf-8"
    )


def write_tokens(annotations: list[TokenAnnotation]) -> str:
    """Serialize just the tokens (no labels) to tokens.txt format."""
    lines = [f"{ann.index} {ann.token}" for ann in annotations]
    lines.append("")
    return "\n".join(lines)


def write_tokens_file(path: str | Path,
                      annotations: list[TokenAnnotation]) -> None:
    """Write a tokens-only file to disk."""
    Path(path).write_text(
        write_tokens(annotations), encoding="utf-8"
    )


def merge_passes(passes: list[list[TokenAnnotation]]) -> list[TokenAnnotation]:
    """Merge multiple annotation passes into a single annotation list.

    All passes must have the same tokens in the same order. Labels from
    all passes are combined on each token.
    """
    if not passes:
        return []

    base = passes[0]
    for pass_annotations in passes[1:]:
        if len(pass_annotations) != len(base):
            raise ValueError(
                f"Pass has {len(pass_annotations)} tokens, "
                f"expected {len(base)}"
            )
        for base_ann, pass_ann in zip(base, pass_annotations):
            if base_ann.index != pass_ann.index:
                raise ValueError(
                    f"Token index mismatch: {base_ann.index} vs "
                    f"{pass_ann.index}"
                )
            if base_ann.token != pass_ann.token:
                raise ValueError(
                    f"Token mismatch at index {base_ann.index}: "
                    f"{base_ann.token!r} vs {pass_ann.token!r}"
                )

    merged: list[TokenAnnotation] = []
    for i, base_ann in enumerate(base):
        all_labels: list[Label] = []
        for pass_annotations in passes:
            all_labels.extend(pass_annotations[i].labels)
        merged.append(TokenAnnotation(
            index=base_ann.index,
            token=base_ann.token,
            labels=all_labels,
        ))

    return merged
