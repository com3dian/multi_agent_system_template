"""
Main entry point for the Metadata Agent application.

This script uses the Orchestrator with planning + parallel execution + debate
to extract structured outputs from datasets.

Example Usage:
    # Single CSV file
    python -m src.main --source ./data/my_data.csv --topology default --objective "Profile this dataset"
    
    # Directory of CSVs
    python -m src.main --source ./data/my_dataset/ --topology default --objective-file ./objective.txt
    
    # SQLite database
    python -m src.main --source ./data/mydb.sqlite --objective "Generate relational metadata and key relationships"
"""
import argparse
import logging
import os
import sys
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.topology import EXECUTION_TOPOLOGIES
from src.orchestrator import Orchestrator
from src.context import create_context
from src.config import DEFAULT_OBJECTIVE


def load_objective(objective: str = "", objective_file: str = "") -> str:
    """Resolve objective text from direct input or a file."""
    if objective and objective.strip():
        return objective.strip()

    if objective_file:
        if not os.path.exists(objective_file):
            raise ValueError(f"Objective file not found: {objective_file}")
        with open(objective_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            raise ValueError(f"Objective file is empty: {objective_file}")
        return content

    return DEFAULT_OBJECTIVE


def main():
    """
    Main function to run the metadata agent.
    """
    parser = argparse.ArgumentParser(
        description="Run objective-driven analysis using multi-agent orchestration."
    )
    
    # Required arguments
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help=(
            "Path to the data source. Can be: "
            "a single CSV file, a directory of CSVs, or a SQLite database."
        )
    )
    
    # Configuration arguments
    parser.add_argument(
        "--name",
        type=str,
        default="dataset",
        help="Name for the context (used in logs/output)."
    )
    parser.add_argument(
        "--topology",
        type=str,
        default="default",
        choices=list(EXECUTION_TOPOLOGIES.keys()),
        help="The execution topology to use (defines parallelism and debate rounds)."
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help="Natural-language objective for the planner.",
    )
    parser.add_argument(
        "--objective-file",
        type=str,
        default="",
        help="Path to a text file containing the objective.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level."
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Validate source exists
    if not os.path.exists(args.source):
        logging.error(f"Source not found: {args.source}")
        return
    
    # Create ExecutionContext to get info for logging
    try:
        context = create_context(args.source, name=args.name)
    except Exception as e:
        logging.error(f"Failed to create context: {e}")
        return
    
    logging.info("=" * 60)
    logging.info("METADATA AGENT")
    logging.info("=" * 60)
    logging.info(f"Source: {args.source}")
    logging.info(f"Context Name: {context.name}")
    logging.info(f"Context Type: {context.context_type.value}")
    logging.info(f"Resources: {context.resources}")
    logging.info(f"Multi-resource: {context.is_multi_resource}")
    logging.info(f"Topology: {args.topology}")
    logging.info("=" * 60)
    
    try:
        objective = load_objective(args.objective, args.objective_file)
    except ValueError as e:
        logging.error(str(e))
        return
    logging.info(f"Objective: {objective}")

    # Initialize and run the orchestrator
    orchestrator = Orchestrator(topology_name=args.topology)
    
    result = orchestrator.run(
        source=context,
        objective=objective,
    )
    
    if result is None:
        logging.error("Orchestration failed. No result produced.")
        return
    
    # Print results
    print("\n" + "=" * 60)
    print("EXECUTION COMPLETE")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Steps Completed: {result.steps_completed}/{result.plan_steps_count}")
    
    print("\n--- Step Results ---")
    for step_result in result.step_results:
        print(f"\nStep {step_result.step_index + 1}: {step_result.task}")
        print(f"  Player: {step_result.player_role}")
        print(f"  Success: {step_result.success}")
        print(f"  Debate Rounds: {step_result.debate_rounds_completed}")
        if step_result.consolidated_result:
            print(f"  Result Preview: {step_result.consolidated_result[:200]}...")
    
    print("\n--- Final Workspace Artifacts ---")
    for name, value in result.final_workspace.items():
        preview = str(value)[:100] if value else "None"
        print(f"  {name}: {preview}...")
    
    if result.final_output:
        print("\n--- Final Output ---")
        pprint(result.final_output)


if __name__ == "__main__":
    main()
