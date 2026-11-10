#!/usr/bin/env python3
import os
import sys
import time
import argparse
from huggingface_hub import snapshot_download

def download():
    parser = argparse.ArgumentParser(description="Download SLM weights to External SSD")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-1.5B-Instruct", 
                        choices=["Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-3B-Instruct", "meta-llama/Llama-3.2-3B-Instruct", "meta-llama/Llama-3.2-1B-Instruct"])
    args = parser.parse_args()

    model_dir_name = args.model.split("/")[-1]
    target_dir = f"/Volumes/Jonath SSD1/nyayavani_models/{model_dir_name}"
    print(f"Target Directory on External SSD: {target_dir}")
    os.makedirs(target_dir, exist_ok=True)
    
    # Strictly isolate all HuggingFace caches to the external drive
    os.environ["HF_HOME"] = "/Volumes/Jonath SSD1/nyayavani_models/hf_cache"
    os.environ["TRANSFORMERS_CACHE"] = "/Volumes/Jonath SSD1/nyayavani_models/hf_cache"

    print(f"Initiating download for {args.model} directly to External SSD...")
    start_time = time.time()
    
    try:
        downloaded_path = snapshot_download(
            repo_id=args.model,
            local_dir=target_dir
        )
    except Exception as e:
        print(f"\nDownload failed: {e}")
        if "gated repo" in str(e).lower() or "403" in str(e):
            print("\n[Notice] This model is gated by the vendor (Meta/Google).")
            print(f"To unlock it, log in to HuggingFace and accept terms at: https://huggingface.co/{args.model}")
            print("Alternatively, use open model: python3 scripts/download_slm.py --model Qwen/Qwen2.5-1.5B-Instruct")
        return

    elapsed = time.time() - start_time
    print(f"\nDownload completed successfully in {elapsed:.1f} seconds!")
    print(f"Model saved to: {downloaded_path}")
    
    # List files and total size on external SSD
    total_size = 0
    print("\nFiles on External SSD:")
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            total_size += sz
            print(f"  • {f} ({sz / (1024*1024):.1f} MB)")
            
    print(f"\nTotal Model Size on External Drive: {total_size / (1024*1024*1024):.2f} GB")

if __name__ == "__main__":
    download()
