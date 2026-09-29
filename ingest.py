import argparse
from rag_pipeline import DEMO_REPO, ingest

parser = argparse.ArgumentParser(description="Build the RepoSage Chroma index.")
parser.add_argument("--repo", default=str(DEMO_REPO), help="Path to a local repository. Defaults to bundled demo repo.")
args = parser.parse_args()

info = ingest(args.repo, rebuild=True)
print("RepoSage index built successfully")
for key, value in info.items():
    print(f"{key}: {value}")
