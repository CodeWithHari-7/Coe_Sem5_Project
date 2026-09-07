"""
LLM Provider Abstraction Layer.
Swap OpenAI / Gemini / Local via LLM_PROVIDER env var.
Never hard-code API keys or provider specifics outside this module.
"""
from __future__ import annotations
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("llm")


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        response_format: Optional[str] = None,  # "json_object"
    ) -> str:
        """Return raw string completion."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return list of embedding vectors."""

    def complete_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> Optional[Dict[str, Any]]:
        """Complete and parse JSON response. Returns None on parse failure."""
        raw = self.complete(messages, temperature, max_tokens, response_format="json_object")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            logger.error("json_parse_failed", raw_sample=raw[:200])
            return None


class OpenAIProvider(LLMProvider):
    def __init__(self):
        import openai
        self.client = openai.OpenAI(api_key=settings.llm_api_key)
        self.model = settings.model_name
        self.embedding_model = settings.embedding_model
        self._demo_fallback = DemoProvider()

    def complete(self, messages, temperature=0.2, max_tokens=4096, response_format=None):
        start = time.time()
        kwargs = dict(model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens)
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}
        try:
            resp = self.client.chat.completions.create(**kwargs)
            latency = (time.time() - start) * 1000
            logger.info("llm_call", model=self.model, latency_ms=round(latency, 1), tokens=resp.usage.total_tokens)
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning("openai_complete_failed_falling_back_to_demo", error=str(e))
            return self._demo_fallback.complete(messages, temperature, max_tokens, response_format)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            resp = self.client.embeddings.create(model=self.embedding_model, input=texts)
            return [item.embedding for item in resp.data]
        except Exception as e:
            logger.warning("openai_embed_failed_falling_back_to_demo", error=str(e))
            return self._demo_fallback.embed(texts)


class GeminiProvider(LLMProvider):
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.llm_api_key)
        self.model = genai.GenerativeModel(settings.model_name)
        self.genai = genai
        self._demo_fallback = DemoProvider()

    def complete(self, messages, temperature=0.2, max_tokens=4096, response_format=None):
        prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
        try:
            resp = self.model.generate_content(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=temperature, max_output_tokens=max_tokens
                ),
            )
            return resp.text
        except Exception as e:
            logger.warning("gemini_complete_failed_falling_back_to_demo", error=str(e))
            return self._demo_fallback.complete(messages, temperature, max_tokens, response_format)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            results = []
            for text in texts:
                resp = self.genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document",
                )
                results.append(resp["embedding"])
            return results
        except Exception as e:
            logger.warning("gemini_embed_failed_falling_back_to_demo", error=str(e))
            return self._demo_fallback.embed(texts)


class DemoProvider(LLMProvider):
    """
    Demo provider — returns pre-crafted synthetic responses.
    Used when DEMO_MODE=true or no valid API key is configured.
    All responses are clearly labeled [DEMO DATA].
    """

    def complete(self, messages, temperature=0.2, max_tokens=4096, response_format=None):
        logger.info("demo_llm_call", note="Using demo provider — no real LLM call made")
        user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return self._generate_demo_response(user_msg, response_format)

    def embed(self, texts: List[str]) -> List[List[float]]:
        import hashlib, math
        results = []
        for text in texts:
            # Deterministic pseudo-embeddings for demo — NOT real embeddings
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            vec = [(math.sin(h * (i + 1)) + 1) / 2 for i in range(384)]
            norm = math.sqrt(sum(x**2 for x in vec)) or 1
            results.append([x / norm for x in vec])
        return results

    def _generate_demo_response(self, user_msg: str, response_format: Optional[str]) -> str:
        from app.agents.demo_data import DEMO_COMPANY_INTELLIGENCE
        if response_format == "json_object":
            return json.dumps(DEMO_COMPANY_INTELLIGENCE)

        return (
            "Based on company research and market signals, key strategic opportunities include: "
            "\n1. **Battery Predictive Analytics Platform** — AI-powered cell health monitoring and warranty cost reduction."
            "\n2. **Fleet EV Data Intelligence** — Fleet route optimization, charging scheduling, and TCO management."
            "\n3. **Connected Vehicle Telemetry Platform** — Monetizable vehicle data marketplace and OTA updates."
            "\n\nExplore the interactive intelligence panels for detailed score breakdowns and evidence attribution."
        )


def get_llm_provider() -> LLMProvider:
    """Factory — returns the configured LLM provider."""
    if settings.demo_mode or not settings.llm_api_key or settings.llm_api_key == "your-openai-api-key-here":
        logger.info("llm_provider_selected", provider="demo")
        return DemoProvider()

    provider = settings.llm_provider.lower()
    try:
        if provider == "openai":
            logger.info("llm_provider_selected", provider="openai", model=settings.model_name)
            return OpenAIProvider()
        elif provider == "gemini":
            logger.info("llm_provider_selected", provider="gemini", model=settings.model_name)
            return GeminiProvider()
        else:
            logger.warning("unknown_provider_fallback", provider=provider)
            return DemoProvider()
    except Exception as e:
        logger.error("llm_provider_init_failed", error=str(e), fallback="demo")
        return DemoProvider()
