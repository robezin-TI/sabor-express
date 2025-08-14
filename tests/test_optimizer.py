from src.backend.optimizer import Point, optimize

def test_optimize_basic():
    pts = [
        Point("A",-23.7168,-46.8492),
        Point("B",-23.7066,-46.8451),
        Point("C",-23.7015,-46.8335),
        Point("D",-23.7189,-46.8412),
    ]
    res = optimize(pts, k_clusters=2)
    assert "clusters" in res and len(res["clusters"]) == 2
    assert res["total_km"] > 0
    assert res["total_eta_min"] > 0
