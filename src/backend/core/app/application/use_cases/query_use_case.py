"""Query use case — orchestrates the RAG pipeline."""

from __future__ import annotations

import uuid

from app.domain.models.citation import Citation
from app.domain.models.grounding import QueryResult
from app.domain.models.interaction import Interaction, InteractionStatus
from app.domain.ports.interaction_store_port import InteractionStorePort
from app.domain.ports.llm_port import LLMPort
from app.domain.ports.vectorstore_port import VectorStorePort
from app.domain.services.grounding_service import GroundingService

UNKNOWN_MESSAGE = "I don't have that information in the provided knowledge base."


class QueryUseCase:
    """Use case for querying the knowledge base with RAG pipeline."""

    def __init__(
        self,
        llm: LLMPort,
        vectorstore: VectorStorePort,
        interaction_store: InteractionStorePort,
        grounding_service: GroundingService,
    ) -> None:
        """Initialize the query use case.

        Args:
            llm: LLM provider port.
            vectorstore: Vector store port.
            interaction_store: Interaction store port.
            grounding_service: Grounding evaluation service.
        """
        self._llm = llm
        self._vectorstore = vectorstore
        self._interaction_store = interaction_store
        self._grounding_service = grounding_service

    async def execute(self, kb_id: str, question: str) -> QueryResult:
        """Execute the query against the knowledge base.

        Args:
            kb_id: Knowledge base ID to query.
            question: User question.

        Returns:
            Query result with answer or unknown status.
        """
        interaction_id = str(uuid.uuid4())

        # Step 1: Embed the question
        query_embedding = await self._llm.embed(question)

        # Step 2: Retrieve relevant chunks
        chunks = await self._vectorstore.search(query_embedding, kb_id)

        if not chunks:
            interaction = Interaction(
                id=interaction_id,
                kb_id=kb_id,
                question=question,
                answer=UNKNOWN_MESSAGE,
                status=InteractionStatus.UNKNOWN,
            )
            await self._interaction_store.save(interaction)
            return QueryResult(
                status="unknown",
                answer=UNKNOWN_MESSAGE,
                citations=[],
                interaction_id=interaction_id,
            )

        # Step 3: Generate answer with context
        context = "\n\n".join(f"[Chunk {c.id}]: {c.content}" for c in chunks)
        prompt = f"Answer the following question based ONLY on the provided context. If the context doesn't contain the answer, say so.\n\nContext:\n{context}\n\nQuestion: {question}"
        answer = await self._llm.generate(prompt, context)

        # Step 4: Evaluate grounding
        grounding = self._grounding_service.evaluate(question, answer, chunks)

        if not grounding.is_grounded:
            interaction = Interaction(
                id=interaction_id,
                kb_id=kb_id,
                question=question,
                answer=UNKNOWN_MESSAGE,
                status=InteractionStatus.UNKNOWN,
            )
            await self._interaction_store.save(interaction)
            return QueryResult(
                status="unknown",
                answer=UNKNOWN_MESSAGE,
                citations=[],
                interaction_id=interaction_id,
            )

        # Step 5: Build citations from supporting chunks
        citations = [
            Citation(
                source_document=c.metadata.get("source_document", ""),
                page=c.metadata.get("page"),
                chunk_id=c.id,
                relevance_score=0.0,
            )
            for c in chunks
            if c.id in grounding.supporting_chunks
        ]

        # Step 6: Save interaction
        interaction = Interaction(
            id=interaction_id,
            kb_id=kb_id,
            question=question,
            answer=answer,
            status=InteractionStatus.ANSWERED,
            citations=citations,
        )
        await self._interaction_store.save(interaction)

        return QueryResult(
            status="answered",
            answer=answer,
            citations=citations,
            interaction_id=interaction_id,
        )
