import json
from graphify.detect import detect
from pathlib import Path
result = detect(Path('.'))
# Write the sidecar from Python, not a shell redirect, so the same block renders
# on PowerShell hosts without console-encoding drift (#2528).
Path('graphify-out\.graphify_detect.json').write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
print(f'Detected {result["total_files"]} files')
