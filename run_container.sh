#!/bin/bash

GPU_DEVICES="0"

docker run -it --rm \
  --gpus "device=$GPU_DEVICES" \
  --name cvdp-vllm \
  -v $(pwd):/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /data4:/data4 \
  -w /workspace/cvdp_benchmark \
  cvdp-vllm:latest \
  /bin/bash