import time
import logging
import argparse
from pathlib import Path
from config import EMBEDDING_MODEL
from services.document_processor import process_docs_in_groups
from services.utils import configure_logging, format_time


def parse_arguments():
    """Sets up command-line argument parser."""
    parser = argparse.ArgumentParser(description="Process PDF Files")
    parser.add_argument(
        "--document_path",
        type=str,
        required=True,
        help="Path to document files",
    )
    parser.add_argument(
        "--max_files",
        type=int,
        default=250000,
        help="Maximum # of documents to process",
    )
    parser.add_argument(
        "--group_size",
        type=int,
        default=1000,
        help="# of documents being processed per group",
    )
    parser.add_argument(
        "--chunk_size", type=int, default=1000, help="Chunk size for text splitting"
    )
    parser.add_argument(
        "--chunk_overlap", type=int, default=20, help="Chunk overlap for text splitting"
    )
    parser.add_argument("--input_type", default="json", help="json or pdf")
    return parser.parse_args()


def main():
    # Configure logging and parse commmand line arguments
    configure_logging()
    args = parse_arguments()

    # Records start time to measure performance
    start_time = time.time()

    # Validate directory path
    docs_path = Path(args.document_path)
    if not docs_path.exists():
        logging.error(f"The directory ('{docs_path}' does not exist)")
        return

    # Make sure files exist
    logging.info(f"Searching for {args.input_type}s...")
    doc_files = list(docs_path.rglob(f"*.{args.input_type}"))[: args.max_files]
    if not doc_files:
        logging.info(f"No {args.input_type}s found.")
        return

    # Process documents and create knowledge vectorstore
    knowledge_vectorstore = process_docs_in_groups(
        doc_files,
        args.group_size,
        args.chunk_size,
        args.chunk_overlap,
        args.input_type,
        EMBEDDING_MODEL,
    )

    # Save knowledge vectorstore
    logging.info("\nSaving knowledge vectorstore...")
    index_dir = Path("./indexes")
    index_dir.mkdir(exist_ok=True)
    index_name = "faiss_index"
    knowledge_vectorstore.save_local(str(index_dir / index_name))
    logging.info("Knowledge vectorstore successfully saved.")

    # Log total execution time
    elapsed_time = format_time(time.time() - start_time)
    logging.info(f"\nTotal time elapsed to run program: {elapsed_time}")


if __name__ == "__main__":
    main()
