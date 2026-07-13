"""Simple reporting helpers for evaluation."""

from __future__ import annotations


def format_evaluation_summary(
    without_glossary: dict, with_glossary: dict
) -> str:
    """Format the main metric summary."""

    return f"""==============================
Evaluation Summary
==============================
Without Glossary
Average sentence SacreBLEU: {without_glossary["average_sacrebleu"]:.2f}
Corpus SacreBLEU: {without_glossary["corpus_sacrebleu"]:.2f}
Average COMET: {without_glossary["average_comet"]:.4f}
Average BERTScore F1: {without_glossary["average_bertscore_f1"]:.4f}

With Glossary
Average sentence SacreBLEU: {with_glossary["average_sacrebleu"]:.2f}
Corpus SacreBLEU: {with_glossary["corpus_sacrebleu"]:.2f}
Average COMET: {with_glossary["average_comet"]:.4f}
Average BERTScore F1: {with_glossary["average_bertscore_f1"]:.4f}"""
