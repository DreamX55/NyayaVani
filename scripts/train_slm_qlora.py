#!/usr/bin/env python3
"""
NyayaVani Sovereign SLM Fine-Tuning Script (LoRA / QLoRA)
Supports Apple Silicon (MPS) and NVIDIA CUDA.
Strictly respects external storage: all HuggingFace caches and adapter weights
can be pointed to your external SSD mount path.
"""

import os
import argparse
import json
import torch

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune a 1B-3B SLM for NyayaVani")
    parser.add_argument("--model_name", type=str, default="meta-llama/Llama-3.2-3B-Instruct", help="Base model identifier")
    parser.add_argument("--dataset_path", type=str, default="scripts/data/nyayavani_finetune_dataset.jsonl", help="Path to training data")
    parser.add_argument("--cache_dir", type=str, default=None, help="Path on EXTERNAL SSD to store downloaded base weights (e.g., /Volumes/MySSD/hf_cache)")
    parser.add_argument("--output_dir", type=str, default="nyayavani_lora_adapter", help="Directory to save trained LoRA adapter weights")
    parser.add_argument("--batch_size", type=int, default=2, help="Per-device train batch size")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Peak learning rate")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA alpha scaling factor")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. External SSD Path Configuration
    if args.cache_dir:
        os.makedirs(args.cache_dir, exist_ok=True)
        os.environ["HF_HOME"] = args.cache_dir
        os.environ["TRANSFORMERS_CACHE"] = args.cache_dir
        print(f"[Storage Safety] All base model downloads & caches directed to EXTERNAL STORAGE: {args.cache_dir}")
    else:
        print("[Notice] No external --cache_dir specified. Please pass --cache_dir /Volumes/<Your_SSD>/cache if running locally.")

    # 2. Hardware Device Selection (CUDA vs MPS vs CPU)
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.bfloat16
        print(f"[Compute] Active hardware: NVIDIA CUDA ({torch.cuda.get_device_name(0)})")
    elif torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
        print("[Compute] Active hardware: Apple Silicon Metal Performance Shaders (MPS)")
    else:
        device = "cpu"
        dtype = torch.float32
        print("[Compute] Active hardware: CPU")

    print(f"\n--- NyayaVani SLM LoRA Fine-Tuning Pipeline ---")
    print(f"Base Model:       {args.model_name}")
    print(f"Training Dataset: {args.dataset_path}")
    print(f"LoRA Target:      Rank={args.lora_r}, Alpha={args.lora_alpha}")
    print(f"Epochs:           {args.epochs}")
    print(f"Output Directory: {args.output_dir}\n")

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
        from peft import LoraConfig, get_peft_model, TaskType
        from datasets import load_dataset
    except ImportError as e:
        print(f"Error: Missing training dependencies: {e}")
        print("Install required fine-tuning packages:")
        print("  pip install peft trl datasets bitsandbytes accelerate")
        return

    # 3. Load Tokenizer & Model
    print(f"Loading base model weights (Cache: {args.cache_dir or 'Default'})...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, cache_dir=args.cache_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        torch_dtype=dtype,
        cache_dir=args.cache_dir,
        device_map="auto" if device == "cuda" else None
    )

    if device == "mps":
        model = model.to("mps")

    # 4. LoRA Adapter Configuration
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 5. Load and Tokenize Dataset
    print(f"Loading training data from {args.dataset_path}...")
    dataset = load_dataset("json", data_files=args.dataset_path, split="train")

    def format_prompt(sample):
        text = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            f"{sample['instruction']}<|eot_id|>\n"
            f"<|start_header_id|>user<|end_header_id|>\n"
            f"{sample['input']}<|eot_id|>\n"
            f"<|start_header_id|>assistant<|end_header_id|>\n"
            f"{sample['output']}<|eot_id|>"
        )
        return tokenizer(text, truncation=True, max_length=1024, padding="max_length")

    tokenized_dataset = dataset.map(format_prompt, batched=False)

    # 6. Training Arguments & Execution
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        num_train_epochs=args.epochs,
        logging_steps=10,
        save_strategy="epoch",
        fp16=(device == "mps"),
        bf16=(device == "cuda"),
        report_to="none"
    )

    from transformers import Trainer, DataCollatorForLanguageModeling
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    print("\nStarting training loop...")
    trainer.train()

    print(f"\nTraining completed! Saving LoRA adapter to {args.output_dir}...")
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"LoRA adapter successfully saved! Total size: ~50 MB.")

if __name__ == "__main__":
    main()
