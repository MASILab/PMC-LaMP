import time
import torch
import logging
from .utils import format_time
from collections import namedtuple
from transformers import (
    BitsAndBytesConfig,
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import (
    READER_MODEL,
    EMBEDDING_MODEL,
    # RERANKER_MODEL,
    FAISS_INDEX,
    PROMPT_TEMPLATE,
)

log = logging.getLogger(__name__)


class ModelLoader:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Using device: {self.device}")

        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

    def load_models(self):
        try:
            init_start_time = time.time()

            log.info("Initializing embedding model...")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                multi_process=False,
                model_kwargs={"device": self.device},
                encode_kwargs={"normalize_embeddings": True},
            )

            self.knowledge_base = FAISS.load_local(
                FAISS_INDEX,
                embeddings=self.embedding_model,
                allow_dangerous_deserialization=True,
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                READER_MODEL, quantization_config=self.bnb_config
            )
            self.tokenizer = AutoTokenizer.from_pretrained(READER_MODEL)
            self.rag_prompt_template = self.tokenizer.apply_chat_template(
                PROMPT_TEMPLATE, tokenize=False, add_generation_prompt=True
            )

            self.reader_llm = pipeline(
                model=self.model,
                tokenizer=self.tokenizer,
                task="text-generation",
                do_sample=True,
                temperature=0.2,
                repetition_penalty=1.1,
                return_full_text=False,
                max_new_tokens=500,
            )

            # self.reranker = RERANKER_MODEL

            init_elapsed_time = format_time(time.time() - init_start_time)
            log.info(f"Models initialized in {init_elapsed_time}")

            return ModelDependencies(
                self.embedding_model,
                self.knowledge_base,
                self.reader_llm,
                self.rag_prompt_template,
                # self.reranker,
            )
        except Exception as e:
            log.error(f"Error during models initialization: {e}")
            raise e


ModelDependencies = namedtuple(
    "ModelDependencies",
    [
        "embedding_model",
        "knowledge_base",
        "reader_llm",
        "rag_prompt_template",
        # "reranker",
    ],
)
