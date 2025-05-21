import time
import logging
import json
from pathlib import Path
from tqdm import tqdm
from datasets import Dataset
from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from .utils import format_time

MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

JSON_SEPARATORS = ["/n/n", "/n", ". ", ", ", " ", ""]


def extract_text_from_json(json_file: Path) -> str:
    try:
        with open(json_file, "r") as f:
            bioc_data = json.load(f)

        all_text = []
        if isinstance(bioc_data, list):
            bioc_data = bioc_data[0]

        for document in bioc_data.get("documents", []):
            for passage in document.get("passages", []):
                all_text.append(passage.get("text", ""))
        return "\n".join(all_text)
    except json.JSONDecodeError:
        logging.warning(f"Skipping invalid JSON file: {json_file.name}")
        return ""
    except Exception as e:
        logging.error(f"Failed to process {json_file.name}: {e}")
        return ""


def process_docs_in_groups(
    input_files, group_size, chunk_size, chunk_overlap, input_type, embedding_model_name
):
    """Process and incrementally save documents to vector database"""

    if input_type == "json":
        separator_type = JSON_SEPARATORS
    else:
        separator_type = MARKDOWN_SEPARATORS

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        strip_whitespace=True,
        separators=separator_type,
    )

    embedding_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        multi_process=False,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )

    knowledge_vectorstore = None
    num_groups = (len(input_files) + group_size - 1) // group_size

    for i in range(0, len(input_files), group_size):
        group_files = input_files[i : i + group_size]
        group_index = i // group_size + 1
        logging.info(
            f"\nExtracting text from {input_type.upper()} Group {group_index}/{num_groups}"
        )
        doc_data = []

        skipped_files = []
        for file in tqdm(
            group_files, desc=f"{input_type.upper()} files", position=0, leave=False
        ):
            if input_type == "json":
                text = extract_text_from_json(file)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")

            if text:
                doc_data.append({"text": text, "source": str(file)})
            else:
                skipped_files.append(file.name)

        if skipped_files:
            logging.warning(
                f"Skipped files in group {group_index}: {', '.join(skipped_files)}"
            )

        if not doc_data:
            logging.warning(f"No valid documents in group {group_index}, skipping...")
            continue

        ds = Dataset.from_dict(
            {
                "text": [data["text"] for data in doc_data],
                "source": [data["source"] for data in doc_data],
            }
        )

        knowledge_base = [
            LangchainDocument(
                page_content=text, metadata={"source": source}
            )
            for text, source in zip(ds["text"], ds["source"])
        ]

        logging.info("Splitting text into chunks...")
        docs_processed = []
        for doc in knowledge_base:
            docs_processed += text_splitter.split_documents([doc])

        start_vectorstore_time = time.time()
        if knowledge_vectorstore is None:
            logging.info("Creating knowledge vectorstore...")
            knowledge_vectorstore = FAISS.from_documents(
                docs_processed,
                embedding_model,
                distance_strategy=DistanceStrategy.COSINE,
            )
        else:
            logging.info("Adding to knowledge vectorstore...")
            knowledge_vectorstore.add_documents(docs_processed)

        vectorstore_elapsed_time = format_time(int(time.time() - start_vectorstore_time))
        logging.info(
            f"Group {group_index} vectorstore added in {vectorstore_elapsed_time}"
        )

    return knowledge_vectorstore
