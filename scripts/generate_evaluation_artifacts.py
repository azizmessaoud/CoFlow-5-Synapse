from pathlib import Path

from coflow5.evaluation import generate_evaluation_artifacts


if __name__ == "__main__":
    report = generate_evaluation_artifacts(Path(__file__).resolve().parents[1])
    print(f"headline={report['headline']['claim_id']}")
    print(f"cells={report['experiment_summary']['cell_count']}")
    print(f"kpis={report['metric_summary']['row_count']}")
