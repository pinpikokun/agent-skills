---
name: voicevox-start
description: VOICEVOXエンジンの起動確認と自動起動。セッション開始時に使用する。
disable-model-invocation: true
allowed-tools: Bash(curl *), Bash(nvidia-smi *), Bash("~/AppData/Local/Programs/VOICEVOX/vv-engine/run.exe" *), Bash(sleep *)
---

VOICEVOXエンジンを起動する。以下のコマンドを実行すること:

```bash
bash ~/.claude/skills/voicevox-start/start.sh
```

結果を表示して完了。
