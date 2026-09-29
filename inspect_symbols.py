import argparse
from rag_pipeline import symbols

parser = argparse.ArgumentParser(description="Inspect Python classes/functions in the indexed repository.")
parser.add_argument("relative_path", help="Example: src/auth.py")
args = parser.parse_args()

for item in symbols(args.relative_path):
    print(f"{item['type']:<16} {item['name']:<30} lines {item['line_start']}-{item['line_end']}")
