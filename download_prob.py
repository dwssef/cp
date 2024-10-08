#!/usr/bin/env python3
"""Download and setup problems from Competitive Companion

Usage:
  download_prob.py --echo
  download_prob.py [<name>... | -n <number> | -b <batches> | --timeout <timeout>] [--dryrun]

Options:
  -h --help     Show this screen.
  --echo        Just echo received responses and exit.
  --dryrun      Don't actually create any problems

Download limit options:
  -n COUNT, --number COUNT   Number of problems.
  -b COUNT, --batches COUNT  Number of batches. (Default 1 batch)
  -t TIME, --timeout TIME    Timeout for listening to problems. in seconds
"""

import http.server
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from docopt import docopt


# Returns unmarshalled or None
def listen_once(*, timeout=None):
    json_data = None

    class CompetitiveCompanionHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            nonlocal json_data
            json_data = json.load(self.rfile)

    with http.server.HTTPServer(
        ("127.0.0.1", 10046), CompetitiveCompanionHandler
    ) as server:
        server.timeout = timeout
        server.handle_request()

    if json_data is not None:
        print(f"Got data {json.dumps(json_data)}")
    else:
        print("Got no data")
    return json_data


def listen_many(*, num_items=None, num_batches=None, timeout=None):
    if num_items is not None:
        res = []
        for _ in range(num_items):
            cur = listen_once(timeout=None)
            res.append(cur)
        return res

    if num_batches is not None:
        res = []

        batches = {}
        while len(batches) < num_batches or any(need for need, tot in batches.values()):
            print(f"Waiting for {num_batches} batches:", batches)
            cur = listen_once(timeout=None)
            res.append(cur)

            cur_batch = cur["batch"]
            batch_id = cur_batch["id"]
            batch_cnt = cur_batch["size"]
            if batch_id not in batches:
                batches[batch_id] = [batch_cnt, batch_cnt]
            assert batches[batch_id][0] > 0
            batches[batch_id][0] -= 1

        return res

    res = [listen_once(timeout=None)]
    while True:
        cnd = listen_once(timeout=timeout)
        if cnd is None:
            break
        res.append(cnd)
    return res


NAME_PATTERN = re.compile(r"^(?:Problem )?([A-Z][0-9]*)\b")


def get_prob_name(data):
    if "USACO" in data["group"]:
        if "fileName" in data["input"]:
            names = [
                data["input"]["fileName"].rstrip(".in"),
                data["output"]["fileName"].rstrip(".out"),
            ]
            if len(set(names)) == 1:
                return names[0]

    if "url" in data and data["url"].startswith("https://www.codechef.com"):
        return data["url"].rstrip("/").rsplit("/")[-1]

    patternMatch = NAME_PATTERN.search(data["name"])
    if patternMatch is not None:
        return patternMatch.group(1)

    print(f"For data: {json.dumps(data, indent=2)}")
    return input("What name to give? ")


def save_samples(data, prob_dir):
    with open(prob_dir / "problem.json", "w") as f:
        json.dump(data, f)

    for i, t in enumerate(data["tests"], start=1):
        with open(prob_dir / f"sample{i}.in", "w") as f:
            f.write(t["input"])
        with open(prob_dir / f"sample{i}.out", "w") as f:
            f.write(t["output"])


# Providing name = '.'
def make_prob(data, name=None):
    if name is None:
        name = get_prob_name(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prob_dir = Path(".") / f"{name}_{timestamp}"  # 添加时间戳到目录名
    # prob_dir = Path('.')/name

    if name == ".":
        print("Using current directory...")
        pass
    elif prob_dir.exists() and prob_dir.is_dir():
        # Skip making it
        print(f"Already created problem {name}...")
    else:
        print(f"Creating problem {name}...")
        get_template(prob_dir, name)

    print("Saving samples...")
    save_samples(data, prob_dir)

    print()


def get_template(prob_dir, name):
    template_dir = Path.cwd() / ".template"

    if template_dir.exists() and template_dir.is_dir():
        os.makedirs(prob_dir, exist_ok=True)

        for item in template_dir.iterdir():
            target_path = Path(prob_dir)

            if item.is_file():
                if item.suffix == ".cpp":
                    new_file_name = f"{name}.cpp"
                    target_path = target_path / new_file_name
                shutil.copy(item, target_path)
                print(f"Copied file: {item} to {target_path}")
            elif item.is_dir():
                shutil.copytree(item, target_path / item.name, dirs_exist_ok=True)
                print(f"Copied directory: {item} to {target_path / item.name}")
    else:
        print(f"Template directory '{template_dir}' does not exist.")


def main():
    arguments = docopt(__doc__)

    if arguments["--echo"]:
        while True:
            print(listen_once())
    else:
        dryrun = arguments["--dryrun"]

        def run_make_prob(*args, **kwargs):
            nonlocal dryrun
            if dryrun:
                print(f"make_prob(*args={args}, **kwargs={kwargs})")
                return
            make_prob(*args, **kwargs)

        if names := arguments["<name>"]:
            datas = listen_many(num_items=len(names))
            for data, name in zip(datas, names):
                run_make_prob(data, name)
        elif cnt := arguments["--number"]:
            cnt = int(cnt)
            datas = listen_many(num_items=cnt)
            for data in datas:
                run_make_prob(data)
        elif batches := arguments["--batches"]:
            batches = int(batches)
            datas = listen_many(num_batches=batches)
            for data in datas:
                run_make_prob(data)
        elif timeout := arguments["--timeout"]:
            timeout = float(timeout)
            datas = listen_many(timeout=timeout)
            for data in datas:
                run_make_prob(data)
        else:
            datas = listen_many(num_batches=1)
            for data in datas:
                run_make_prob(data)


if __name__ == "__main__":
    main()
