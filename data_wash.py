#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_RAW_DATA_DIR = BASE_DIR / "data" / "raw_data"
DEFAULT_USER_DEFINED_FILE = BASE_DIR / "src" / "movie_analyze" / "intent" / "USER_DEFINED.json"

MOVIE_NAME_PAT = re.compile(r"《([^》]+)》")
ACTOR_NAME_PAT = re.compile(r"[（(]\s*([^()（）]*?)\s*飾(?:演)?\s*[）)]")


def clean_term(term, remove_inner_space=False):
    term = term.strip()
    term = re.sub(r"\s+", "" if remove_inner_space else " ", term)
    return term.strip("，,。.!！？?；;：「」『』【】[]()（）")


def unique_sorted(term_iterable):
    return sorted({term for term in term_iterable if term})


def extract_terms(text):
    movie_names = [clean_term(match) for match in MOVIE_NAME_PAT.findall(text)]
    actor_names = [clean_term(match, remove_inner_space=True) for match in ACTOR_NAME_PAT.findall(text)]

    return {
        "_movieName": unique_sorted(movie_names),
        "_actorName": unique_sorted(actor_names),
    }


def read_raw_text(raw_data_dir):
    content_list = []
    for text_path in sorted(raw_data_dir.glob("*.txt")):
        content_list.append(text_path.read_text(encoding="utf-8"))
    return "\n".join(content_list)


def merge_user_defined(user_defined_dict, extracted_dict):
    merged_dict = dict(user_defined_dict)

    for key, extracted_list in extracted_dict.items():
        existing_list = merged_dict.get(key, [])
        merged_dict[key] = unique_sorted([*existing_list, *extracted_list])

    return merged_dict


def update_user_defined(raw_data_dir, user_defined_file, dry_run=False):
    raw_text = read_raw_text(raw_data_dir)
    extracted_dict = extract_terms(raw_text)

    user_defined_dict = {}
    if user_defined_file.exists():
        user_defined_dict = json.loads(user_defined_file.read_text(encoding="utf-8"))

    merged_dict = merge_user_defined(user_defined_dict, extracted_dict)

    if not dry_run:
        user_defined_file.write_text(
            json.dumps(merged_dict, ensure_ascii=False, indent=4) + "\n",
            encoding="utf-8"
        )

    return extracted_dict, merged_dict


def main():
    parser = argparse.ArgumentParser(description="Extract movie and actor names into USER_DEFINED.json.")
    parser.add_argument("--raw-data-dir", type=Path, default=DEFAULT_RAW_DATA_DIR)
    parser.add_argument("--user-defined-file", type=Path, default=DEFAULT_USER_DEFINED_FILE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    extracted_dict, merged_dict = update_user_defined(
        raw_data_dir=args.raw_data_dir,
        user_defined_file=args.user_defined_file,
        dry_run=args.dry_run
    )

    print(f"extract _movieName: {len(extracted_dict['_movieName'])}")
    print(f"extract _actorName: {len(extracted_dict['_actorName'])}")
    print(f"merged _movieName: {len(merged_dict['_movieName'])}")
    print(f"merged _actorName: {len(merged_dict['_actorName'])}")

    if args.dry_run:
        print("dry-run only, USER_DEFINED.json was not changed")
    else:
        print(f"updated: {args.user_defined_file}")


if __name__ == "__main__":
    main()
