
import json

from app.models.insight import Insight
from app.services.llm_service import generate_text



class GeminiInsightService:
    """Service for generating impact and recommendations for insights using Gemini."""

    def generate_insight_analysis(self, insight: Insight) -> Insight:
        """
        Generate impact and recommendation for an insight using Gemini.

        Args:
            insight: Insight object containing issue, evidence, and severity

        Returns:
            Updated Insight object with impact and recommendation fields populated
        """
        prompt = self._build_prompt(insight)
        response_text = generate_text(prompt)
        analysis = self._parse_response(response_text)

        # Update insight with generated values
        insight.impact = analysis.get("impact", "")
        insight.recommendation = analysis.get("recommendation", "")

        return insight

    def _build_prompt(self, insight: Insight) -> str:
        """Build a structured prompt for insight analysis."""
        evidence_text = "\n".join(
            [f"- {item}" for item in insight.evidence]
        )

        prompt = f"""You are an operations analyst specializing in identifying business impacts and actionable recommendations.

Analyze the following operational insight and provide structured analysis:

ISSUE:
{insight.issue}

SEVERITY: {insight.severity}

EVIDENCE:
{evidence_text}

---

Based on the issue, severity level, and evidence provided, generate:

1. IMPACT: A concise description (2-3 sentences) of the potential business impact if this issue is not addressed. Consider operational, financial, and strategic implications.

2. RECOMMENDATION: A clear, actionable recommendation (2-3 sentences) for addressing this issue. Be specific and practical.

Respond ONLY with valid JSON in this exact format, no additional text:
{{
    "impact": "description of business impact",
    "recommendation": "actionable recommendation"
}}"""

        return prompt

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse the JSON response from Gemini.

        Args:
            response_text: Raw text response from Gemini

        Returns:
            Dictionary with 'impact' and 'recommendation' keys
        """
        try:
            # Try to extract JSON from the response
            # Handle cases where the response might have extra text
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return {
                    "impact": response_text,
                    "recommendation": "Please review the issue manually."
                }
        except json.JSONDecodeError:
            return {
                "impact": response_text,
                "recommendation": "Please review the issue manually."
            }


def generate_insight_analysis(insight: Insight) -> Insight:
    """
    Convenience function to generate insight analysis.

    Args:
        insight: Insight object to analyze

    Returns:
        Updated Insight object with impact and recommendation
    """
    service = GeminiInsightService()
    return service.generate_insight_analysis(insight)
