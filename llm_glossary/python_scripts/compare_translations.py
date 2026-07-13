import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import evaluate_candidates
from evaluation.reporting import format_evaluation_summary


parser = argparse.ArgumentParser(
    description="Compare translations generated with and without glossary context."
)
# Read command line input values.
parser.add_argument("--german-text", required=True)
parser.add_argument("--without-glossary", required=True)
parser.add_argument("--with-glossary", required=True)
parser.add_argument("--ground-truth")
args = parser.parse_args()

# Print source and translations.
print("German:")
print(args.german_text)

if args.ground_truth:
    print("\nGround truth:")
    print(args.ground_truth)

print("\nTranslation without glossary:")
print(args.without_glossary)

print("\nTranslation with glossary:")
print(args.with_glossary)

print("\nComparison:")

if args.ground_truth:
    # Evaluate both candidate translations.
    sources = [args.german_text]
    references = [args.ground_truth]
    without_metrics = evaluate_candidates(sources, references, [args.without_glossary])
    with_metrics = evaluate_candidates(sources, references, [args.with_glossary])
    print(format_evaluation_summary(without_metrics, with_metrics))
else:
    print("Pass --ground-truth to compute SacreBLEU, COMET, and BERTScore.")
