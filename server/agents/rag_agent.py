import langroid as lr

class RagAgentConfig(lr.agent.special.DocChatAgentConfig):
    n_query_rephrases: int = 0
    hypothetical_answer: bool = False
    extraction_granularity: int = 3
    n_neighbor_chunks: int = 4
    parsing: lr.parsing.ParsingConfig = lr.parsing.ParsingConfig(  # modify as needed
        splitter=lr.parsing.Splitter.TOKENS,
        chunk_size=200,  # aim for this many tokens per chunk
        overlap=50,  # overlap between chunks
        max_chunks=10_000,
        n_neighbor_ids=5,  # store ids of window of k chunks around each chunk.
        # aim to have at least this many chars per chunk when
        # truncating due to punctuation
        min_chunk_chars=200,
        discard_chunk_chars=5,  # discard chunks with fewer than this many chars
        n_similar_docs=15,
        pdf=lr.parsing.PdfParsingConfig(
            # alternatives: "unstructured", "pdfplumber", "fitz"
            library="pdfplumber",
        ),
    )
    embed_cfg: lr.embedding_models.SentenceTransformerEmbeddingsConfig = (
        lr.embedding_models.SentenceTransformerEmbeddingsConfig(
            model_type="sentence-transformer",
            model_name="BAAI/bge-large-en-v1.5"
        )
    )

    vecdb: lr.vector_store.QdrantDBConfig = lr.vector_store.QdrantDBConfig(
        collection_name="intellilang",
        replace_collection=False,
        cloud=True,
        #storage_path=".qdrant/data/",
        embedding=embed_cfg,
    )

    # vecdb: lr.vector_store.LanceDBConfig = lr.vector_store.LanceDBConfig(
    #     collection_name="intellilang",
    #     replace_collection=False,
    #     storage_path=".lancedb/data/",
    #     embedding=embed_cfg,
    # )


class RagAgent(lr.agent.special.DocChatAgent):
    def __init__(self, config: RagAgentConfig):
        super().__init__(config)
        self.config: RagAgentConfig = config

