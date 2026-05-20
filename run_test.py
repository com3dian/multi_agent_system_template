"""
A simple test script to run the metadata agent with explicit objectives.
"""
import os

# --- Using inline objective ---
print("--- Running with inline objective ---")
os.system(
    "python -m src.main "
    "--source ./data/test_data.csv "
    "--topology fast "
    "--objective \"Analyze this dataset and return key structure + quality findings.\""
)
print("\n" * 3)


# --- Using objective from file ---
objective_content = """
Analyze the dataset resources and produce:
1) schema summary,
2) row/field-level quality concerns,
3) recommended next analysis steps.
"""
objective_path = "./data/objective.txt"
with open(objective_path, "w", encoding="utf-8") as f:
    f.write(objective_content)

print(f"--- Running with objective from file: {objective_path} ---")
os.system(
    f"python -m src.main "
    f"--source ./data/test_data.csv "
    f"--topology fast "
    f"--objective-file {objective_path}"
)

# Clean up
os.remove(objective_path)
