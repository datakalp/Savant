#!/bin/bash
# you are expected to be in Savant/ directory

DOCKER_IMAGE=ghcr.io/insight-platform/savant-deepstream:latest
DOCKER_RUNTIME="--gpus=all"
if [ "$(uname -m)" = "aarch64" ]; then
  DOCKER_IMAGE=ghcr.io/insight-platform/savant-deepstream-l4t:latest
  DOCKER_RUNTIME="--runtime=nvidia"
fi

docker run --rm -it $DOCKER_RUNTIME \
  -e BUFFER_QUEUES \
  -v `pwd`/samples:/opt/savant/samples \
  -v `pwd`/data:/data:ro \
  $DOCKER_IMAGE \
  samples/opencv_cuda_bg_remover_mog2/demo_performance.yml
