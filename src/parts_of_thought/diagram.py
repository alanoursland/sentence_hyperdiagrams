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
    child_curr, child_prev, and index_prev to connect labels across
    tokens. In the serialized file format, child_curr is written first
    because it is the label on the token where this label is attached.
    """

    name: str
    child_curr: str | None = None
    child_prev: str | None = None
    index_prev: int | None = None
    parameter: int = 0
    weight: float = 1.0

    @property
    def is_leaf(self) -> bool:
        return self.child_prev is None

    def to_line(self) -> str:
        """Serialize to a diagram label line (without leading indent)."""
        if self.is_leaf:
            if self.weight != 1.0:
                return f"{self.name} {self.weight}"
            return self.name

        parts = [self.name, self.child_curr, self.child_prev,
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

    if len(parts) == 2:
        # Weighted leaf label: NAME WEIGHT
        try:
            weight = float(parts[1])
            return Label(name=parts[0], weight=weight)
        except ValueError:
            pass
        raise ValueError(
            f"Label with 2 fields must be a weighted leaf (NAME WEIGHT), "
            f"got: {line!r}"
        )

    if len(parts) == 3:
        raise ValueError(
            f"Label must have 1 field (leaf), 2 fields (weighted leaf), "
            f"or >= 4 fields (linking), got {len(parts)}: {line!r}"
        )

    name = parts[0]
    child_curr = parts[1]
    child_prev = parts[2]
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


_PUNCT = set('.,!?;:()[]{}"\u2014')


def tokenize(text: str, start_index: int = 0) -> list[TokenAnnotation]:
    """Tokenize raw text into indexed tokens for annotation.

    Splits on whitespace and separates leading/trailing punctuation
    into its own tokens.  Hyphens and apostrophes are kept as part
    of the word (contractions, compound words).
    """
    tokens: list[TokenAnnotation] = []
    index = start_index

    for word in text.split():
        # Peel off leading punctuation.
        while word and word[0] in _PUNCT:
            tokens.append(TokenAnnotation(index=index, token=word[0]))
            index += 1
            word = word[1:]

        # Collect trailing punctuation.
        trailing: list[str] = []
        while word and word[-1] in _PUNCT:
            trailing.append(word[-1])
            word = word[:-1]

        # The word itself.
        if word:
            tokens.append(TokenAnnotation(index=index, token=word))
            index += 1

        # Trailing punctuation in original order.
        for ch in reversed(trailing):
            tokens.append(TokenAnnotation(index=index, token=ch))
            index += 1

    return tokens


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


class ValidationError(Exception):
    """Raised when a diagram fails validation."""


def validate(annotations: list[TokenAnnotation]) -> list[str]:
    """Validate label references across all tokens.

    Checks that every linking label's children actually exist:
    - index_prev must be strictly less than the current token index
    - child_curr must be a label name on the current token
    - child_prev must be a label name on the token at index_prev
    - index_prev must reference a valid token index

    Returns a list of error messages. Empty list means valid.
    """
    errors: list[str] = []

    # Build index: token_index -> set of label names on that token.
    token_by_index: dict[int, TokenAnnotation] = {}
    for ann in annotations:
        token_by_index[ann.index] = ann

    for ann in annotations:
        label_names_here = {l.name for l in ann.labels}

        for label in ann.labels:
            if label.is_leaf:
                continue

            # index_prev must be strictly less than current token index.
            if label.index_prev >= ann.index:
                errors.append(
                    f"Token {ann.index} ({ann.token!r}): label "
                    f"{label.name} has index_prev {label.index_prev} "
                    f"which is not less than the current token index"
                )
                continue

            # child_curr must be on the current token.
            if label.child_curr not in label_names_here:
                errors.append(
                    f"Token {ann.index} ({ann.token!r}): label "
                    f"{label.name} references child_curr "
                    f"{label.child_curr!r} which is not a label on "
                    f"this token. Labels here: "
                    f"{sorted(label_names_here)}"
                )

            # index_prev must be a valid token.
            if label.index_prev not in token_by_index:
                errors.append(
                    f"Token {ann.index} ({ann.token!r}): label "
                    f"{label.name} references index_prev "
                    f"{label.index_prev} which is not a valid token "
                    f"index"
                )
            else:
                # child_prev must be on the token at index_prev.
                prev_ann = token_by_index[label.index_prev]
                prev_label_names = {l.name for l in prev_ann.labels}
                if label.child_prev not in prev_label_names:
                    errors.append(
                        f"Token {ann.index} ({ann.token!r}): label "
                        f"{label.name} references child_prev "
                        f"{label.child_prev!r} at index "
                        f"{label.index_prev} ({prev_ann.token!r}), "
                        f"but that token's labels are: "
                        f"{sorted(prev_label_names)}"
                    )

    return errors


def validate_or_raise(annotations: list[TokenAnnotation]) -> None:
    """Validate and raise ValidationError if any errors found."""
    errors = validate(annotations)
    if errors:
        msg = f"{len(errors)} validation error(s):\n"
        msg += "\n".join(f"  - {e}" for e in errors)
        raise ValidationError(msg)


def fix_label_placement(annotations: list[TokenAnnotation]) -> list[TokenAnnotation]:
    """Relocate linking labels to the token of their most recent child.

    For each linking label, finds where its two children actually live,
    then places the label on the higher-indexed child's token.  That
    child becomes child_curr; the other becomes child_prev with its
    token index as index_prev.

    Iterates until all labels are stable.
    """
    # Deep copy into mutable structure.
    by_index: dict[int, TokenAnnotation] = {}
    for ann in annotations:
        by_index[ann.index] = TokenAnnotation(
            index=ann.index, token=ann.token, labels=list(ann.labels),
        )

    changed = True
    while changed:
        changed = False

        # Build label_name -> sorted list of token indices.
        name_to_indices: dict[str, list[int]] = {}
        for ann in by_index.values():
            for label in ann.labels:
                name_to_indices.setdefault(label.name, []).append(ann.index)
        for v in name_to_indices.values():
            v.sort()

        for ann_idx in sorted(by_index.keys()):
            ann = by_index[ann_idx]
            for label in list(ann.labels):
                if label.is_leaf:
                    continue

                # child_prev lives at index_prev.
                prev_token_idx = label.index_prev

                # Find child_curr: nearest occurrence after index_prev.
                candidates = name_to_indices.get(label.child_curr, [])
                curr_token_idx = None
                for idx in candidates:
                    if idx > prev_token_idx:
                        curr_token_idx = idx
                        break

                if curr_token_idx is None:
                    continue

                # Label goes on the most recent child's token.
                target_idx = max(prev_token_idx, curr_token_idx)

                # Determine which child is on the target token.
                if curr_token_idx == target_idx:
                    new_child_curr = label.child_curr
                    new_child_prev = label.child_prev
                    new_index_prev = prev_token_idx
                else:
                    new_child_curr = label.child_prev
                    new_child_prev = label.child_curr
                    new_index_prev = curr_token_idx

                needs_fix = (target_idx != ann_idx
                             or new_child_curr != label.child_curr
                             or new_index_prev != label.index_prev)

                if needs_fix:
                    new_label = Label(
                        name=label.name,
                        child_prev=new_child_prev,
                        child_curr=new_child_curr,
                        index_prev=new_index_prev,
                        parameter=label.parameter,
                        weight=label.weight,
                    )
                    ann.labels.remove(label)
                    by_index[target_idx].labels.append(new_label)
                    changed = True
                    break

            if changed:
                break

    return [by_index[idx] for idx in sorted(by_index.keys())]


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
