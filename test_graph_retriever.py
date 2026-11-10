import json
from backend.services.graph_retriever import LegalGraphRetriever

def run_tests():
    print("Initializing LegalGraphRetriever...")
    retriever = LegalGraphRetriever()
    print(f"Loaded {len(retriever.nodes)} graph nodes and {sum(len(v) for v in retriever.adj.values())} directed edges.")

    test_queries = [
        ("Street Vendor Eviction", "Police is breaking my thela in Lajpat Nagar and asking 500 rupees bribe."),
        ("Predatory Loan Blackmail", "Loan app recovery agents are morphing my photos and calling my contacts."),
        ("Car Crash Collision", "A speeding truck hit my car at the highway crossing and fled."),
        ("RERA Builder Delay", "Builder has delayed flat possession by 2 years after taking 90% payment."),
        ("MSME Overdue Payment", "Corporate client has defaulted on precision parts invoice for 70 days.")
    ]

    for label, q in test_queries:
        print(f"\n=======================================================")
        print(f"TEST QUERY: [{label}]")
        print(f"Query: {q}")
        res = retriever.query(q)
        verdict = res["legality_verdict"]
        print(f"VERDICT: {verdict['status']} (Lawful: {verdict['is_lawful']})")
        print(f"Summary: {verdict['verdict_summary']}")
        print(f"Citizen Standing: {verdict['citizen_standing']}")
        print(f"Root Nodes: {[n['id'] for n in res['root_nodes']]}")
        print(f"Graph Subgraph Nodes Pulled ({len(res['statutory_sections'])} statutory provisions):")
        for s in res['statutory_sections'][:4]:
            print(f"  • {s['law']}")
            
        assert len(res["root_nodes"]) > 0, "Expected at least 1 root node"
        assert len(res["statutory_sections"]) > 0, "Expected traversed statutory sections"
        assert verdict["is_lawful"] is False, "Expected unlawful verdict for violation query"

    print("\n ALL GRAPH RETRIEVER TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_tests()
