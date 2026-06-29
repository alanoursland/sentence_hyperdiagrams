"""Right-to-left pattern language for Parts of Thought annotations.

Patterns are parsed into a small AST and matched directly against
TokenAnnotation sequences.  This is deliberately not a full regular
expression engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from parts_of_thought.diagram import Label, TokenAnnotation


class PatternSyntaxError(ValueError):
    """Raised when a pattern string cannot be parsed."""


@dataclass(frozen=True)
class Span:
    """Inclusive token span covered by a label instance."""

    left: int
    right: int


@dataclass(frozen=True)
class LabelInstance:
    """A concrete label attached to a token."""

    label: Label
    token_index: int
    span: Span

    @property
    def name(self) -> str:
        return self.label.name


@dataclass(frozen=True)
class RegexElement:
    """Base class for pattern AST nodes."""


@dataclass(frozen=True)
class TokenLiteral(RegexElement):
    value: str


@dataclass(frozen=True)
class LabelAtom(RegexElement):
    name: str


@dataclass(frozen=True)
class SentinelAtom(RegexElement):
    name: str


@dataclass(frozen=True)
class Sequence(RegexElement):
    elements: tuple[RegexElement, ...]


@dataclass(frozen=True)
class Group(RegexElement):
    element: RegexElement


@dataclass(frozen=True)
class Union(RegexElement):
    alternatives: tuple[RegexElement, ...]


@dataclass(frozen=True)
class Optional(RegexElement):
    element: RegexElement


@dataclass(frozen=True)
class Capture(RegexElement):
    element: RegexElement


@dataclass(frozen=True)
class MatchState:
    """Intermediate matcher state."""

    index: int
    captures: tuple[LabelInstance, ...] = ()
    child_curr: LabelInstance | None = None


@dataclass(frozen=True)
class MatchResult:
    """Result of matching a pattern at one token index."""

    matched: bool
    child_curr: LabelInstance | None = None
    captures: tuple[LabelInstance, ...] = ()
    left_index_after_match: int | None = None

    @property
    def child_prev(self) -> LabelInstance | None:
        if not self.captures:
            return None
        return self.captures[-1]


@dataclass(frozen=True)
class Rule:
    """A transform rule that emits a label when its pattern matches."""

    emit: str
    pattern: RegexElement | str
    weight: float = 1.0
    _compiled: RegexElement = field(init=False, repr=False)

    def __post_init__(self) -> None:
        compiled = parse_pattern(self.pattern) if isinstance(
            self.pattern, str
        ) else self.pattern
        object.__setattr__(self, "_compiled", compiled)

    @property
    def compiled(self) -> RegexElement:
        return self._compiled

    def match_at(
        self,
        annotations: list[TokenAnnotation],
        token_index: int,
    ) -> MatchResult:
        return match_pattern(self.compiled, annotations, token_index)

    def apply_at(
        self,
        annotations: list[TokenAnnotation],
        token_index: int,
    ) -> Label | None:
        """Return the emitted label for this token, or None if no match."""
        result = self.match_at(annotations, token_index)
        if not result.matched or result.child_curr is None:
            return None

        child_prev = result.child_prev
        if child_prev is None:
            return Label(name=self.emit, weight=self.weight)

        return Label(
            name=self.emit,
            child_prev=child_prev.name,
            child_curr=result.child_curr.name,
            index_prev=child_prev.token_index,
            weight=self.weight,
        )


def parse_pattern(pattern: str) -> RegexElement:
    """Parse a pattern string into a RegexElement tree."""
    parser = _PatternParser(_tokenize_pattern(pattern))
    element = parser.parse()
    if parser.peek() is not None:
        raise PatternSyntaxError(
            f"Unexpected token {parser.peek()!r} at end of pattern"
        )
    return element


def match_pattern(
    pattern: RegexElement,
    annotations: list[TokenAnnotation],
    token_index: int,
) -> MatchResult:
    """Match a parsed pattern right-to-left from token_index."""
    state = MatchState(index=token_index)
    for next_state in _match_element(pattern, annotations, state):
        return MatchResult(
            matched=True,
            child_curr=next_state.child_curr,
            captures=next_state.captures,
            left_index_after_match=next_state.index,
        )
    return MatchResult(matched=False)


def apply_rule_at(
    annotations: list[TokenAnnotation],
    token_index: int,
    emit: str,
    pattern: str | RegexElement,
    weight: float = 1.0,
) -> Label | None:
    """Convenience wrapper for applying one rule at one token."""
    return Rule(emit=emit, pattern=pattern, weight=weight).apply_at(
        annotations, token_index
    )


def apply_rules(
    annotations: list[TokenAnnotation],
    rules: list[Rule],
) -> list[TokenAnnotation]:
    """Apply rules left-to-right and return a new annotation list.

    Labels emitted by earlier rules are visible to later rules on the same
    token and to all later tokens.
    """
    result = [
        TokenAnnotation(
            index=ann.index,
            token=ann.token,
            labels=list(ann.labels),
        )
        for ann in annotations
    ]

    for ann in result:
        for rule in rules:
            emitted = rule.apply_at(result, ann.index)
            if emitted is not None:
                ann.labels.append(emitted)

    return result


def compute_label_span(
    annotations: list[TokenAnnotation],
    token_index: int,
    label: Label,
) -> Span:
    """Compute the token span covered by a label instance.

    Duplicate label names are resolved by the first matching label on the
    referenced token.  Parameter-aware matching can be added when the diagram
    format starts relying on same-name duplicates.
    """
    if label.is_leaf:
        return Span(token_index, token_index)

    child_prev = _find_label(annotations, label.index_prev, label.child_prev)
    child_curr = _find_label(annotations, token_index, label.child_curr)

    if child_prev is None:
        raise ValueError(
            f"Missing child_prev {label.child_prev!r} at index "
            f"{label.index_prev}"
        )
    if child_curr is None:
        raise ValueError(
            f"Missing child_curr {label.child_curr!r} at index {token_index}"
        )

    prev_span = compute_label_span(annotations, label.index_prev, child_prev)
    curr_span = compute_label_span(annotations, token_index, child_curr)
    return Span(
        left=min(prev_span.left, curr_span.left),
        right=max(prev_span.right, curr_span.right),
    )


def label_instances_at(
    annotations: list[TokenAnnotation],
    token_index: int,
    name: str,
) -> list[LabelInstance]:
    """Return concrete label instances with this name at token_index."""
    ann = _annotation_at(annotations, token_index)
    if ann is None:
        return []

    instances: list[LabelInstance] = []
    for label in ann.labels:
        if label.name == name:
            instances.append(
                LabelInstance(
                    label=label,
                    token_index=token_index,
                    span=compute_label_span(annotations, token_index, label),
                )
            )
    return instances


def _tokenize_pattern(pattern: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()|?@":
            tokens.append(ch)
            i += 1
            continue
        if ch == '"':
            start = i
            i += 1
            value_chars: list[str] = []
            while i < len(pattern):
                if pattern[i] == "\\":
                    if i + 1 >= len(pattern):
                        raise PatternSyntaxError(
                            f"Unterminated escape in {pattern[start:]!r}"
                        )
                    value_chars.append(pattern[i + 1])
                    i += 2
                    continue
                if pattern[i] == '"':
                    i += 1
                    tokens.append('"' + "".join(value_chars) + '"')
                    break
                value_chars.append(pattern[i])
                i += 1
            else:
                raise PatternSyntaxError(
                    f"Unterminated string literal in {pattern[start:]!r}"
                )
            continue

        start = i
        while i < len(pattern) and not pattern[i].isspace() and pattern[i] not in "()|?@":
            i += 1
        tokens.append(pattern[start:i])
    return tokens


class _PatternParser:
    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> str | None:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def consume(self) -> str:
        token = self.peek()
        if token is None:
            raise PatternSyntaxError("Unexpected end of pattern")
        self.pos += 1
        return token

    def parse(self) -> RegexElement:
        return self.parse_union(stop_at_rparen=False)

    def parse_union(self, stop_at_rparen: bool) -> RegexElement:
        alternatives = [self.parse_sequence(stop_at_rparen=stop_at_rparen)]
        while self.peek() == "|":
            self.consume()
            alternatives.append(self.parse_sequence(stop_at_rparen=stop_at_rparen))

        if len(alternatives) == 1:
            return alternatives[0]
        return Union(tuple(alternatives))

    def parse_sequence(self, stop_at_rparen: bool) -> RegexElement:
        elements: list[RegexElement] = []
        while True:
            token = self.peek()
            if token is None or token == "|":
                break
            if token == ")":
                if stop_at_rparen:
                    break
                raise PatternSyntaxError("Unmatched ')' in pattern")
            elements.append(self.parse_postfix())

        if not elements:
            raise PatternSyntaxError("Expected pattern element")
        if len(elements) == 1:
            return elements[0]
        return Sequence(tuple(elements))

    def parse_postfix(self) -> RegexElement:
        element = self.parse_atom()
        if self.peek() == "?":
            self.consume()
            element = Optional(element)
        return element

    def parse_atom(self) -> RegexElement:
        token = self.consume()

        if token == "@":
            return Capture(self.parse_postfix())

        if token == "(":
            element = self.parse_union(stop_at_rparen=True)
            if self.peek() != ")":
                raise PatternSyntaxError("Unclosed '(' in pattern")
            self.consume()
            return Group(element)

        if token.startswith('"') and token.endswith('"'):
            return TokenLiteral(token[1:-1])

        if token == "BOF":
            return SentinelAtom(token)

        if token in {"|", ")", "?"}:
            raise PatternSyntaxError(f"Unexpected token {token!r}")

        return LabelAtom(token)


def _match_element(
    element: RegexElement,
    annotations: list[TokenAnnotation],
    state: MatchState,
) -> list[MatchState]:
    if isinstance(element, Sequence):
        states = [state]
        for child in reversed(element.elements):
            next_states: list[MatchState] = []
            for current in states:
                next_states.extend(_match_element(child, annotations, current))
            states = next_states
            if not states:
                break
        return states

    if isinstance(element, Group):
        return _match_element(element.element, annotations, state)

    if isinstance(element, Union):
        for alternative in element.alternatives:
            result = _match_element(alternative, annotations, state)
            if result:
                return result
        return []

    if isinstance(element, Optional):
        result = _match_element(element.element, annotations, state)
        if result:
            return result
        return [state]

    if isinstance(element, Capture):
        result = _match_element(element.element, annotations, state)
        captured: list[MatchState] = []
        for matched_state in result:
            capture = _capture_between(
                annotations=annotations,
                element=element.element,
                before=state,
                after=matched_state,
            )
            if capture is None:
                captured.append(matched_state)
            else:
                captured.append(
                    MatchState(
                        index=matched_state.index,
                        captures=matched_state.captures + (capture,),
                        child_curr=matched_state.child_curr,
                    )
                )
        return captured

    if isinstance(element, LabelAtom):
        if state.index < 0:
            return []
        results: list[MatchState] = []
        for instance in label_instances_at(annotations, state.index, element.name):
            child_curr = state.child_curr
            if child_curr is None:
                child_curr = instance
            results.append(
                MatchState(
                    index=instance.span.left - 1,
                    captures=state.captures,
                    child_curr=child_curr,
                )
            )
        return results

    if isinstance(element, TokenLiteral):
        ann = _annotation_at(annotations, state.index)
        if ann is None or ann.token != element.value:
            return []
        return [
            MatchState(
                index=state.index - 1,
                captures=state.captures,
                child_curr=state.child_curr,
            )
        ]

    if isinstance(element, SentinelAtom):
        if element.name == "BOF" and state.index == -1:
            return [state]
        return []

    raise TypeError(f"Unsupported pattern element: {element!r}")


def _capture_between(
    annotations: list[TokenAnnotation],
    element: RegexElement,
    before: MatchState,
    after: MatchState,
) -> LabelInstance | None:
    """Find the label instance captured by a successful Capture child match."""
    if isinstance(element, Optional):
        if before.index == after.index and before.child_curr == after.child_curr:
            return None
        return _capture_between(annotations, element.element, before, after)

    if isinstance(element, Group):
        return _capture_between(annotations, element.element, before, after)

    if isinstance(element, Union):
        for alternative in element.alternatives:
            result = _match_element(alternative, annotations, before)
            if after in result:
                return _capture_between(annotations, alternative, before, after)
        return None

    if isinstance(element, LabelAtom):
        if before.index < 0:
            return None
        for instance in label_instances_at(annotations, before.index, element.name):
            if instance.span.left - 1 == after.index:
                return instance
        return None

    # Capturing literals and sentinels is allowed syntactically but does not
    # produce a child_prev label.
    return None


def _annotation_at(
    annotations: list[TokenAnnotation],
    token_index: int,
) -> TokenAnnotation | None:
    if token_index < 0:
        return None
    for ann in annotations:
        if ann.index == token_index:
            return ann
    return None


def _find_label(
    annotations: list[TokenAnnotation],
    token_index: int | None,
    name: str | None,
) -> Label | None:
    if token_index is None or name is None:
        return None
    ann = _annotation_at(annotations, token_index)
    if ann is None:
        return None
    for label in ann.labels:
        if label.name == name:
            return label
    return None
