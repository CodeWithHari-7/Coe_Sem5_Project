"""
Evaluation module — baseline vs. AI+RAG comparison.
Metrics: precision, recall, F1, acceptance rate, response time, evidence coverage, failure rate.
All synthetic evaluation data is clearly labeled.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.agents.demo_data import DEMO_COMPANY_INTELLIGENCE
from app.utils.logger import get_logger

logger = get_logger("evaluation")


class BaselineRecommender:
    """
    Rule-based baseline recommendation system.
    IF industry matches product AND recent activity exists THEN recommend.
    Used as baseline comparison for AI+RAG system.
    """

    INDUSTRY_OPPORTUNITY_MAP = {
        "automotive": ["Fleet Management", "Predictive Maintenance", "Supply Chain Analytics"],
        "ev": ["Battery Analytics", "Charging Infrastructure", "Fleet Intelligence"],
        "banking": ["Fraud Detection", "Customer Analytics", "Risk Management"],
        "healthcare": ["Patient Analytics", "Claims Processing", "Clinical Decision Support"],
        "retail": ["Demand Forecasting", "Customer Segmentation", "Inventory Optimization"],
        "logistics": ["Route Optimization", "Fleet Tracking", "Warehouse Automation"],
        "saas": ["Customer Success Analytics", "Product Usage Intelligence", "Churn Prediction"],
        "energy": ["Grid Analytics", "Predictive Maintenance", "Energy Optimization"],
    }

    def recommend(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate rule-based recommendations."""
        industry = (company.get("industry") or "").lower()
        recent_events = company.get("recent_events") or []
        has_recent_activity = len(recent_events) > 0

        opportunities = []
        for key, opps in self.INDUSTRY_OPPORTUNITY_MAP.items():
            if key in industry:
                for opp in opps:
                    score = 60.0 if has_recent_activity else 40.0
                    opportunities.append({
                        "title": opp,
                        "score": score,
                        "level": "MEDIUM" if score >= 60 else "LOW",
                        "basis": "rule_based",
                        "rule": f"industry={key}, recent_activity={has_recent_activity}",
                    })

        return opportunities[:3]  # top 3 rule-based


class Evaluator:
    """Compute evaluation metrics for baseline vs. AI+RAG."""

    def get_demo_evaluation(self) -> Dict[str, Any]:
        """Return synthetic evaluation report — clearly labeled."""
        return DEMO_COMPANY_INTELLIGENCE["evaluation"]

    def compute_metrics(
        self,
        recommendations: List[Dict],
        ground_truth: List[Dict],
        response_times: List[float],
        failures: int,
        total_requests: int,
    ) -> Dict[str, float]:
        """
        Compute precision, recall, F1, etc. from actual data.
        Returns empty dict if insufficient data.
        """
        if not recommendations or not ground_truth:
            logger.warning("insufficient_data_for_evaluation")
            return {}

        rec_titles = set(r.get("title", "").lower() for r in recommendations)
        gt_titles = set(g.get("title", "").lower() for g in ground_truth)

        tp = len(rec_titles & gt_titles)
        fp = len(rec_titles - gt_titles)
        fn = len(gt_titles - rec_titles)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        avg_rt = sum(response_times) / len(response_times) if response_times else 0.0
        failure_rate = failures / total_requests if total_requests > 0 else 0.0

        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "avg_response_time_ms": round(avg_rt, 1),
            "failure_rate": round(failure_rate, 3),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
        }

    def compute_improvement(self, baseline: Dict, ai_rag: Dict) -> Dict[str, float]:
        """Compute percentage improvement of AI+RAG over baseline."""
        improvements = {}
        for key in ["precision", "recall", "f1_score", "acceptance_rate", "evidence_coverage"]:
            b = baseline.get(key, 0)
            a = ai_rag.get(key, 0)
            if b > 0:
                improvements[key] = round((a - b) / b * 100, 1)
        # Failure rate — lower is better
        b_fail = baseline.get("failure_rate", 0)
        a_fail = ai_rag.get("failure_rate", 0)
        if b_fail > 0:
            improvements["failure_rate"] = round((b_fail - a_fail) / b_fail * 100, 1)
        return improvements
