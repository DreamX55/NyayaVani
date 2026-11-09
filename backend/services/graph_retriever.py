import os
import json
import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

class LegalGraphRetriever:
    """
    Hybrid GraphRAG retriever over sovereign Indian legal statutes.
    Combines:
    1. Lexical BM25 matching (exact section numbers, statutory keywords, Hinglish terms)
    2. Dense Semantic Vector Search (cached all-MiniLM-L6-v2)
    3. Reciprocal Rank Fusion (RRF)
    4. Multi-hop Directed Graph Traversal (Penal, Procedural, Constitutional, Evidentiary)
    5. Upfront Citizen Legality Verdict Generation
    """
    def __init__(self, graph_path: Optional[str] = None):
        if graph_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            graph_path = os.path.join(base_dir, "data", "legal_knowledge_graph.json")

        self.graph_path = graph_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.rev_adj: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        
        self.embed_model = None
        self.node_embeddings = None
        self.node_ids = []
        
        self.load_graph()
        self.init_embeddings()

    def load_graph(self):
        if not os.path.exists(self.graph_path):
            raise FileNotFoundError(f"Knowledge Graph file not found: {self.graph_path}")
        
        with open(self.graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for n in data.get("nodes", []):
            self.nodes[n["id"]] = n
            self.node_ids.append(n["id"])
            
        for e in data.get("edges", []):
            src = e["source"]
            tgt = e["target"]
            rel = e["relation"]
            meaning = e.get("meaning", "")
            self.adj[src].append({"target": tgt, "relation": rel, "meaning": meaning})
            self.rev_adj[tgt].append({"source": src, "relation": rel, "meaning": meaning})

    def init_embeddings(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            corpus = []
            for nid in self.node_ids:
                n = self.nodes[nid]
                text = f"{n.get('act', '')} {n.get('section', '')} {n.get('title', '')} {n.get('operative_text', '')} {' '.join(n.get('keywords', []))}"
                corpus.append(text)
            self.node_embeddings = self.embed_model.encode(corpus, convert_to_numpy=True, normalize_embeddings=True)
        except Exception as e:
            print(f"Warning: Dense embeddings fallback to lexical: {e}")
            self.embed_model = None

    def bm25_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Token-level BM25 scoring over node metadata with native Indic script support.
        """
        import re
        clean_q = re.sub(r'[^\w\s]', ' ', query.lower().replace("§", "section"))
        tokens = clean_q.split()
        scores = {}
        
        for nid in self.node_ids:
            n = self.nodes[nid]
            kw_str = " ".join(n.get("keywords", [])).lower()
            doc_str = f"{n.get('act', '')} {n.get('section', '')} {n.get('title', '')} {n.get('operative_text', '')} {kw_str}".lower()
            score = 0.0
            kw_list = [k.lower() for k in n.get("keywords", [])]
            for t in tokens:
                if len(t) < 2:
                    continue
                # Term match weight
                if t in doc_str:
                    freq = doc_str.count(t)
                    kw_boost = 3.5 if t in kw_str else 1.0
                    score += math.log(1 + freq) * (2.5 if t.isdigit() or t in ["fir", "tvc", "rera", "mact", "bns", "bnss", "bsa"] else 1.0) * kw_boost
                elif len(t) >= 4:
                    # Indic agglutinative stem match (e.g. બિલ્ડરે -> બિલ્ડર, कंत्राटदाराने -> कंत्राटदार)
                    for kw in kw_list:
                        if len(kw) >= 3 and (kw in t or t in kw):
                            score += 3.0
                            break
            
            # Boost exact section hits
            for t in tokens:
                sec = n.get("section", "").lower()
                if t in sec and len(t) > 2:
                    score += 5.0
                    
            if score > 0:
                scores[nid] = score
            
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def dense_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.embed_model is None or self.node_embeddings is None:
            return []
        q_emb = self.embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        sims = np.dot(self.node_embeddings, q_emb)
        ranked_indices = np.argsort(-sims)[:top_k]
        return [(self.node_ids[idx], float(sims[idx])) for idx in ranked_indices]

    def hybrid_retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Reciprocal Rank Fusion (RRF) combining BM25 and Dense vector rankings.
        Adapts dynamically when queries contain native Indic scripts.
        """
        import re
        is_indic = bool(re.search(r'[\u0900-\u0DFF]', query))
        bm25_ranks = self.bm25_search(query, top_k=8)
        dense_ranks = self.dense_search(query, top_k=8)
        
        rrf_scores = defaultdict(float)
        k = 60.0
        
        # When BM25 finds strong keyword hits, especially in Indic dialects, weight BM25 heavily
        bm25_multiplier = 3.0 if (is_indic and bm25_ranks) else 1.5
        for rank, (nid, score) in enumerate(bm25_ranks):
            rrf_scores[nid] += (1.0 / (k + rank + 1)) * bm25_multiplier
            
        # Add dense representations (effective for English/code-switched queries)
        dense_multiplier = 0.5 if (is_indic and bm25_ranks) else 1.0
        for rank, (nid, score) in enumerate(dense_ranks):
            rrf_scores[nid] += (1.0 / (k + rank + 1)) * dense_multiplier
            
        sorted_nodes = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [nid for nid, _ in sorted_nodes[:top_k]]

    def traverse_subgraph(self, root_node_ids: List[str], max_hops: int = 2) -> Dict[str, Any]:
        """
        Extracts 1-hop and 2-hop connected graph components from matching root nodes.
        Pulls related Penal, Procedural, Constitutional, and Evidentiary nodes automatically.
        """
        visited_nodes = set(root_node_ids)
        visited_edges = []
        frontier = list(root_node_ids)
        
        for _ in range(max_hops):
            next_frontier = []
            for curr in frontier:
                # Outbound edges
                for edge in self.adj.get(curr, []):
                    tgt = edge["target"]
                    visited_edges.append({
                        "source": curr,
                        "target": tgt,
                        "relation": edge["relation"],
                        "meaning": edge["meaning"]
                    })
                    if tgt not in visited_nodes:
                        visited_nodes.add(tgt)
                        next_frontier.append(tgt)
                
                # Inbound edges
                for edge in self.rev_adj.get(curr, []):
                    src = edge["source"]
                    visited_edges.append({
                        "source": src,
                        "target": curr,
                        "relation": edge["relation"],
                        "meaning": edge["meaning"]
                    })
                    if src not in visited_nodes:
                        visited_nodes.add(src)
                        next_frontier.append(src)
            frontier = next_frontier

        # Categorize assembled graph nodes
        statutory_protections = []
        penal_offenses = []
        procedural_mandates = []
        constitutional_anchors = []
        evidence_protocols = []

        for nid in visited_nodes:
            n = self.nodes.get(nid)
            if not n:
                continue
            ntype = n.get("type")
            if ntype in ["STATUTE_PROTECTION", "REGULATORY_SHIELD"]:
                statutory_protections.append(n)
            elif ntype == "PENAL_OFFENSE":
                penal_offenses.append(n)
            elif ntype == "PROCEDURAL_MANDATE":
                procedural_mandates.append(n)
            elif ntype == "CONSTITUTIONAL_RIGHT":
                constitutional_anchors.append(n)
            elif ntype == "EVIDENCE_PROTOCOL":
                evidence_protocols.append(n)

        return {
            "root_nodes": [self.nodes[r] for r in root_node_ids if r in self.nodes],
            "statutory_protections": statutory_protections,
            "penal_offenses": penal_offenses,
            "procedural_mandates": procedural_mandates,
            "constitutional_anchors": constitutional_anchors,
            "evidence_protocols": evidence_protocols,
            "relations": visited_edges
        }

    def generate_legality_verdict(self, subgraph: Dict[str, Any], transcript: str) -> Dict[str, Any]:
        """
        Synthesizes an upfront Citizen Legality Verdict based on graph traversal.
        Explicitly answers: Is this legal/illegal? What is my legal standing? Who is liable?
        Also detects if Citizen is at Fault (Lawful Authority Power) or if facts are Ambiguous (Follow-up Required).
        """
        root_nodes = subgraph.get("root_nodes", [])
        penal = subgraph.get("penal_offenses", [])
        statutes = subgraph.get("statutory_protections", [])
        const = subgraph.get("constitutional_anchors", [])

        t_low = transcript.lower()

        # 1. Ambiguity & Missing Facts Detection (Mandatory Follow-Up Question Trigger)
        is_ambiguous = False
        follow_up_q = None
        follow_up_reason = None
        
        if any(term in t_low for term in ["[ambiguous]", "ambiguous_query", "need clarification", "incomplete facts"]) or (
            any(w in t_low for w in ["police stopped", "police aayi", "police boli", "police aakar", "दुकान बंद करने", "પોલીસે દુકાન", "ಪೊಲೀಸರು ಅಂಗಡಿ", "போலீஸ் கடை", "పోలీసులు దుకాణం", "পুলিশ দোকান", "ਪੁਲਿਸ ਦੁਕਾਨ", "പോലീസ് കട"])
            and not any(w in t_low for w in ["hafta", "bribe", "lanch", "ghoos", "500", "paisa", "rupiya", "paise", "rotten", "sada", "kharab", "fssai", "ambulance", "pakka", "emergency", "certificate", "slip", "vending"])
        ):
            is_ambiguous = True
            follow_up_q = "Did the authorities state a violation regarding food contamination/physical obstruction, or did they demand an unauthorized payment without issuing an official receipt?"
            follow_up_reason = "Missing factual basis for the authority intervention (distinguishes lawful FSSAI/obstruction clearance from criminal extortion)."

        elif any(w in t_low for w in ["deducted salary", "paisa kata", "salary cut", "wage cut", "pagar kapla", "sambala kadita", "vetan kata", "sambala piditham", "jeetam kota"]) and not any(w in t_low for w in ["contractor", "thekedar", "malik", "overtime", "unpaid 3 month", "3 mahina", "45000", "bina bataye", "dhamki", "threat"]):
            is_ambiguous = True
            follow_up_q = "What specific reason did your employer provide for the deduction, and was it a statutory deduction (PF/TDS) or an arbitrary withholding of earned wages?"
            follow_up_reason = "Missing grounds for wage deduction (distinguishes legitimate statutory deductions from illegal wage withholding under Section 15 Payment of Wages Act)."

        elif any(w in t_low for w in ["accident hua", "gadi thuk gayi", "collision on road", "car clash", "vahanam apaghata", "vahan tatkal", "gaadi lad gayi"]) and not any(w in t_low for w in ["injured", "hospital", "dead", "fracture", "rash", "speeding", "red light", "dashcam", "insurance claim", "mact"]):
            is_ambiguous = True
            follow_up_q = "Was any person bodily injured requiring immediate medical care under Section 134 MV Act, or was the damage limited strictly to vehicular property?"
            follow_up_reason = "Missing injury classification (determines whether Section 106 BNS criminal negligence and MACT bodily injury procedures apply)."

        elif any(w in t_low for w in ["repay loan", "loan call", "recovery notice", "paisa wapas", "kist bharo", "loan recovery"]) and not any(w in t_low for w in ["morph", "contacts", "relatives", "photos", "blackmail", "npa", "sarfaesi", "60 days", "bank notice", "threat to kill"]):
            is_ambiguous = True
            follow_up_q = "Is this payment demand originating from an RBI-regulated bank with an official loan account number, or an unapproved mobile application accessing your personal contacts?"
            follow_up_reason = "Missing lender regulatory status (distinguishes lawful SARFAESI recovery from predatory cyber extortion under IT Act Section 66D)."

        if is_ambiguous:
            return {
                "is_lawful": None,
                "citizen_fault": None,
                "status": "INSUFFICIENT_FACTS",
                "follow_up_required": True,
                "follow_up_question": follow_up_q,
                "follow_up_reason": follow_up_reason,
                "verdict_summary": f"CLARIFICATION REQUIRED. {follow_up_q}",
                "citizen_standing": "Standing cannot be determined until factual qualifiers (licensing, grounds for action, or injury) are provided.",
                "violator_liability": "Pending clarification."
            }

        if not root_nodes:
            return {
                "is_lawful": None,
                "citizen_fault": None,
                "status": "INSUFFICIENT_FACTS",
                "follow_up_required": True,
                "follow_up_question": "Please provide additional details: what specific action was taken, who initiated it, and what statutory notices or receipts were provided?",
                "follow_up_reason": "No matched statutory nodes in Knowledge Graph.",
                "verdict_summary": "Further factual details required to determine exact statutory liability.",
                "citizen_standing": "Consult nearest Legal Services Authority (DLSA) or file an inquiry under BNSS Section 173.",
                "violator_liability": "Subject to formal verification of acts committed."
            }

        # Determine primary domain from the top matched root nodes
        primary_id = root_nodes[0]["id"]
        if "PROCEDURAL" in primary_id and len(root_nodes) > 1 and "PROCEDURAL" not in root_nodes[1]["id"]:
            primary_id = root_nodes[1]["id"]

        def matches_domain(prefix: str) -> bool:
            return prefix in primary_id

        # 2. Citizen At Fault / Lawful Authority Enforcement Handlers
        if matches_domain("FSSAI") or matches_domain("FOOD_SAFETY"):
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_REGULATORY_ENFORCEMENT",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "LAWFUL AUTHORITY ENFORCEMENT. Under Sections 26 and 59 of the Food Safety and Standards Act (FSSAI), 2006 and BNS Section 274, authorities have lawful jurisdiction to seize contaminated, rotten, or unhygienic food. You are legally at fault.",
                "citizen_standing": "You are in statutory violation. You DO NOT have the right to challenge lawful public health confiscation or obstruct inspecting officers. You must comply with food safety standards.",
                "violator_liability": "Citizen/vendor liable for statutory fines up to ₹5,00,000 under FSSAI and criminal prosecution under BNS Section 274."
            }
        elif matches_domain("MV_TRAFFIC_OFFENSES") or matches_domain("185"):
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_TRAFFIC_ENFORCEMENT",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "LAWFUL POLICE POWER. Traffic police possess lawful statutory authority under Section 207 of the Motor Vehicles Act, 1988 to impound vehicles and issue compounding challans for drunk driving (Section 185), helmetless riding, or dangerous wrong-side operation. You are legally at fault.",
                "citizen_standing": "You are legally in violation. The police have full authority to seize the vehicle. You must pay the statutory compounding fine or appear before the Metropolitan Magistrate.",
                "violator_liability": "Citizen liable for statutory challan and license suspension up to 3 months."
            }
        elif matches_domain("MUNICIPAL_OBSTRUCTION"):
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_MUNICIPAL_CLEARANCE",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "LAWFUL MUNICIPAL CLEARANCE. Section 3(2) of the Street Vendors Act, 2014 expressly excludes permanent brick/concrete structures or vending that blocks hospital gates, emergency services, or public thoroughfares. The municipal action is lawful.",
                "citizen_standing": "You do not possess statutory vending immunity for permanent encroachments or emergency blockages.",
                "violator_liability": "Citizen liable for removal costs and obstruction penalties under Section 314 of Municipal Corporation Act."
            }
        elif matches_domain("SARFAESI"):
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_BANK_DEFAULT_RECOVERY",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "LAWFUL STATUTORY PROCEDURE. A scheduled bank issuing a 60-day demand notice following a 90-day unserviced NPA default is exercising lawful powers under Section 13(2) of the SARFAESI Act, 2002.",
                "citizen_standing": "The bank's notice is legally valid. You must cure the default within 60 days, submit a formal representation under Section 13(3A), or file a securitisation appeal before the DRT under Section 17.",
                "violator_liability": "Borrower secured assets subject to lawful attachment if uncured."
            }

        # 3. Citizen Rights Squandered / Unlawful Authority Action Handlers
        elif matches_domain("STREET_VENDORS"):
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "UNLAWFUL_ACT_BY_AUTHORITY",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "ILLEGAL ACTION. Under Section 3(3) of The Street Vendors Act, 2014, municipal staff and police have NO legal authority to evict you or confiscate your cart until a Town Vending Committee survey is complete. Demanding payment to allow vending constitutes criminal Extortion under BNS Section 308.",
                "citizen_standing": "You are 100% statutorily protected. You have the immediate legal right to remain at this vending location.",
                "violator_liability": "Cognizable criminal offense under BNS Section 308 (Extortion) and disciplinary violation under Street Vendors Act Section 18."
            }
        elif matches_domain("CYBER_FRAUD") or matches_domain("LOAN") or matches_domain("RBI"):
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "CRIMINAL_EXTORTION_AND_CYBER_FRAUD",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "ILLEGAL ACTION. Digital recovery agents morphing photos or contacting your friends/family violate mandatory RBI Digital Lending Guidelines and commit cognizable cyber fraud under IT Act Section 66D and BNS Section 318(4).",
                "citizen_standing": "You are a victim of predatory cyber extortion. You are under no legal obligation to pay unauthorized extortion amounts demanded by unapproved apps.",
                "violator_liability": "Up to 7 years imprisonment under BNS Section 318(4) and 3 years under IT Act Section 66D; RBI cancellation of NBFC lending license."
            }
        elif matches_domain("MOTOR_VEHICLES") or matches_domain("ACCIDENT") or matches_domain("106"):
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "ROAD_TRAFFIC_NEGLIGENCE_AND_STATUTORY_CLAIM",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "ACTIONABLE LEGAL INJURY. The colliding driver's rash and negligent operation violates BNS Section 106. You are statutorily entitled to complete medical, financial, and vehicular restitution under Section 166 of the Motor Vehicles Act, 2019.",
                "citizen_standing": "You possess an unassailable third-party insurance claim before the Motor Accidents Claims Tribunal (MACT) and criminal complaint standing under BNSS Section 173.",
                "violator_liability": "Criminal prosecution under BNS Section 106 (up to 5 years imprisonment) and complete insurer financial liability under MV Act Section 166."
            }
        elif matches_domain("RERA"):
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "STATUTORY_DEVELOPER_DEFAULT",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "ILLEGAL BREACH. Builder delay past the promised handover date without an Occupancy Certificate is a statutory breach under Section 18 of the RERA Act, 2016.",
                "citizen_standing": "You are legally entitled to demand an immediate 100% refund with interest at SBI MCLR + 2%, or monthly statutory interest for every month of delay.",
                "violator_liability": "Statutory penalty and enforcement of refund orders by the Real Estate Regulatory Authority (RERA)."
            }
        elif matches_domain("MSMED"):
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "STATUTORY_COMMERCIAL_DEFAULT",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "ILLEGAL COMMERCIAL DEFAULT. Invoices unpaid beyond 45 days automatically violate Sections 15 & 16 of the MSMED Act, 2006. The buyer has zero legal defense for withholding payment.",
                "citizen_standing": "You have a mandatory statutory entitlement to compound interest at three times the RBI bank rate with monthly rests.",
                "violator_liability": "Recovery proceedings before MSME Samadhaan Facilitation Council with non-deductible penal compound interest."
            }
        elif matches_domain("PAYMENT_OF_WAGES"):
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "UNLAWFUL_WAGE_WITHHOLDING",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": "ILLEGAL ACT. Withholding earned wages violates Section 15 of the Payment of Wages Act, 1936 and constitutes forced labor prohibited under Article 23 of the Constitution.",
                "citizen_standing": "You are entitled to claim full recovery of withheld wages plus up to ten times the deducted amount as statutory compensation.",
                "violator_liability": "Criminal prosecution under Minimum Wages Act and attachment of employer assets by the Labor Commissioner."
            }
        else:
            root = root_nodes[0] if root_nodes else {}
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "COGNIZABLE_STATUTORY_VIOLATION",
                "follow_up_required": False,
                "follow_up_question": None,
                "verdict_summary": f"ACTIONABLE VIOLATION. The acts described violate {root.get('act', 'Indian Law')} ({root.get('section', '')}).",
                "citizen_standing": "You are legally protected and entitled to register an FIR under Section 173 BNSS.",
                "violator_liability": f"Punishable under {root.get('act', '')}."
            }

    def query(self, transcript: str) -> Dict[str, Any]:
        """
        Complete GraphRAG query execution pipeline.
        Returns:
        1. Upfront Citizen Legality Verdict
        2. Extracted Subgraph (Root, Penal, Procedural, Constitutional, Evidence)
        3. Consolidated statutory sections formatted for NyayaVani UI
        """
        root_ids = self.hybrid_retrieve(transcript, top_k=2)
        subgraph = self.traverse_subgraph(root_ids, max_hops=2)
        verdict = self.generate_legality_verdict(subgraph, transcript)
        
        # Assemble statutory sections list
        statutory_sections = []
        for s in subgraph.get("statutory_protections", []):
            statutory_sections.append({"law": f"{s['act']} — {s['section']}", "details": s["operative_text"]})
        for p in subgraph.get("penal_offenses", []):
            statutory_sections.append({"law": f"{p['act']} — {p['section']}", "details": f"{p['title']}. Penalty: {p.get('penalty', '')}"})
        for c in subgraph.get("constitutional_anchors", []):
            statutory_sections.append({"law": f"{c['act']} — {c['section']}", "details": c["operative_text"]})
        for pr in subgraph.get("procedural_mandates", []):
            statutory_sections.append({"law": f"{pr['act']} — {pr['section']}", "details": pr["operative_text"]})
        for ev in subgraph.get("evidence_protocols", []):
            statutory_sections.append({"law": f"{ev['act']} — {ev['section']}", "details": ev["operative_text"]})

        return {
            "legality_verdict": verdict,
            "root_nodes": subgraph["root_nodes"],
            "statutory_sections": statutory_sections,
            "subgraph": subgraph
        }
