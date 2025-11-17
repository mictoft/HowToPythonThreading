#!/usr/bin/env python3
"""
CLI Launcher for Python Threading Examples

This script lists and runs all available threading examples.
"""

import sys
import os
import importlib.util
import argparse
from pathlib import Path
from typing import List, Dict, Any


def get_examples_dir() -> Path:
    """Get the examples directory path."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    return project_root / "examples"


def discover_examples() -> List[Dict[str, Any]]:
    """
    Discover all example files in the examples directory.

    Returns:
        List of dictionaries with example metadata
    """
    examples_dir = get_examples_dir()
    examples = []

    # Find all Python files starting with digits
    for file_path in sorted(examples_dir.glob("[0-9]*.py")):
        # Extract number and name
        filename = file_path.stem
        parts = filename.split("_", 1)

        if len(parts) == 2:
            number = parts[0]
            name = parts[1].replace("_", " ").title()

            # Try to extract docstring
            doc = extract_docstring(file_path)

            examples.append({
                "number": number,
                "name": name,
                "filename": file_path.name,
                "path": file_path,
                "docstring": doc
            })

    return examples


def extract_docstring(file_path: Path) -> str:
    """
    Extract the module docstring from a Python file.

    Args:
        file_path: Path to Python file

    Returns:
        First line of docstring or empty string
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        in_docstring = False
        docstring_lines = []

        for line in lines:
            if '"""' in line and not in_docstring:
                in_docstring = True
                # Get text after """
                text = line.split('"""', 1)[1].strip()
                if text:
                    docstring_lines.append(text)
                if line.count('"""') == 2:  # Single line docstring
                    break
            elif '"""' in line and in_docstring:
                # End of docstring
                text = line.split('"""')[0].strip()
                if text:
                    docstring_lines.append(text)
                break
            elif in_docstring:
                text = line.strip()
                if text:
                    docstring_lines.append(text)

        # Return first non-empty line
        for line in docstring_lines:
            if line and not line.startswith("Example"):
                return line

        return docstring_lines[0] if docstring_lines else ""

    except Exception:
        return ""


def list_examples(examples: List[Dict[str, Any]]):
    """
    Display all available examples.

    Args:
        examples: List of example metadata
    """
    print("\n" + "=" * 70)
    print("Python Threading Learning Examples")
    print("=" * 70 + "\n")

    for example in examples:
        print(f"{example['number']:>2}. {example['name']}")
        if example['docstring']:
            print(f"    {example['docstring']}")
        print()

    print("=" * 70)
    print(f"\nTotal examples: {len(examples)}")
    print("\nUsage:")
    print("  python -m launcher.cli <number>     # Run specific example")
    print("  python -m launcher.cli --list        # List all examples")
    print("  python -m launcher.cli --all         # Run all examples")
    print()


def run_example(example: Dict[str, Any]):
    """
    Run a specific example.

    Args:
        example: Example metadata dictionary
    """
    print("\n" + "=" * 70)
    print(f"Running: {example['number']}. {example['name']}")
    print("=" * 70 + "\n")

    try:
        # Load and run the module
        spec = importlib.util.spec_from_file_location(
            f"example_{example['number']}",
            example['path']
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        # Run main function if it exists
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"Warning: {example['filename']} has no main() function")

    except KeyboardInterrupt:
        print("\n\nExample interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\nError running example: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Python Threading Examples Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'example_number',
        nargs='?',
        help='Example number to run (e.g., 01, 1, 05, 5)'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available examples'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all examples sequentially'
    )

    args = parser.parse_args()

    # Discover examples
    examples = discover_examples()

    if not examples:
        print("Error: No examples found!")
        return 1

    # List mode
    if args.list or (not args.example_number and not args.all):
        list_examples(examples)
        return 0

    # Run all mode
    if args.all:
        print(f"\nRunning all {len(examples)} examples...\n")
        for i, example in enumerate(examples, 1):
            run_example(example)
            if i < len(examples):
                print("\n" + "-" * 70)
                input("\nPress Enter to continue to next example...")
        return 0

    # Run specific example
    if args.example_number:
        # Normalize example number (01 or 1 -> "01")
        example_num = args.example_number.zfill(2)

        # Find matching example
        matching_example = None
        for example in examples:
            if example['number'] == example_num:
                matching_example = example
                break

        if matching_example:
            run_example(matching_example)
            return 0
        else:
            print(f"Error: Example {example_num} not found!")
            print("\nAvailable examples:")
            for example in examples:
                print(f"  {example['number']}: {example['name']}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
