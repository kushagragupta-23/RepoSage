import argparse
from rag_pipeline import ask, index_info

parser = argparse.ArgumentParser(description="Ask RepoSage a codebase question.")
parser.add_argument("question", nargs="*", help="Question to ask")
args = parser.parse_args()

question = " ".join(args.question).strip() or input("Developer question: ").strip()
print("Indexed repository:", index_info().get("repo_path", "not indexed"))
answer, docs = ask(question)
print("\nANSWER\n", answer.answer)
print("\nOBSERVED EVIDENCE")
for item in answer.observed_evidence:
    print("-", item)
if answer.likely_causes:
    print("\nLIKELY CAUSES")
    for item in answer.likely_causes:
        print("-", item)
print("\nRECOMMENDED STEPS")
for item in answer.recommended_steps:
    print("-", item)
print("\nSOURCES")
for item in answer.source_references:
    print("-", item)
print("\nINFORMATION GAP:", answer.information_gap)
