#!/bin/bash
curl -s -o /dev/null http://localhost:50021/version && echo "VOICEVOX is already running" || {
  if nvidia-smi &>/dev/null; then
    GPU="--use_gpu"
    echo "NVIDIA GPU detected"
  fi
  "~/AppData/Local/Programs/VOICEVOX/vv-engine/run.exe" --host 127.0.0.1 --port 50021 $GPU &>/dev/null & disown
  echo "Starting VOICEVOX..."
  sleep 5
  curl -s -o /dev/null http://localhost:50021/version && echo "VOICEVOX started" || echo "VOICEVOX startup timeout"
}
