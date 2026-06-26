#!/usr/bin/env bash
# Pre-push hook: build the container image when a Containerfile/Dockerfile is
# present, to catch broken builds locally before they reach CI.
#
# DevSecOps Guardrails epic (jmservera/SquadScope-Coordinator#33), issue #544.
# SquadScope ships no container file today, so this hook is a no-op until one is
# added at the repo root (Containerfile or Dockerfile).
set -euo pipefail

containerfile=""
for candidate in Containerfile Dockerfile; do
  if [ -f "$candidate" ]; then
    containerfile="$candidate"
    break
  fi
done

if [ -z "$containerfile" ]; then
  echo "docker-build: no Containerfile/Dockerfile found — skipping."
  exit 0
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker-build: '$containerfile' present but docker is not installed." >&2
  echo "docker-build: install Docker or push with --no-verify (then fix locally)." >&2
  exit 1
fi

echo "docker-build: building image from $containerfile ..."
docker build -f "$containerfile" -t squadscope-local-build-check .
echo "docker-build: build succeeded."
