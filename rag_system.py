"""
RAG (Retrieval-Augmented Generation) system for PawPal+
"""
import os
from typing import Optional
import chromadb
from pet_knowledge_base import PET_CARE_DOCUMENTS


class VectorDatabaseManager:
    """Manages the vector database of pet care knowledge."""

    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None

    def initialize_knowledge_base(self) -> None:
        """Load pet care documents into the vector database."""
        self.collection = self.client.get_or_create_collection(
            name="pet_care_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

        ids = []
        documents = []
        metadatas = []

        for doc in PET_CARE_DOCUMENTS:
            ids.append(doc["id"])
            documents.append(doc["content"])
            metadatas.append({
                "category": doc.get("category", "general"),
                "species": doc.get("species", "all"),
                "breed": doc.get("breed", "general"),
            })

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"✅ Loaded {len(ids)} documents into vector database")

    def search(
        self,
        query: str,
        species: Optional[str] = None,
        top_k: int = 5
    ) -> list[dict]:
        """Search the knowledge base for relevant documents."""
        if self.collection is None:
            self.initialize_knowledge_base()

        where_filter = None
        if species:
            where_filter = {
                "$or": [
                    {"species": species},
                    {"species": "all"}
                ]
            }

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
        )

        formatted = []
        if results and results["documents"] and len(results["documents"]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                })

        return formatted

    def reset(self) -> None:
        """Clear the database (for testing)."""
        import shutil
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)
        self.collection = None
        print("✅ Vector database reset")


if __name__ == "__main__":
    db = VectorDatabaseManager()
    db.initialize_knowledge_base()

    results = db.search("How much exercise does my dog need?", species="dog", top_k=3)
    print("\n🔍 Search results:")
    for r in results:
        print(f"\n📄 {r['id']}")
        print(f"   Content: {r['content'][:200]}...")
