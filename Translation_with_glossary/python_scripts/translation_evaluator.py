import csv
import os
from pathlib import Path

import sacrebleu
from comet import download_model, load_from_checkpoint


# Set the project path.
ROOT = Path(__file__).resolve().parents[1]

# Set both input files.
LLM_CSV = ROOT / "data/outputs/translation_with_llm.csv"
GLOSSARY_LLM_CSV = ROOT / "data/outputs/translation_with_llm_glossary.csv"

# Set the output file.
OUTPUT_CSV = ROOT / "data/outputs/translation_evaluation.csv"

# Set the COMET model.
COMET_MODEL = os.getenv("COMET_MODEL", "Unbabel/wmt22-comet-da")
COMET_BATCH_SIZE = int(os.getenv("COMET_BATCH_SIZE", "8"))


def load_comet_model():
    # Download the model once.
    model_path = download_model(COMET_MODEL)

    # Load the downloaded model.
    model = load_from_checkpoint(model_path)
    return model


def calculate_comet_scores(model, rows, translation_column):
    # Store COMET input rows.
    comet_data = []

    # Prepare every translation row.
    for row in rows:
        comet_data.append(
            {
                "src": row["de_text"],
                "mt": row[translation_column],
                "ref": row["en_grtr"],
            }
        )

    # Score the complete dataset.
    predictions = model.predict(
        comet_data,
        batch_size=COMET_BATCH_SIZE,
        gpus=0,
    )

    # Round every COMET score.
    scores = []
    for score in predictions.scores:
        scores.append(round(float(score), 4))

    return scores


def calculate_chrf_score(translation, ground_truth):
    # Compare translation and reference.
    result = sacrebleu.sentence_chrf(
        translation,
        [ground_truth],
    )

    # Return a rounded score.
    return round(result.score, 2)


def read_translation_file(file_path):
    # Store the translation rows.
    rows = []

    # Open one translation file.
    with open(file_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Read every translation row.
        for row in reader:
            rows.append(row)

    return rows


def combine_translation_files():
    # Read translations without glossary.
    llm_rows = read_translation_file(LLM_CSV)

    # Read translations with glossary.
    glossary_rows = read_translation_file(GLOSSARY_LLM_CSV)

    # Check equal row counts.
    if len(llm_rows) != len(glossary_rows):
        raise ValueError("Translation files have different row counts.")

    # Store the combined rows.
    combined_rows = []

    # Join matching translation rows.
    for llm_row, glossary_row in zip(llm_rows, glossary_rows):
        # Check the German texts.
        if llm_row["de_text"] != glossary_row["de_text"]:
            raise ValueError("German texts do not match.")

        # Check the ground truths.
        if llm_row["en_grtr"] != glossary_row["en_grtr"]:
            raise ValueError("Ground-truth texts do not match.")

        # Add one combined row.
        combined_rows.append(
            {
                "de_text": llm_row["de_text"],
                "en_grtr": llm_row["en_grtr"],
                "tr_llm": llm_row["en_tr_llm"],
                "tr_llm_glsr": glossary_row["en_tr_llm"],
            }
        )

    return combined_rows


def evaluate_all_rows(rows, comet_model):
    # Score normal LLM translations.
    llm_comet_scores = calculate_comet_scores(comet_model, rows, "tr_llm")

    # Score glossary LLM translations.
    glossary_comet_scores = calculate_comet_scores(
        comet_model,
        rows,
        "tr_llm_glsr",
    )

    # Store all evaluated rows.
    evaluated_rows = []

    # Evaluate each translation pair.
    for index, row in enumerate(rows):
        # Calculate both chrF scores.
        llm_chrf_score = calculate_chrf_score(row["tr_llm"], row["en_grtr"])
        glossary_chrf_score = calculate_chrf_score(
            row["tr_llm_glsr"],
            row["en_grtr"],
        )

        # Add one evaluated row.
        evaluated_rows.append(
            {
                "de_text": row["de_text"],
                "en_grtr": row["en_grtr"],
                "tr_llm": row["tr_llm"],
                "tr_llm_comet_score": llm_comet_scores[index],
                "tr_llm_chrF_score": llm_chrf_score,
                "tr_llm_glsr": row["tr_llm_glsr"],
                "tr_llm_glsr_comet_score": glossary_comet_scores[index],
                "tr_llm_glsr_chrF_score": glossary_chrf_score,
            }
        )

    return evaluated_rows


def save_evaluation(rows):
    # Set the output columns.
    columns = [
        "de_text",
        "en_grtr",
        "tr_llm",
        "tr_llm_comet_score",
        "tr_llm_chrF_score",
        "tr_llm_glsr",
        "tr_llm_glsr_comet_score",
        "tr_llm_glsr_chrF_score",
    ]

    # Create the output folder.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Write all evaluated rows.
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def print_average_scores(rows):
    # Add all metric scores.
    llm_comet_total = 0
    glossary_comet_total = 0
    llm_chrf_total = 0
    glossary_chrf_total = 0

    for row in rows:
        llm_comet_total += row["tr_llm_comet_score"]
        glossary_comet_total += row["tr_llm_glsr_comet_score"]
        llm_chrf_total += row["tr_llm_chrF_score"]
        glossary_chrf_total += row["tr_llm_glsr_chrF_score"]

    # Calculate all score averages.
    row_count = len(rows)
    llm_comet_average = llm_comet_total / row_count
    glossary_comet_average = glossary_comet_total / row_count
    llm_chrf_average = llm_chrf_total / row_count
    glossary_chrf_average = glossary_chrf_total / row_count

    # Print the average scores.
    print(f"Without glossary COMET average: {llm_comet_average:.4f}")
    print(f"With glossary COMET average: {glossary_comet_average:.4f}")
    print(f"Without glossary chrF average: {llm_chrf_average:.2f}")
    print(f"With glossary chrF average: {glossary_chrf_average:.2f}")

    # Compare both COMET averages.
    if glossary_comet_average > llm_comet_average:
        print("COMET winner: translation with glossary")
    elif llm_comet_average > glossary_comet_average:
        print("COMET winner: translation without glossary")
    else:
        print("COMET result: both are equal")

    # Compare both chrF averages.
    if glossary_chrf_average > llm_chrf_average:
        print("chrF winner: translation with glossary")
    elif llm_chrf_average > glossary_chrf_average:
        print("chrF winner: translation without glossary")
    else:
        print("chrF result: both are equal")


def main():
    # Read and combine translations.
    rows = combine_translation_files()
    print(f"Loaded {len(rows)} translation pairs")

    # Load the COMET model.
    comet_model = load_comet_model()

    # Calculate all quality scores.
    evaluated_rows = evaluate_all_rows(rows, comet_model)

    # Save the final results.
    save_evaluation(evaluated_rows)
    print(f"Saved evaluation: {OUTPUT_CSV}")

    # Print average score results.
    print_average_scores(evaluated_rows)


if __name__ == "__main__":
    main()
