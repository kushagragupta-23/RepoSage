import argparse
import pandas as pd
from rag_pipeline import evaluate_retrieval

parser = argparse.ArgumentParser(description="Compare RepoSage retrieval methods.")
parser.add_argument("--methods", nargs="+", default=["similarity", "mmr", "hybrid"])
args = parser.parse_args()

all_results = []
for method in args.methods:
    print(f"Evaluating: {method}")
    all_results.append(evaluate_retrieval(method))

results = pd.concat(all_results, ignore_index=True)
summary = results.groupby("method")[["source_hit", "symbol_hit", "reciprocal_rank"]].mean().round(3)
print("\nSUMMARY")
print(summary)
results.to_csv("evaluation/retrieval_results.csv", index=False)
summary.to_csv("evaluation/retrieval_summary.csv")
print("\nSaved evaluation/retrieval_results.csv and retrieval_summary.csv")
