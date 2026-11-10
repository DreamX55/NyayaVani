# NyayaVani Benchmark & Evaluation Track: Provenance, Methodology, and Reproducibility

## 1. Overview
The `scripts/` directory contains an offline synthetic benchmark and SLM fine-tuning suite developed to evaluate the Sovereign Legal Knowledge Graph retrieval accuracy and language model grounding across Indian languages.

> **Important Guardrail:** In accordance with the NyayaVani Product Requirements Document and rigorous scientific evaluation standards, synthetic evaluation metrics are documented strictly as **offline preliminary benchmarks**. No unverified production accuracy score is advertised until reproduced against held-out, human-annotated empirical case sets.

## 2. Dataset Provenance & Data Hygiene
- **Synthetic Generator:** `scripts/generate_400_benchmark_dataset.py` generates 400 multi-domain citizen query scenarios covering 10 Indian languages (Hindi, Marathi, Gujarati, Kannada, Tamil, Telugu, Bengali, Punjabi, Malayalam, and English).
- **Domain Coverage:**
  1. Street Vendor Livelihood Protection (Street Vendors Act, 2014)
  2. Wage Withholding & Minimum Wage (Payment of Wages Act, 1936 / Code on Wages, 2019)
  3. Real Estate Possession Delay (RERA Act, 2016)
  4. MSME Commercial Default (MSMED Act, 2006)
  5. Motor Vehicle Third-Party Injury & MACT (Motor Vehicles Act, 1988)
  6. Predatory Digital Lending & Cyber Fraud (IT Act, 2000 / RBI Guidelines)
  7. Food Safety Seizures (FSSAI Act, 2006)
  8. Municipal Encroachment (Municipal Acts)
- **Data Leakage Prevention:**
  - Distinct seed templates and vocabulary variations are used between training fine-tune sets (`nyayavani_finetune_dataset.jsonl`) and evaluation test suites (`nyayavani_400_test_suite.json`).
  - No private user audio or WhatsApp communications are included in training or evaluation datasets.

## 3. Evaluation Scripts
- `scripts/run_400_benchmark.py`: Evaluates retrieval precision, domain routing, and reciprocal rank fusion (RRF) across the 400 test scenarios.
- `scripts/run_multilingual_benchmark.py`: Evaluates cross-lingual consistency and script adaptation across the 10 Indic languages.
- `scripts/train_slm_qlora.py`: Offline QLoRA fine-tuning script targeting local Small Language Models (e.g. Qwen2.5-Coder-7B or Sarvam-2B) for sovereign offline edge deployment.

## 4. Reproducibility Instructions
To run the offline benchmark suite:
```powershell
# Run the 400-query benchmark
python scripts/run_400_benchmark.py

# Run the 10-language Indic cross-lingual benchmark
python scripts/run_multilingual_benchmark.py
```
All outputs are saved to `scripts/data/` with timestamps and parameter hashes.
