from pathlib import Path
from subprocess import check_output
from os import chdir
import re
from collections import Counter
from json import loads


def get_blame(blame_path):
    chdir("/tmp")
    path = Path("opendp")
    if not path.exists():
        check_output("git clone https://github.com/opendp/opendp.git".split(" "))
    chdir("opendp")
    blames = []
    for root, dirs, files in Path(".").walk():
        for file in files:
            file_path = root/file
            if str(file_path).startswith('.git/'):
                # Fresh checkout, so shouldn't have any generated files to ignore.
                continue
            print(file_path)
            if file_path.is_dir():
                continue
            try:
                blame = check_output(f"git blame --show-email {file_path}".split(" "), text=True)
            except UnicodeDecodeError:
                continue
            blames += [f"{file_path}: {line}" for line in blame.splitlines()]
    chdir("..")
    blame_path.write_text("\n".join(blames))


def get_counts():
    chdir("/tmp")
    blame_path = Path("opendp.blame")
    if not blame_path.exists():
        get_blame(blame_path)
    blame = blame_path.read_text().splitlines()
    counts = Counter()
    for line in blame:
        m = re.match(r'^([^:]+): [0-9a-f^]{9}(?: [^(]+)? \(<(?:\d+\+)?([^@]+)', line)
        if m:
            file = m.group(1)
            user = m.group(2).lower()
            counts[user] += 1
        else:
            raise Exception(f'No match: {line}')
    return counts


def get_contrib():
    contributors_json = (Path(__file__).parent.parent / 'contributors.json').read_text()
    contributors = [c.lower() for c in loads(contributors_json)]
    return contributors


def get_special():
    special_txt = (Path(__file__).parent.parent / 'contributors-special.txt').read_text()
    contributors = [uncomment for line in special_txt.splitlines() if (uncomment := line.split('#')[0].strip())]
    return contributors

def main():
    counts = get_counts()
    contributors = get_contrib()
    specials = get_special()
    for c in contributors:
        del counts[c]
    for s in specials:
        del counts[s]
    for (k, v) in counts.most_common():
        print(f"{k}: {v}")

if __name__ == '__main__':
    main()