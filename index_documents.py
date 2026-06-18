#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from chunkers import VALID_STRATEGIES, chunk_text
from db import get_connection, init_schema, insert_chunks
from embeddings import embed_texts
from extractor import extract_text

logging.basicConfig(
    level=logging.WARNING,
    format="%(name)s [%(levelname)s] %(message)s",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index a PDF or DOCX into PostgreSQL.")
    parser.add_argument("--file", required=True, help="Path to PDF or DOCX file.")
    parser.add_argument("--strategy", required=True, choices=VALID_STRATEGIES)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    filename = Path(args.file).name
    print(f"Indexing '{filename}' with strategy='{args.strategy}'")

    print("  [1/4] Extracting text...")
    try:
        text = extract_text(args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"  Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"        {len(text):,} characters extracted.")

    print("  [2/4] Chunking...")
    try:
        chunks = chunk_text(text, args.strategy)
    except ValueError as exc:
        print(f"  Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"        {len(chunks)} chunks produced.")

    print("  [3/4] Generating embeddings...")
    try:
        embeddings = embed_texts(chunks)
    except (KeyError, RuntimeError) as exc:
        print(f"  Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"        dim={len(embeddings[0])}.")

    print("  [4/4] Storing in PostgreSQL...")
    try:
        conn = get_connection()
        init_schema(conn)
        count = insert_chunks(conn, chunks, embeddings, filename, args.strategy)
        conn.close()
    except Exception as exc:
        print(f"  Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"\nDone. {count} chunks indexed.")


if __name__ == "__main__":
    main()
