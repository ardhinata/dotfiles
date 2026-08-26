#!/usr/bin/env python3
"""Checker for ASD-STE100 Simplified Technical English.

Applies the writing rules that plain text can show. It has no dictionary and no
part-of-speech analysis, so it cannot prove conformance. Read the output as help.

Usage:
    python3 ste_check.py FILE [FILE ...]
    python3 ste_check.py --mode procedural FILE
    python3 ste_check.py --json FILE
    cat FILE | python3 ste_check.py -

Exit status: 1 when it finds an error, 0 when it finds none.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict

LIMITS = {"procedural": 20, "descriptive": 25}

CONTRACTIONS = re.compile(
    r"\b(?:can't|cannot've|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't|"
    r"hasn't|haven't|hadn't|shouldn't|wouldn't|couldn't|mustn't|it's|that's|there's|"
    r"we're|they're|you're|i'm|we've|they've|you've|i've|we'll|they'll|you'll|it'll|"
    r"let's|he's|she's|what's|who's|ain't)\b",
    re.I,
)

IRREGULAR_PARTICIPLES = {
    "been", "done", "gone", "made", "found", "given", "taken", "written", "shown",
    "known", "seen", "set", "put", "sent", "kept", "held", "read", "run", "built",
    "broken", "chosen", "driven", "drawn", "eaten", "fallen", "forgotten", "frozen",
    "hidden", "lost", "meant", "met", "paid", "said", "sold", "spent", "stolen",
    "taught", "told", "thrown", "understood", "worn", "won", "cut", "left", "let",
    "lit", "shut", "split", "spread", "began", "begun", "come", "become", "brought",
}

PHRASAL_VERBS = [
    "set up", "sets up", "setting up", "put together", "take off", "takes off",
    "put in", "turn on", "turns on", "turn off", "turns off", "find out", "finds out",
    "carry out", "carries out", "go through", "goes through", "bring up", "brings up",
    "shut down", "shuts down", "back up", "backs up", "roll out", "rolls out",
    "roll back", "rolls back", "spin up", "spins up", "tear down", "tears down",
    "look into", "looks into", "come up with", "figure out", "figures out",
    "go ahead", "check out", "checks out", "fill out", "fills out", "log in",
    "log out", "sign in", "sign up", "hand over", "hands over", "point out",
]

UNAPPROVED_WORDS = {
    "verify": "make sure", "verifies": "makes sure", "verified": "made sure",
    "ensure": "make sure", "ensures": "makes sure", "ensured": "made sure",
    "confirm": "make sure", "confirms": "makes sure", "confirmed": "made sure",
    "validate": "make sure", "validates": "makes sure",
    "utilize": "use", "utilizes": "use", "utilise": "use",
    "leverage": "use", "leverages": "use",
    "obtain": "get", "obtains": "get", "obtained": "got",
    "perform": "do", "performs": "do", "performed": "did",
    "accomplish": "do", "achieve": "do", "achieves": "do",
    "commence": "start", "initiate": "start", "initiates": "start",
    "terminate": "stop", "terminates": "stop", "cease": "stop",
    "indicate": "show", "indicates": "show",
    "identify": "find", "identifies": "find",
    "modify": "change", "modifies": "change",
    "approximately": "about", "sufficient": "enough", "adequate": "enough",
    "additional": "more", "numerous": "many", "subsequent": "next",
    "prior": "earlier", "optimum": "best", "optimal": "best",
    "erroneous": "incorrect", "methodology": "method",
    "however": "but", "nevertheless": "but", "nonetheless": "but",
    "furthermore": "also", "moreover": "also", "additionally": "also",
    "currently": "now", "presently": "now", "whilst": "while",
    "regarding": "about", "concerning": "about",
}

WORDY_PHRASES = {
    "due to the fact that": "because",
    "owing to the fact that": "because",
    "in order to": "to",
    "in the event that": "if",
    "prior to": "before",
    "subsequent to": "after",
    "with regard to": "about",
    "with respect to": "about",
    "in conjunction with": "with",
    "by means of": "with",
    "at this time": "now",
    "in the vicinity of": "near",
    "it is worth noting that": "(remove)",
    "it should be noted that": "(remove)",
    "please note that": "(remove)",
}

LATIN = {"e.g.": "for example", "i.e.": "that is", "etc.": "the complete list",
         "vs.": "compared to", "et al.": "and other persons", "n.b.": "note"}

STOPWORDS = {
    "a", "an", "the", "of", "for", "to", "in", "on", "at", "by", "with", "from",
    "and", "or", "but", "if", "when", "then", "than", "as", "is", "are", "was",
    "were", "be", "been", "this", "that", "these", "those", "it", "its", "you",
    "your", "we", "our", "they", "their", "he", "she", "his", "her", "not", "no",
    "do", "does", "did", "can", "must", "will", "would", "should", "may", "each",
    "all", "any", "one", "two", "three", "more", "most", "other", "same", "only",
    "also", "therefore", "because", "so", "use", "uses", "used", "make", "makes",
    "give", "gives", "get", "gets", "has", "have", "had", "there", "here", "how",
}

# Rule 3.5 permits an "-ing" word as a technical noun. Rule 1.8 says each organization
# approves its own technical nouns, so extend this with --technical-nouns.
DEFAULT_TECHNICAL_NOUNS = {
    "string", "during", "thing", "warning", "setting", "settings", "bearing", "logging",
    "engineering", "training", "meaning", "staging", "caching", "routing", "streaming",
    "monitoring", "encoding", "mapping", "binding", "listing", "heading", "padding",
    "polling", "sampling", "timing", "tracing", "versioning", "indexing", "sharding",
    "handling", "processing", "testing", "building", "packaging", "branching", "tagging",
    "onboarding", "provisioning", "scaling", "throttling", "batching", "queueing",
}


def load_technical_nouns(path: str | None) -> set[str]:
    """Read one term for each line. A line that starts with # is a comment."""
    nouns = set(DEFAULT_TECHNICAL_NOUNS)
    if not path:
        return nouns
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            term = line.split("#", 1)[0].strip().lower()
            if term:
                nouns.add(term)
    return nouns


@dataclass
class Finding:
    path: str
    line: int
    rule: str
    severity: str
    message: str
    excerpt: str


def strip_markdown(text: str, include_quotes: bool = False) -> list[tuple[int, str, str]]:
    """Return (line, prose, kind) triples. kind is 'para' or 'item'.

    Removes frontmatter, fenced code, tables, headings, and rules. Blockquotes hold
    quotations and deliberate bad examples, so it skips them unless include_quotes is set.
    """
    out: list[tuple[int, str, str]] = []
    in_fence = False
    in_frontmatter = False
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if i == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.lstrip()
        if stripped.startswith("|") or stripped.startswith("#"):
            continue
        if re.fullmatch(r"[-*_ ]{3,}", stripped):
            continue
        if stripped.startswith(">"):
            if not include_quotes:
                continue
            stripped = re.sub(r"^>\s?", "", stripped)
        # Rule 4.3: each item of a vertical list is its own unit.
        kind = "para"
        item = re.sub(r"^(?:[-*+]|\d+\.)\s+", "", stripped)
        if item != stripped:
            kind = "item"
            stripped = item
        if stripped:
            out.append((i, stripped, kind))
    return out


SENTINEL = "\x00"

# Dots and colons that must not end a sentence. Each pattern is replaced by a
# same-length sentinel so that character offsets, and therefore line numbers, survive.
NO_SPLIT = [
    re.compile(r"\b(?:e\.g|i\.e|etc|vs|n\.b|et al|dr|mr|mrs|ms|inc|ltd|fig|no|approx)\.", re.I),
    re.compile(r"(?<=\d)\.(?=\d)"),          # 3.9, 1.024
    re.compile(r"(?<=\d):(?=\d)"),           # 10:30
    re.compile(r"://"),                      # https://
    re.compile(r"\b[A-Za-z]\.(?=[A-Za-z]\.)"),  # a.b.c
]


def mask_no_split(text: str) -> str:
    """Replace sentence-ending characters that are not sentence ends. Length is unchanged."""
    chars = list(text)
    for pattern in NO_SPLIT:
        for match in pattern.finditer(text):
            for i in range(match.start(), match.end()):
                if chars[i] in ".:":
                    chars[i] = SENTINEL
    return "".join(chars)


def to_sentences(blocks: list[tuple[int, str, str]]) -> list[tuple[int, str]]:
    """Split prose into sentences. Each sentence keeps the line where it starts.

    A blank line ends a paragraph. `strip_markdown` drops blank lines, so a gap in the
    line numbers marks the boundary. A list item is always its own unit (rule 4.3).
    """
    sentences: list[tuple[int, str]] = []
    paragraph: list[tuple[int, str]] = []

    def flush(par: list[tuple[int, str]]) -> None:
        if not par:
            return
        # Record where each source line starts inside the joined paragraph.
        spans: list[tuple[int, int]] = []
        offset = 0
        pieces: list[str] = []
        for line, prose in par:
            spans.append((offset, line))
            pieces.append(prose)
            offset += len(prose) + 1
        joined = " ".join(pieces)
        masked = mask_no_split(joined)

        def line_of(pos: int) -> int:
            found = spans[0][1]
            for start, line in spans:
                if start <= pos:
                    found = line
                else:
                    break
            return found

        # Rule 8.4: in a vertical list a colon ends a sentence.
        for match in re.finditer(r"[^.!?:]+(?:[.!?:]+|$)", masked):
            text = joined[match.start():match.end()].strip().rstrip(".!?:").strip()
            if text:
                sentences.append((line_of(match.start()), text))

    previous_line = None
    for line, prose, kind in blocks:
        starts_new = (
            kind == "item"
            or previous_line is None
            or line != previous_line + 1
        )
        if starts_new:
            flush(paragraph)
            paragraph = []
        paragraph.append((line, prose))
        previous_line = line
    flush(paragraph)
    return sentences


def count_words(sentence: str) -> int:
    """Word count under rules 8.5, 8.6, and 8.7."""
    s = sentence
    s = re.sub(r"`[^`]*`", " CODE ", s)                    # inline code = 1 word
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)          # link text only
    s = re.sub(r"https?://\S+", " URL ", s)
    s = re.sub(r"\([^)]*\)", " PAREN ", s)                  # rule 8.5
    s = re.sub(r"\b\d+(?:\.\d+)?\s*[A-Za-z%]+\b", " VALUE ", s)  # rule 8.6
    tokens = re.findall(r"[A-Za-z0-9$_./-]+", s)            # rule 8.7 keeps hyphens joined
    return len(tokens)


def check_sentence(path: str, line: int, sent: str, limit: int,
                   technical_nouns: set[str]) -> list[Finding]:
    f: list[Finding] = []
    low = sent.lower()
    bare = re.sub(r"`[^`]*`", " ", sent)          # never flag inside inline code
    bare_low = bare.lower()

    n = count_words(sent)
    if n > limit:
        f.append(Finding(path, line, "5.1/6.3", "error",
                         f"Sentence has {n} words. The maximum is {limit}.", sent[:90]))
    if ";" in bare:
        f.append(Finding(path, line, "8.1", "error", "Semicolon is not permitted.", sent[:90]))
    for m in CONTRACTIONS.finditer(bare):
        f.append(Finding(path, line, "4.2", "error",
                         f"Contraction '{m.group(0)}'. Write the full form.", sent[:90]))
    for m in re.finditer(r"\b(have|has|had|will have|would have)\s+(\w+)\b", bare_low):
        word = m.group(2)
        if word in IRREGULAR_PARTICIPLES or word.endswith("ed"):
            f.append(Finding(path, line, "3.2/3.4", "error",
                             f"Complex verb form '{m.group(0)}'. Use a simple tense.", sent[:90]))
    for m in re.finditer(r"\b(is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(\w+)\b", bare_low):
        word = m.group(2)
        if word in IRREGULAR_PARTICIPLES or (word.endswith("ed") and len(word) > 4):
            f.append(Finding(path, line, "3.6", "warning",
                             f"Possible passive voice '{m.group(0)}'. Name the agent.", sent[:90]))
    for m in re.finditer(r"\b(\w{4,}ing)\b", bare):
        if m.group(1).lower() not in technical_nouns:
            f.append(Finding(path, line, "3.5", "warning",
                             f"'-ing' form '{m.group(1)}'. Permitted only as a technical noun. "
                             f"Add it with --technical-nouns if it is one.",
                             sent[:90]))
    for phrase in PHRASAL_VERBS:
        if re.search(rf"\b{re.escape(phrase)}\b", bare_low):
            f.append(Finding(path, line, "9.3", "error",
                             f"Phrasal verb '{phrase}'. Use one approved verb.", sent[:90]))
    for phrase, better in WORDY_PHRASES.items():
        if phrase in bare_low:
            f.append(Finding(path, line, "9.1", "warning",
                             f"Wordy phrase '{phrase}'. Use '{better}'.", sent[:90]))
    for word, better in UNAPPROVED_WORDS.items():
        if re.search(rf"\b{word}\b", bare_low):
            f.append(Finding(path, line, "1.1/1.3", "warning",
                             f"'{word}' is probably not approved. Use '{better}'.", sent[:90]))
    for abbr, better in LATIN.items():
        if abbr in bare_low:
            f.append(Finding(path, line, "GR-6", "error",
                             f"Latin abbreviation '{abbr}'. Write '{better}'.", sent[:90]))
    if "&" in bare:
        f.append(Finding(path, line, "GESG-8.1", "warning", "Ampersand. Write 'and'.", sent[:90]))
    if re.search(r"\w\(s\)", bare):
        f.append(Finding(path, line, "GESG-8.8.6", "warning",
                         "'(s)' for a plural. Write 'one or more ...'.", sent[:90]))
    words = re.findall(r"\b[A-Za-z][A-Za-z-]*\b", re.sub(r"`[^`]*`", " ", sent))
    run: list[str] = []
    for w in words + [""]:
        if w and w.lower() not in STOPWORDS and w.islower():
            run.append(w)
        else:
            if len(run) >= 4:
                f.append(Finding(path, line, "2.1", "warning",
                                 f"Possible noun cluster of {len(run)} words: "
                                 f"'{' '.join(run)}'. The maximum is 3.", sent[:90]))
            run = []
    return f


def check_text(path: str, text: str, limit: int, technical_nouns: set[str],
               include_quotes: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for line, sent in to_sentences(strip_markdown(text, include_quotes)):
        findings.extend(check_sentence(path, line, sent, limit, technical_nouns))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="ASD-STE100 checker (rules only, no dictionary).")
    ap.add_argument("files", nargs="+", help="files to check, or - for standard input")
    ap.add_argument("--mode", choices=sorted(LIMITS), default="descriptive",
                    help="procedural = 20 words, descriptive = 25 words (default)")
    ap.add_argument("--max-words", type=int, default=None, help="override the word limit")
    ap.add_argument("--technical-nouns", default=None,
                    help="file of approved technical nouns, one for each line (rule 1.8)")
    ap.add_argument("--include-quotes", action="store_true",
                    help="also check blockquotes. They are skipped by default, because they "
                         "hold quotations and deliberate bad examples.")
    ap.add_argument("--json", action="store_true", help="write JSON")
    ap.add_argument("--errors-only", action="store_true", help="hide warnings")
    args = ap.parse_args()

    limit = args.max_words or LIMITS[args.mode]
    technical_nouns = load_technical_nouns(args.technical_nouns)
    findings: list[Finding] = []
    for path in args.files:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        findings.extend(check_text(path, text, limit, technical_nouns, args.include_quotes))
    if args.errors_only:
        findings = [f for f in findings if f.severity == "error"]

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for f in findings:
            print(f"{f.path}:{f.line}: [{f.severity}] rule {f.rule}: {f.message}")
            print(f"    {f.excerpt}")
        errors = sum(1 for f in findings if f.severity == "error")
        warnings = len(findings) - errors
        print(f"\n{errors} error(s), {warnings} warning(s). "
              f"Mode: {args.mode}, limit {limit} words.")
        print("The checker has no dictionary. It cannot prove conformance.")
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
