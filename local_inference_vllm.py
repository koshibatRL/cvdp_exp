#!/usr/bin/env python3
import json
import argparse
from vllm import LLM, SamplingParams

def load_model(model_name, tensor_parallel_size=1, gpu_memory_utilization=0.9):
    print(f"Loading vLLM model: {model_name}")
    print(f"Tensor parallel size: {tensor_parallel_size}")
    print(f"GPU memory utilization: {gpu_memory_utilization}")
    
    llm = LLM(
        model=model_name,
        tensor_parallel_size=tensor_parallel_size,
        gpu_memory_utilization=gpu_memory_utilization,
        trust_remote_code=True
    )
    return llm

def process_prompts_batch(prompts_file, responses_file, model_name, samples_per_prompt=1, tensor_parallel_size=1, gpu_memory_utilization=0.9):
    llm = load_model(model_name, tensor_parallel_size, gpu_memory_utilization)
    
    prompts_data = []
    with open(prompts_file, 'r', encoding='utf-8') as f:
        for line in f:
            prompts_data.append(json.loads(line.strip()))
    
    sampling_params = SamplingParams(
        temperature=0.8 if samples_per_prompt > 1 else 0.1,
        top_p=0.9,
        max_tokens=2048,
        n=samples_per_prompt
    )
    
    prompts = [data["prompt"] for data in prompts_data]
    print(f"Processing {len(prompts)} prompts with {samples_per_prompt} samples each...")
    
    outputs = llm.generate(prompts, sampling_params)
    
    responses = []
    for i, output in enumerate(outputs):
        prompt_id = prompts_data[i]["id"]
        for sample_output in output.outputs:
            response_text = sample_output.text.strip()
            responses.append({
                "id": prompt_id,
                "completion": response_text
            })
    
    with open(responses_file, 'w', encoding='utf-8') as f:
        for response in responses:
            f.write(json.dumps(response, ensure_ascii=False) + '\n')
    
    print(f"Generated {len(responses)} responses and saved to {responses_file}")

def main():
    parser = argparse.ArgumentParser(description="CVDP Benchmark Local Inference with vLLM")
    parser.add_argument("--prompts-file", required=True, help="Input prompts JSONL file")
    parser.add_argument("--responses-file", required=True, help="Output responses JSONL file")
    parser.add_argument("--model", required=True, help="Model name or path")
    parser.add_argument("--samples", type=int, default=1, help="Number of samples per prompt")
    parser.add_argument("--tensor-parallel-size", type=int, default=1, help="Tensor parallel size")
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.9, help="GPU memory utilization ratio")
    
    args = parser.parse_args()
    
    process_prompts_batch(
        args.prompts_file,
        args.responses_file,
        args.model,
        args.samples,
        args.tensor_parallel_size,
        args.gpu_memory_utilization
    )

if __name__ == "__main__":
    main()