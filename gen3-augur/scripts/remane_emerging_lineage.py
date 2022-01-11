import json
import argparse, sys, os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename clade_membership as emerging_lineage",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--file", type=str, help="emerging lineage json file ")
    args = parser.parse_args()


with open(args.file, "r", encoding="utf-8") as fh:
    d = json.load(fh)
    new_data = {}
    for k, v in d["nodes"].items():
        if "clade_membership" in v:
            new_data[k] = {"emerging_lineage": v["clade_membership"]}
with open(args.file, "w") as fh:
    json.dump({"nodes": new_data}, fh, indent=2)
