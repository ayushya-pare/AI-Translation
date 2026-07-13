"""Smoke-test the translation evaluation metrics on a tiny fixed dataset.

Run from the repository root:

    python tests/validate_metrics.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import evaluate_candidates
from evaluation.reporting import format_evaluation_summary


def main() -> None:
    """Evaluate two miniature systems and print sentence and average scores."""

    # Define fixed German source sentences.
    sources = [
        "Bitte senden Sie den Antrag per E-Mail.",
        "Die Prüfungsordnung gilt für alle Studierenden.",
        "Weitere Informationen finden Sie auf der Webseite der Universität Bonn.",
    ]
    # Define expected English reference translations.
    references = [
        "Please send the application by email.",
        "The examination regulations apply to all students.",
        "Further information can be found on the University of Bonn website.",
    ]
    # Define baseline translation candidates.
    without_glossary = [
        "Please send the request by e-mail.",
        "The exam rules apply to all students.",
        "More information is available on the website of Bonn University.",
    ]
    # Define glossary-improved translation candidates.
    with_glossary = [
        "Please submit the application by email.",
        "The examination regulations apply to all students.",
        "Further information can be found on the University of Bonn website.",
    ]

    # Evaluate both translation candidate sets.
    without_metrics = evaluate_candidates(sources, references, without_glossary)
    with_metrics = evaluate_candidates(sources, references, with_glossary)

    # Print sentence-level metric values.
    for label, batch in (
        ("Without Glossary", without_metrics),
        ("With Glossary", with_metrics),
    ):
        print(f"\n{label} sentence scores")
        for index, scores in enumerate(batch["sentence_scores"], start=1):
            print(
                f"{index}: BLEU={scores['sacrebleu']:.2f}, "
                f"COMET={scores['comet']:.4f}, "
                f"BERTScore_F1={scores['bertscore_f1']:.4f}"
            )

    # Print average metric summary.
    print()
    print(format_evaluation_summary(without_metrics, with_metrics))


if __name__ == "__main__":
    main()
