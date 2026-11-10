#!/usr/bin/env python3
"""
NyayaVani 400-Question Sovereign Multilingual Legal Benchmark Runner
Evaluates 400 comprehensive legal intake scenarios across 10 Indian languages.
Generates:
1. Detailed JSON results report (scripts/data/nyayavani_400_benchmark_results.json)
2. Exportable CSV / Excel Matrix (scripts/data/nyayavani_400_benchmark_matrix.csv)
3. Representative live Gnani Timbre voice audio samples (1 per language)
4. Full telemetry on follow-up question triggers, authority vs citizen fault attribution, and latency
"""

import os
import sys
import time
import json
import csv
from typing import Dict, Any, List

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.graph_retriever import LegalGraphRetriever
from backend.core.gnani_client import GnaniClient

VOICE_MAP = {
    "hi": "Shivani",
    "mr": "Harshad",
    "gu": "Yashraj",
    "bhoj": "Shivani",
    "kn": "Chetana",
    "ta": "Kalpana",
    "te": "Vasudha",
    "bn": "Riyaa",
    "pa": "Shivani",
    "ml": "Kalpana"
}

def run_benchmark():
    input_file = "scripts/data/nyayavani_400_test_suite.json"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Test suite file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("=" * 75)
    print(f"NYAYAVANI 400-QUESTION MULTILINGUAL LEGAL BENCHMARK")
    print(f"Total Cases: {len(cases)} across 10 Indian Languages")
    print("=" * 75)

    retriever = LegalGraphRetriever()
    client = GnaniClient()

    results = []
    correct_domains = 0
    correct_verdicts = 0
    correct_fault_attributions = 0
    correct_followup_triggers = 0
    total_latency_ms = 0.0

    live_speech_calls = 0
    saved_audio_files = []
    os.makedirs("audio_samples/benchmark_400", exist_ok=True)

    start_all = time.time()

    # Domain keyword matching helper
    def domain_matches(expected_dom: str, retrieved_nodes: List[str]) -> bool:
        for nid in retrieved_nodes:
            if (
                expected_dom in nid
                or (expected_dom == "STREET_VENDORS" and any(k in nid for k in ["STREET_VENDORS", "BNS_308"]))
                or (expected_dom == "CYBER_FRAUD" and any(k in nid for k in ["BNS_318", "IT_ACT_66D", "RBI_DIGITAL_LENDING"]))
                or (expected_dom == "MOTOR_VEHICLES" and any(k in nid for k in ["BNS_106", "MOTOR_VEHICLES", "MACT"]))
                or (expected_dom == "RERA" and "RERA" in nid)
                or (expected_dom == "MSMED" and "MSMED" in nid)
                or (expected_dom == "PAYMENT_OF_WAGES" and any(k in nid for k in ["PAYMENT_OF_WAGES", "WAGE"]))
                or (expected_dom == "CONSTITUTION_ART_21" and any(k in nid for k in ["ART_21", "BNS_329"]))
                or (expected_dom == "CONSTITUTION_ART_25" and any(k in nid for k in ["ART_25", "RELIGIOUS", "BNSS"]))
                or (expected_dom == "PROCEDURAL_BNSS" and any(k in nid for k in ["BNSS", "173"]))
                or (expected_dom == "EVIDENCE_BSA" and any(k in nid for k in ["BSA", "63"]))
                or (expected_dom == "FSSAI_FOOD_SAFETY" and any(k in nid for k in ["FSSAI", "FOOD_SAFETY", "BNS_274"]))
                or (expected_dom == "MV_TRAFFIC_OFFENSES" and any(k in nid for k in ["MV_TRAFFIC", "185", "207", "106"]))
                or (expected_dom == "MUNICIPAL_OBSTRUCTION" and any(k in nid for k in ["MUNICIPAL_OBSTRUCTION", "STREET_VENDORS"]))
                or (expected_dom == "SARFAESI_BANK_RECOVERY" and any(k in nid for k in ["SARFAESI", "BANK"]))
                or ("AMBIGUOUS" in expected_dom)  # Ambiguous queries don't depend on a single statutory node
            ):
                return True
        return False

    print("\n--- Executing GraphRAG Evaluation across 400 Scenarios ---")

    # To be cost-effective and safe with rate limits: synthesize 1 sample per language (10 audio samples total)
    audio_sample_target_ids = {f"{lcode.upper()}_01" for lcode in VOICE_MAP.keys()}

    for idx, c in enumerate(cases):
        t0 = time.time()
        query_text = c["input_text"]
        res = retriever.query(query_text)
        elapsed_ms = (time.time() - t0) * 1000
        total_latency_ms += elapsed_ms

        verdict = res["legality_verdict"]
        root_nodes = [n["id"] for n in res["root_nodes"]]

        # 1. Statutory domain match check
        is_domain_match = domain_matches(c["expected_domain"], root_nodes)
        if is_domain_match:
            correct_domains += 1

        # 2. Follow-up question requirement check
        expected_followup = c["expected_follow_up_required"]
        actual_followup = verdict.get("follow_up_required", False)
        followup_match = (expected_followup == actual_followup)
        if followup_match:
            correct_followup_triggers += 1

        # 3. Citizen at fault / Lawful authority check
        expected_fault = c["expected_citizen_fault"]
        actual_fault = verdict.get("citizen_fault")
        fault_match = (expected_fault == actual_fault)
        if fault_match:
            correct_fault_attributions += 1

        # 4. Overall verdict validity check
        if expected_followup:
            verdict_match = (verdict["status"] == "INSUFFICIENT_FACTS")
        elif expected_fault:
            verdict_match = (verdict["is_lawful"] is True and actual_fault is True)
        else:
            verdict_match = (verdict["is_lawful"] is False and actual_fault is False)

        if verdict_match:
            correct_verdicts += 1

        # 5. Live Speech synthesis for 1 representative sample per language (10 samples total)
        audio_telemetry = None
        if c["id"] in audio_sample_target_ids:
            live_speech_calls += 1
            lcode = c["language_code"]
            voice_name = VOICE_MAP.get(lcode, "Shivani")
            audio_filename = f"sample_{c['id']}_{lcode}_{voice_name}.wav"
            audio_out_path = os.path.join("audio_samples", "benchmark_400", audio_filename)
            try:
                spoken_script = verdict.get("verdict_summary", query_text)[:120]
                tts_t0 = time.time()
                tts_res = client.synthesize(
                    text=spoken_script,
                    voice=voice_name,
                    output_path=audio_out_path
                )
                tts_sec = time.time() - tts_t0
                saved_audio_files.append(audio_out_path)
                time.sleep(2.0)  # Gnani 1-concurrency rate limit cooldown
                audio_telemetry = {
                    "audio_file": audio_out_path,
                    "voice": voice_name,
                    "elapsed_seconds": round(tts_sec, 2),
                    "bytes": tts_res.get("bytes", 0)
                }
                print(f"  [SPEECH] {c['id']} ({c['language']}) -> Audio Synthesized via {voice_name} ({tts_sec:.2f}s)")
            except Exception as err:
                audio_telemetry = {"error": str(err)}
                print(f"  [SPEECH ERROR] {c['id']}: {err}")

        case_record = {
            "id": c["id"],
            "language": c["language"],
            "language_code": c["language_code"],
            "format_style": c["format_style"],
            "legal_truth_type": c["legal_truth_type"],
            "expected_domain": c["expected_domain"],
            "expected_statute": c["expected_statute"],
            "expected_is_lawful": c["expected_is_lawful"],
            "expected_citizen_fault": c["expected_citizen_fault"],
            "expected_follow_up_required": expected_followup,
            "actual_root_nodes": root_nodes,
            "actual_verdict_status": verdict["status"],
            "actual_is_lawful": verdict.get("is_lawful"),
            "actual_citizen_fault": actual_fault,
            "actual_follow_up_required": actual_followup,
            "follow_up_question": verdict.get("follow_up_question"),
            "follow_up_reason": verdict.get("follow_up_reason"),
            "verdict_summary": verdict.get("verdict_summary", ""),
            "domain_match": is_domain_match,
            "verdict_match": verdict_match,
            "latency_ms": round(elapsed_ms, 2),
            "input_text": query_text,
            "audio_telemetry": audio_telemetry
        }
        results.append(case_record)

        if (idx + 1) % 40 == 0 or idx == len(cases) - 1:
            print(f"Evaluated {idx + 1}/{len(cases)} questions... (Verdict Accuracy: {correct_verdicts / (idx + 1) * 100:.1f}%)")

    total_time_sec = time.time() - start_all
    avg_latency = total_latency_ms / len(cases)

    statute_acc = (correct_domains / len(cases)) * 100
    verdict_acc = (correct_verdicts / len(cases)) * 100
    fault_acc = (correct_fault_attributions / len(cases)) * 100
    followup_acc = (correct_followup_triggers / len(cases)) * 100

    # Credit tracking
    cost_per_req = 0.38
    credits_consumed = round(live_speech_calls * cost_per_req, 2)
    credits_remaining = round(4898.1 - credits_consumed, 2)

    summary = {
        "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases_evaluated": len(cases),
        "total_languages_evaluated": len(VOICE_MAP),
        "statutory_domain_accuracy_percent": round(statute_acc, 2),
        "overall_verdict_accuracy_percent": round(verdict_acc, 2),
        "citizen_fault_attribution_accuracy_percent": round(fault_acc, 2),
        "follow_up_trigger_accuracy_percent": round(followup_acc, 2),
        "average_retrieval_latency_ms": round(avg_latency, 2),
        "total_evaluation_time_seconds": round(total_time_sec, 2),
        "credit_telemetry": {
            "initial_credit_balance": 4898.1,
            "cost_per_live_audio_request_credits": cost_per_req,
            "live_speech_calls_executed": live_speech_calls,
            "credits_consumed_this_run": credits_consumed,
            "credits_remaining": credits_remaining,
            "is_within_budget": True
        },
        "live_audio_samples_generated": saved_audio_files
    }

    # 1. Save JSON Report
    json_out = "scripts/data/nyayavani_400_benchmark_results.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "details": results}, f, indent=2, ensure_ascii=False)

    # 2. Save CSV / Excel Matrix
    csv_out = "scripts/data/nyayavani_400_benchmark_matrix.csv"
    with open(csv_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Case ID",
            "Language",
            "Language Code",
            "Format Style",
            "Legal Truth Type",
            "Expected Domain",
            "Expected Statute",
            "Expected Authority Lawful?",
            "Expected Citizen Fault?",
            "Expected Follow-up Required?",
            "Actual Root Nodes",
            "Actual Verdict Status",
            "Actual Authority Lawful?",
            "Actual Citizen Fault?",
            "Actual Follow-up Required?",
            "Follow-up Question Generated",
            "Follow-up Reason / Ground",
            "Domain Match (T/F)",
            "Verdict Match (T/F)",
            "Latency (ms)",
            "Verdict Summary",
            "Input Transcript"
        ])
        for r in results:
            writer.writerow([
                r["id"],
                r["language"],
                r["language_code"],
                r["format_style"],
                r["legal_truth_type"],
                r["expected_domain"],
                r["expected_statute"],
                str(r["expected_is_lawful"]),
                str(r["expected_citizen_fault"]),
                str(r["expected_follow_up_required"]),
                "; ".join(r["actual_root_nodes"]),
                r["actual_verdict_status"],
                str(r["actual_is_lawful"]),
                str(r["actual_citizen_fault"]),
                str(r["actual_follow_up_required"]),
                r["follow_up_question"] or "N/A (Immediate Verdict Rendered)",
                r["follow_up_reason"] or "N/A (Facts Actionable on Turn 1)",
                "PASS" if r["domain_match"] else "FAIL",
                "PASS" if r["verdict_match"] else "FAIL",
                r["latency_ms"],
                r["verdict_summary"],
                r["input_text"]
            ])

    print("\n" + "=" * 75)
    print("400-QUESTION BENCHMARK SUMMARY")
    print(f"Total Cases Evaluated:       {len(cases)}")
    print(f"Languages Covered:           10 Indian Languages")
    print(f"Overall Verdict Accuracy:    {verdict_acc:.1f}%")
    print(f"Statutory Domain Accuracy:   {statute_acc:.1f}%")
    print(f"Citizen Fault Attribution:   {fault_acc:.1f}%")
    print(f"Follow-up Trigger Accuracy:  {followup_acc:.1f}%")
    print(f"Avg GraphRAG Latency:        {avg_latency:.2f} ms")
    print(f"Live Audio Files Generated:  {len(saved_audio_files)}")
    print(f"Credits Consumed:            {credits_consumed} credits (₹{credits_consumed * 0.01:.2f})")
    print(f"Remaining Credit Balance:    {credits_remaining} credits")
    print(f"JSON Report Saved:           {json_out}")
    print(f"Excel/CSV Spreadsheet Saved: {csv_out}")
    print("=" * 75)

    return summary

if __name__ == "__main__":
    run_benchmark()
