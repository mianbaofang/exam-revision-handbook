"""OpenAI provider implementation for concept explanation generation."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from intl_exam_guide.llm.provider import (
    ConceptExplanation,
    ConceptJob,
    CostLimitExceededError,
)

logger = logging.getLogger(__name__)

# System prompt for the LLM
SYSTEM_PROMPT = "You are an A-Level/IGCSE study guide writer."

# GPT-4 pricing (USD per 1K tokens)
COST_PER_1K_PROMPT = 0.03
COST_PER_1K_COMPLETION = 0.06


class OpenAIProvider:
    """OpenAI-based LLM provider for concept explanations."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        max_retries: int = 3,
        timeout: int = 30,
        cost_limit_usd: float = 5.0,
    ):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            cost_limit_usd: Maximum cost limit in USD
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self.cost_limit = cost_limit_usd
        self.total_cost = 0.0

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _generate_single(self, job: ConceptJob) -> ConceptExplanation:
        """
        Generate a single concept explanation.

        Args:
            job: Concept generation task

        Returns:
            Generated concept explanation

        Raises:
            CostLimitExceededError: If cost limit is exceeded
        """
        if self.total_cost >= self.cost_limit:
            raise CostLimitExceededError(
                estimated_cost=self.total_cost,
                cost_limit=self.cost_limit,
                job_count=1,
            )

        prompt = self._build_prompt(job)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
                timeout=self.timeout,
            )

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from API")

            parsed = self._parse_response(content)

            # Track cost
            if response.usage:
                cost = self._calculate_cost(response.usage)
                self.total_cost += cost
            else:
                cost = 0.0

            return ConceptExplanation(
                concept_term=job.concept_term,
                explanation=parsed.get("explanation", ""),
                analogy=parsed.get("analogy"),
                example=parsed.get("example"),
                common_misconception=parsed.get("misconception"),
                status="generated",
                metadata={
                    "model": self.model,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                    "cost_usd": cost,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to generate explanation for {job.concept_term}: {e}")
            raise

    def generate_concept_explanations(
        self, jobs: list[ConceptJob], max_concurrency: int = 5
    ) -> list[ConceptExplanation]:
        """
        Generate concept explanations for multiple jobs concurrently.

        Args:
            jobs: List of concept generation tasks
            max_concurrency: Maximum number of concurrent API calls

        Returns:
            List of concept explanations
        """

        async def _run() -> list[ConceptExplanation]:
            semaphore = asyncio.Semaphore(max_concurrency)

            async def _generate_with_semaphore(job: ConceptJob) -> ConceptExplanation:
                async with semaphore:
                    try:
                        return await self._generate_single(job)
                    except CostLimitExceededError as e:
                        logger.warning(
                            f"Cost limit exceeded, stopping generation for {job.concept_term}"
                        )
                        return ConceptExplanation(
                            concept_term=job.concept_term,
                            explanation="",
                            status="failed",
                            metadata={"error": str(e)},
                        )
                    except Exception as e:
                        logger.error(f"Failed to generate {job.concept_term}: {e}")
                        return ConceptExplanation(
                            concept_term=job.concept_term,
                            explanation="",
                            status="failed",
                            metadata={"error": str(e)},
                        )

            return await asyncio.gather(*[_generate_with_semaphore(job) for job in jobs])

        return asyncio.run(_run())

    def estimate_cost(self, jobs: list[ConceptJob]) -> float:
        """
        Estimate the cost for generating explanations.

        This is a rough estimate based on average token usage.

        Args:
            jobs: List of concept generation tasks

        Returns:
            Estimated cost in USD
        """
        # Rough estimate: ~500 prompt tokens + ~600 completion tokens per job
        estimated_prompt_tokens = len(jobs) * 500
        estimated_completion_tokens = len(jobs) * 600

        prompt_cost = (estimated_prompt_tokens / 1000) * COST_PER_1K_PROMPT
        completion_cost = (estimated_completion_tokens / 1000) * COST_PER_1K_COMPLETION

        return prompt_cost + completion_cost

    def _build_prompt(self, job: ConceptJob) -> str:
        """
        Build the prompt for concept explanation generation.

        Args:
            job: Concept generation task

        Returns:
            Formatted prompt string
        """
        return f"""For {job.level} {job.subject} students studying:

Topic: {job.topic_title}
Concept to explain: {job.concept_term}

Context from syllabus:
{job.context_snippet}

Please provide:
1. A clear, concise explanation (2-3 sentences)
2. An analogy or metaphor to aid understanding
3. A concrete example
4. One common misconception students have

Format your response as JSON:
{{"explanation": "...", "analogy": "...", "example": "...", "misconception": "..."}}
"""

    def _parse_response(self, content: str) -> dict[str, Any]:
        """
        Parse LLM response, handling markdown code blocks.

        Args:
            content: Raw response content from LLM

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If response cannot be parsed as JSON
        """
        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())

    def _calculate_cost(self, usage: Any) -> float:
        """
        Calculate cost based on token usage.

        Args:
            usage: OpenAI usage object with token counts

        Returns:
            Cost in USD
        """
        prompt_cost = (usage.prompt_tokens / 1000) * COST_PER_1K_PROMPT
        completion_cost = (usage.completion_tokens / 1000) * COST_PER_1K_COMPLETION

        return prompt_cost + completion_cost

    def reset_cost_tracking(self) -> None:
        """Reset the total cost counter."""
        self.total_cost = 0.0

    def get_total_cost(self) -> float:
        """Get the current total cost."""
        return self.total_cost
