#!/usr/bin/env python3
"""
Validate all draft puzzle JSON files against the puzzle.schema.json.
Usage: python validate_schema.py
"""
import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError

# Paths (adjust as needed)
BASE_DIR    = Path(__file__).parent
SCHEMA_FILE = BASE_DIR / 'puzzle.schema.json'
DRAFTS_DIR  = BASE_DIR / 'puzzles' / 'drafts'


def main():
    # Load schema
    try:
        schema = json.loads(SCHEMA_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)

    # Validate each draft JSON
    errors = 0
    for draft in sorted(DRAFTS_DIR.glob('*.json')):
        try:
            data = json.loads(draft.read_text(encoding='utf-8'))
            validate(instance=data, schema=schema)
            print(f"{draft.name}: OK")
        except ValidationError as ve:
            print(f"{draft.name}: INVALID - {ve.message}")
            errors += 1
        except SchemaError as se:
            print(f"Invalid schema definition: {se.message}")
            sys.exit(2)
        except Exception as e:
            print(f"{draft.name}: Error reading or parsing - {e}")
            errors += 1

    if errors:
        print(f"\n{errors} draft(s) failed validation.")
        sys.exit(1)
    else:
        print(f"\nAll {len(list(DRAFTS_DIR.glob('*.json')))} drafts validated successfully.")


if __name__ == '__main__':
    main()
