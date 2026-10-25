"""Stage answer candidates outside the repository; CC BY-SA is not permissive.

This discovery command does not import candidates into the corpus. The import
command preserves the original share-alike licenses and attribution. A code block is
HTML-decoded without adding imports, concatenating blocks, or repairing code.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pre = self.code = False
        self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.pre = True
        if tag == "code" and self.pre:
            self.code = True
            self.blocks.append("")
    def handle_endtag(self, tag):
        if tag == "pre":
            self.pre = False
        if tag == "code":
            self.code = False
    def handle_data(self, data):
        if self.pre and self.code:
            self.blocks[-1] += data


def fetch(path, parameters, dest):
    url = "https://api.stackexchange.com/2.3/" + path + "?" + urlencode(dict(site="blender", **parameters))
    if dest.exists():
        data = json.loads(dest.read_text())
    else:
        raw = subprocess.run(["curl", "-fsSL", "--retry", "2", "--max-time", "60", url], capture_output=True, check=True).stdout
        dest.write_bytes(raw)
        data = json.loads(raw)
        if data.get("backoff"):
            time.sleep(data["backoff"])
    if data.get("error_id"):
        raise RuntimeError(data)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", required=True)
    parser.add_argument("--count", type=int, default=92)
    args = parser.parse_args()
    staging = Path(args.staging).resolve()
    staging.mkdir(parents=True, exist_ok=True)
    candidates, hashes = [], set()
    for page in range(1, 6):
        questions = fetch("search/advanced", {"q": "bpy", "tagged": "python", "accepted": "True", "sort": "votes", "order": "desc", "pagesize": 100, "page": page}, staging / f"questions-{page}.json")
        ids = [str(q["question_id"]) for q in questions["items"]]
        answers = fetch("questions/" + ";".join(ids) + "/answers", {"sort": "votes", "order": "desc", "pagesize": 100, "filter": "withbody"}, staging / f"answers-{page}.json")
        for answer in answers["items"]:
            parser = Blocks()
            parser.feed(answer["body"])
            for index, source in enumerate(parser.blocks):
                if "import bpy" not in source or len(source.splitlines()) < 12:
                    continue
                sha = hashlib.sha256(source.encode()).hexdigest()
                if sha in hashes:
                    continue
                filename = f"stackexchange-{answer['answer_id']}-block-{index+1}.py"
                (staging / filename).write_bytes(source.encode())
                (staging / (filename + ".answer.json")).write_text(json.dumps(answer, indent=2) + "\n")
                candidates.append({"file": filename, "provider": "blender-stackexchange", "source_url": f"https://blender.stackexchange.com/a/{answer['answer_id']}",
                                   "author": answer.get("owner", {}).get("display_name"), "author_url": answer.get("owner", {}).get("link"),
                                   "license": answer.get("content_license", "UNCONFIRMED"), "answer_id": answer["answer_id"], "code_block": index + 1,
                                   "sha256": sha, "source_transform": "HTML entity decoding only; one unchanged code block",
                                   "creation_date": answer["creation_date"], "last_edit_date": answer.get("last_edit_date")})
                hashes.add(sha)
                break  # At most one script per answer; never pad with fragments.
            if len(candidates) == args.count:
                break
        (staging / "candidates.json").write_text(json.dumps(candidates, indent=2) + "\n")
        print(json.dumps({"page": page, "candidates": len(candidates), "quota_remaining": answers.get("quota_remaining")}), flush=True)
        if len(candidates) == args.count or not questions.get("has_more"):
            break
