#!/usr/bin/env python3
import argparse
import logging
import sys

from dotenv import load_dotenv

from db import get_connection, search_similar
from embeddings import embed_query

logging.basicConfig(
    level=logging.WARNING,
    format="%(name)s [%(levelname)s] %(message)s",
)

SIMILARITY_THRESHOLD = 0.55


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Semantic search over indexed document chunks.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    try:
        query_embedding = embed_query(args.query)
    except (KeyError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        conn = get_connection()
        results = search_similar(conn, query_embedding, top_k=args.top_k)
        conn.close()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    results = [(cid, ct, fn, st, ca, d) for cid, ct, fn, st, ca, d in results if (1 - d) >= SIMILARITY_THRESHOLD]

    if not results:
        print("No results found.")
        sys.exit(0)

    print(f"\nQuery: \"{args.query}\"  —  {len(results)} result(s)\n")
    for rank, (chunk_id, chunk_text, filename, strategy, created_at, distance) in enumerate(results, 1):
        score = 1 - distance
        preview = chunk_text[:280].replace("\n", " ")
        if len(chunk_text) > 280:
            preview += "..."
        print(f"[{rank}] score={score:.4f}  file={filename}  strategy={strategy}  id={chunk_id}")
        print(f"    {preview}\n")


if __name__ == "__main__":
    main()
