"""Execute the reference exporter in one Blender process to amortize startup."""
import json
import sys
from pathlib import Path
requests=Path(sys.argv[sys.argv.index('--')+1])
runner=Path(__file__).with_name('run_blender.py')
for item in json.loads(requests.read_text()):
    sys.argv=['blender','--',item['script'],item['output']]
    exec(compile(runner.read_text(),str(runner),'exec'), {'__name__':'__main__','__file__':str(runner)})
