#!/bin/bash
# コンテナ内で実行するコマンド

echo "=== CVDP Benchmark ワークフロー ==="

# Step 1: CVDP依存関係をインストール
echo "Step 1: Installing CVDP dependencies..."
pip3 install -r /workspace/cvdp_benchmark/requirements.txt

# Step 2: HuggingFaceデータセットのパスを確認
echo "Step 2: Locating HuggingFace dataset..."
DATASET_PATH=$(find /data4/.cache/huggingface/hub/datasets--nvidia--cvdp-benchmark-dataset -name "*.jsonl" | grep "cvdp.*nonagentic.*no_commercial" | head -1)
if [ -z "$DATASET_PATH" ]; then
    echo "❌ データセットファイルが見つかりません"
    echo "利用可能なファイル:"
    find /data4/.cache/huggingface/hub/datasets--nvidia--cvdp-benchmark-dataset -name "*.jsonl" | head -5
    exit 1
fi
echo "✅ データセットファイル: $DATASET_PATH"

# Step 3: プロンプトエクスポート
echo "Step 3: Exporting prompts..."
python3 /workspace/cvdp_benchmark/run_samples.py \
  -f "$DATASET_PATH" \
  --model local_export \
  --prompts-responses-file /workspace/data/exported_prompts.jsonl \
  -n 3 \
  -p /workspace/results/vllm_experiment

# Step 4: vLLM推論
echo "Step 4: Running vLLM inference..."
python3 /workspace/local_inference_vllm.py \
  --prompts-file /workspace/data/exported_prompts.jsonl \
  --responses-file /workspace/data/responses.jsonl \
  --model "codellama/CodeLlama-7b-Instruct-hf" \
  --samples 3 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.8

# Step 5: 結果インポートと評価
echo "Step 5: Importing responses and evaluating..."
python3 /workspace/cvdp_benchmark/run_samples.py \
  -f "$DATASET_PATH" \
  --model local_import \
  --prompts-responses-file /workspace/data/responses.jsonl \
  -n 3 \
  -p /workspace/results/vllm_experiment

# Step 6: 結果表示
echo "Step 6: Showing results..."
cat /workspace/results/vllm_experiment/composite_report.txt

echo "=== ワークフロー完了 ==="