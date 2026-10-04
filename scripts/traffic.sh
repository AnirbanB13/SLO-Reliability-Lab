#!/usr/bin/env bash
# Sends ~5 checkout requests per second until you press Ctrl+C
URL=${1:-http://localhost:8080/checkout}
while true; do
  curl -s -o /dev/null -X POST "$URL"
  sleep 0.2
done
