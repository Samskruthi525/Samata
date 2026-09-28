"""heritage_core — reference implementation of the archive's trust-critical rules.

Pure Python 3.10+, standard library only. These modules are the executable
specification for the rules the README describes (rights gate, hybrid
retrieval, the RAG answer contract, offline-manifest handling, the kiosk
visitor state machine and evaluation metrics). Production services
(FastAPI + PostgreSQL/pgvector) must reproduce the same behaviour and are
expected to re-use these test vectors.
"""
__version__ = "0.1.0"
