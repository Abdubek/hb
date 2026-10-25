"""Execute the unchanged file, reporting the original Python exception."""
import json
import runpy
import sys
import traceback
import bpy

source = sys.argv[sys.argv.index("--") + 1]
record = {"blender_version": bpy.app.version_string, "source": source}
try:
    runpy.run_path(source, run_name="__main__")
    record["ok"] = True
except BaseException as error:
    frames = traceback.extract_tb(error.__traceback__)
    own = [frame for frame in frames if frame.filename == source]
    record.update(ok=False, exception=type(error).__name__, message=str(error),
                  line=own[-1].lineno if own else getattr(error, "lineno", None))
    traceback.print_exc()
print("CORPUS_RESULT=" + json.dumps(record), flush=True)
if not record["ok"]:
    raise SystemExit(1)
