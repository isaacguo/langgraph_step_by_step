#!/bin/bash
set -e

echo "Building Docker image..."
cd "$(dirname "$0")/.."
docker build -t langgraph-safety:latest -f docker/Dockerfile .
echo "Build complete."
