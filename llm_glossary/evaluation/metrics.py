"""Simple translation evaluation metric helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from statistics import mean


def compute_sacrebleu(reference: str, hypothesis: str) -> float:
    """Return sentence-level SacreBLEU score."""

    # Import library only when needed.
    import sacrebleu

    score = sacrebleu.sentence_bleu(hypothesis, [reference])
    return float(score.score)


def compute_corpus_sacrebleu(references: list[str], hypotheses: list[str]) -> float:
    """Return corpus-level SacreBLEU score."""

    # Check lists have same length.
    check_same_length(references, hypotheses)

    # Import library only when needed.
    import sacrebleu

    score = sacrebleu.corpus_bleu(hypotheses, [references])
    return float(score.score)


def compute_bertscore(reference: str, hypothesis: str) -> float:
    """Return BERTScore F1 score."""

    precision, recall, f1 = compute_bertscore_prf(reference, hypothesis)
    return f1


def compute_bertscore_prf(
    reference: str, hypothesis: str
) -> tuple[float, float, float]:
    """Return BERTScore precision, recall, F1."""

    scores = compute_bertscore_batch([reference], [hypothesis])
    return scores[0]


def compute_bertscore_batch(
    references: list[str], hypotheses: list[str]
) -> list[tuple[float, float, float]]:
    """Return BERTScore values for batches."""

    # Check lists have same length.
    check_same_length(references, hypotheses)

    # Import library only when needed.
    from bert_score import score

    # Read optional metric runtime settings.
    model_type = os.getenv("BERTSCORE_MODEL")
    device = os.getenv("BERTSCORE_DEVICE")
    batch_size = int(os.getenv("BERTSCORE_BATCH_SIZE", "16"))
    rescale = os.getenv("BERTSCORE_RESCALE_WITH_BASELINE", "true").lower()

    # Prepare BERTScore function keyword arguments.
    options = {
        "lang": "en",
        "batch_size": batch_size,
        "rescale_with_baseline": rescale in {"1", "true", "yes"},
        "verbose": False,
    }
    if model_type:
        options["model_type"] = model_type
    if device:
        options["device"] = device

    # Compute precision, recall, F1 scores.
    precision, recall, f1 = score(hypotheses, references, **options)

    results = []
    for p_score, r_score, f_score in zip(
        precision.tolist(), recall.tolist(), f1.tolist()
    ):
        results.append((float(p_score), float(r_score), float(f_score)))
    return results


def compute_comet(source: str, reference: str, hypothesis: str) -> float:
    """Return COMET score for one sentence."""

    scores = compute_comet_batch([source], [reference], [hypothesis])
    return scores[0]


def compute_comet_batch(
    sources: list[str], references: list[str], hypotheses: list[str]
) -> list[float]:
    """Return COMET scores for batches."""

    # Check lists have same length.
    check_same_length(sources, references)
    check_same_length(references, hypotheses)

    # Load COMET model only once.
    model = load_comet_model()

    # Read optional metric runtime settings.
    batch_size = int(os.getenv("COMET_BATCH_SIZE", "8"))
    gpus = int(os.getenv("COMET_GPUS", "0"))

    # Build COMET input data dictionaries.
    data = []
    for source, reference, hypothesis in zip(sources, references, hypotheses):
        data.append({"src": source, "ref": reference, "mt": hypothesis})

    # Run COMET model prediction step.
    try:
        prediction = model.predict(data, batch_size=batch_size, gpus=gpus)
    except TypeError:
        prediction = model.predict(data, batch_size=batch_size)

    return get_comet_scores(prediction)


def evaluate_candidates(
    sources: list[str], references: list[str], hypotheses: list[str]
) -> dict:
    """Evaluate one translation system batch."""

    # Check lists have same length.
    check_same_length(sources, references)
    check_same_length(references, hypotheses)

    # Compute sentence-level BLEU scores.
    bleu_scores = []
    for reference, hypothesis in zip(references, hypotheses):
        bleu_scores.append(compute_sacrebleu(reference, hypothesis))

    # Compute BERTScore for whole batch.
    bert_scores = compute_bertscore_batch(references, hypotheses)

    # Compute COMET for whole batch.
    comet_scores = compute_comet_batch(sources, references, hypotheses)

    # Combine metric scores per sentence.
    sentence_scores = []
    for bleu, bert, comet in zip(bleu_scores, bert_scores, comet_scores):
        precision, recall, f1 = bert
        sentence_scores.append(
            {
                "sacrebleu": bleu,
                "bertscore_precision": precision,
                "bertscore_recall": recall,
                "bertscore_f1": f1,
                "comet": comet,
            }
        )

    # Return averages and sentence scores.
    return {
        "sentence_scores": sentence_scores,
        "corpus_sacrebleu": compute_corpus_sacrebleu(references, hypotheses),
        "average_sacrebleu": average(bleu_scores),
        "average_bertscore_precision": average(
            [score["bertscore_precision"] for score in sentence_scores]
        ),
        "average_bertscore_recall": average(
            [score["bertscore_recall"] for score in sentence_scores]
        ),
        "average_bertscore_f1": average(
            [score["bertscore_f1"] for score in sentence_scores]
        ),
        "average_comet": average([score["comet"] for score in sentence_scores]),
    }


@lru_cache(maxsize=1)
def load_comet_model():
    """Load the COMET model once."""

    # Import library only when needed.
    from comet import download_model, load_from_checkpoint

    # Use default COMET model name.
    model_name = os.getenv("COMET_MODEL", "Unbabel/wmt22-comet-da")
    model_path = download_model(model_name)
    return load_from_checkpoint(model_path)


def get_comet_scores(prediction) -> list[float]:
    """Extract sentence COMET scores."""

    # Support different COMET output formats.
    if isinstance(prediction, dict):
        scores = prediction.get("scores")
    else:
        scores = getattr(prediction, "scores", None)

    if scores is None:
        raise RuntimeError("Could not read COMET scores.")

    return [float(score) for score in scores]


def average(values: list[float]) -> float:
    """Return average, or zero."""

    # Avoid errors for empty lists.
    if not values:
        return 0.0
    return float(mean(values))


def check_same_length(left: list[str], right: list[str]) -> None:
    """Check that lists align."""

    # Lists must stay properly aligned.
    if len(left) != len(right):
        raise ValueError(f"List lengths differ: {len(left)} != {len(right)}")
