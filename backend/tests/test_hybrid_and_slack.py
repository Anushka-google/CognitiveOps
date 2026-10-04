import pytest
from app.services.hybrid_search_service import BM25Retriever, HybridSearchService
from app.services.slack_service import SlackService


def test_bm25_retriever():
    """Verify BM25 sparse keyword ranking matches exact terms correctly."""
    corpus = [
        "KAN-101 deployment is blocked because approval is pending in release pipeline.",
        "KAN-102 database migration finished with zero downtime.",
        "OPS-301 critical memory leak detected on payment microservice cluster."
    ]
    bm25 = BM25Retriever()
    bm25.index(documents=corpus)

    # Search for specific keyword
    results = bm25.search("blocked approval", top_k=2)
    assert len(results) > 0
    assert "KAN-101" in results[0]["document"]
    assert results[0]["score"] > 0

    # Search for unrelated/leak keyword
    results_leak = bm25.search("memory leak cluster", top_k=1)
    assert len(results_leak) > 0
    assert "OPS-301" in results_leak[0]["document"]


def test_query_rewriter_and_fusion():
    """Verify query expansion and Reciprocal Rank Fusion calculate valid scores."""
    hybrid = HybridSearchService()
    
    # 1. Query Expansion
    expanded = hybrid.rewrite_query("Why is the workflow blocked?")
    assert len(expanded) >= 2
    assert any("impediment" in q or "blocker" in q for q in expanded)

    # 2. Reciprocal Rank Fusion
    dense_candidates = [
        {"id": "doc1", "document": "SLA breach due to waiting time", "score": 0.9},
        {"id": "doc2", "document": "Jira ticket KAN-501 in progress", "score": 0.5}
    ]
    sparse_candidates = [
        {"id": "doc1", "document": "SLA breach due to waiting time", "score": 2.1},
        {"id": "doc3", "document": "Routine health check", "score": 0.3}
    ]
    fused = hybrid.reciprocal_rank_fusion(dense_candidates, sparse_candidates, top_k=3)
    assert len(fused) > 0
    # doc1 is ranked 1st in both dense & sparse, so it must lead the fusion
    assert fused[0]["id"] == "doc1"
    assert "rrf_score" in fused[0]


def test_slack_service_incident_card():
    """Verify Slack Block Kit alert formatting and status checking."""
    slack = SlackService()
    
    # Status check
    status = slack.get_status()
    assert isinstance(status, dict)
    assert "configured" in status

    # Incident Card simulation
    alert_res = slack.send_incident_card(
        ticket_id="KAN-999",
        title="CI/CD Build Failure",
        status="Blocked",
        priority="Critical",
        impact_summary="Master branch build blocked on Docker engine timeout."
    )
    assert alert_res["ticket_id"] == "KAN-999"
    assert alert_res["status"] in ["delivered", "simulated"]
