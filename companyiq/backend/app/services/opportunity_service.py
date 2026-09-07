"""
Opportunity Scoring Engine — explainable weighted scoring system.
Never depends entirely on LLM for opportunity ranking.
"""
from typing import List, Dict, Any, Optional
from app.config import settings
from app.schemas.schemas import OpportunityScoreBreakdown
from app.utils.logger import get_logger

logger = get_logger("opportunity_scorer")

SCORE_THRESHOLDS = {
    "HIGH": 80.0,
    "MEDIUM": 60.0,
    "LOW": 40.0,
}


def classify_score(score: float) -> str:
    if score >= SCORE_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif score >= SCORE_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    elif score >= SCORE_THRESHOLDS["LOW"]:
        return "LOW"
    return "VERY_LOW"


class OpportunityScorer:
    """
    Explainable opportunity scorer.
    Weights are configurable via environment variables.

    Score = 30% Business Relevance
          + 25% Recent Activity
          + 20% Product Fit
          + 15% Historical Similarity
          + 10% Evidence Confidence
    """

    def __init__(self):
        self.weights = {
            "business_relevance": settings.score_weight_business_relevance,
            "recent_activity": settings.score_weight_recent_activity,
            "product_fit": settings.score_weight_product_fit,
            "historical_similarity": settings.score_weight_historical_similarity,
            "evidence_confidence": settings.score_weight_evidence_confidence,
        }

    def score(
        self,
        company_profile: Dict[str, Any],
        opportunity_data: Dict[str, Any],
        retrieved_chunks: List[Any],
        product_context: Optional[str] = None,
        historical_outcomes: Optional[List[Dict]] = None,
    ) -> OpportunityScoreBreakdown:
        """Compute all five sub-scores and the weighted overall score."""

        br = self._score_business_relevance(company_profile, opportunity_data)
        ra = self._score_recent_activity(company_profile, retrieved_chunks)
        pf = self._score_product_fit(opportunity_data, product_context)
        hs = self._score_historical_similarity(company_profile, historical_outcomes)
        ec = self._score_evidence_confidence(retrieved_chunks, opportunity_data)

        overall = (
            br * self.weights["business_relevance"]
            + ra * self.weights["recent_activity"]
            + pf * self.weights["product_fit"]
            + hs * self.weights["historical_similarity"]
            + ec * self.weights["evidence_confidence"]
        )

        logger.info(
            "opportunity_scored",
            title=opportunity_data.get("title", ""),
            overall=round(overall, 1),
            level=classify_score(overall),
        )

        return OpportunityScoreBreakdown(
            business_relevance=round(br, 1),
            recent_activity=round(ra, 1),
            product_fit=round(pf, 1),
            historical_similarity=round(hs, 1),
            evidence_confidence=round(ec, 1),
            overall=round(overall, 1),
            level=classify_score(overall),
        )

    def _score_business_relevance(self, profile: Dict, opp: Dict) -> float:
        """How aligned is the opportunity with the company's industry and strategic priorities?"""
        score = 50.0
        industry = (profile.get("industry") or "").lower()
        priorities = " ".join(profile.get("strategic_priorities") or []).lower()
        opp_text = (f"{opp.get('title', '')} {opp.get('description', '')} {opp.get('why', '')}").lower()

        # Industry match keywords
        ev_keywords = ["ev", "electric vehicle", "battery", "electr"]
        tech_keywords = ["ai", "analytics", "data", "digital", "platform", "software"]
        relevance_keywords = ev_keywords + tech_keywords

        matches = sum(1 for kw in relevance_keywords if kw in opp_text or kw in priorities)
        score += min(matches * 8, 40)

        if any(kw in industry for kw in ["automotive", "ev", "energy", "logistics"]):
            score += 10

        return min(score, 100.0)

    def _score_recent_activity(self, profile: Dict, chunks: List[Any]) -> float:
        """Are there recent signals of investment or change in this area?"""
        base = 40.0
        recent_events = profile.get("recent_developments") or profile.get("recent_events") or []
        signals = profile.get("business_signals") or []

        ev_activity = sum(1 for e in recent_events if any(kw in str(e).lower() for kw in ["ev", "battery", "invest", "partner", "launch"]))
        base += min(ev_activity * 12, 36)

        high_signal_chunks = [c for c in chunks if getattr(c, "score", 0) > 0.75]
        base += min(len(high_signal_chunks) * 3, 24)

        return min(base, 100.0)

    def _score_product_fit(self, opp: Dict, product_context: Optional[str]) -> float:
        """How well does our product fit the identified opportunity?"""
        base = 60.0
        if not product_context:
            return base

        opp_text = (f"{opp.get('title', '')} {opp.get('what', '')} {opp.get('description', '')}").lower()
        product_lower = product_context.lower()

        fit_keywords = ["analytics", "predictive", "monitoring", "battery", "fleet", "data", "ai", "platform"]
        matches = sum(1 for kw in fit_keywords if kw in opp_text and kw in product_lower)
        base += min(matches * 10, 40)

        return min(base, 100.0)

    def _score_historical_similarity(self, profile: Dict, outcomes: Optional[List[Dict]]) -> float:
        """Are there similar past deals in similar companies?"""
        if not outcomes:
            return 55.0  # neutral when no historical data

        industry = (profile.get("industry") or "").lower()
        similar = [o for o in outcomes if (o.get("industry") or "").lower() in industry or industry in (o.get("industry") or "").lower()]
        won = [o for o in similar if o.get("outcome") == "won"]

        if not similar:
            return 50.0
        win_rate = len(won) / len(similar)
        return min(40 + win_rate * 60, 100.0)

    def _score_evidence_confidence(self, chunks: List[Any], opp: Dict) -> float:
        """How much evidence supports this opportunity?"""
        evidence = opp.get("evidence") or []
        n_evidence = len(evidence)

        if n_evidence == 0:
            return 20.0

        avg_relevance = sum(e.get("relevance_score", 0.5) if isinstance(e, dict) else 0.5 for e in evidence) / max(n_evidence, 1)
        high_confidence_chunks = [c for c in chunks if getattr(c, "score", 0) > 0.70]

        base = min(n_evidence * 15, 60)
        base += avg_relevance * 25
        base += min(len(high_confidence_chunks) * 3, 15)
        return min(base, 100.0)
