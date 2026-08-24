from pathlib import Path
from subprocess import check_output
from os import chdir
import re
from collections import Counter
from json import loads
from sys import exit


special_file = 'contributors-special-cases.txt'

def rewind_to_clabot_commit():
    """
    We assume that after .clabot was added,
    no commits without CLA signature have been added:
    We don't miss anything by rewinding.

    After .clabot was added formatting changes could
    hide contributions in git blame.

    Another approach would be to only look at git log,
    but that would make it harder to relate to the files touched.
    """
    log_line = check_output("git log --oneline -1 .clabot".split(" "), text=True)
    hash = log_line.split()[0]
    check_output(f"git checkout {hash}".split(" "))


def get_blame(blame_path):
    repo_cache_path = Path(__file__).parent / '.repo-cache'
    repo_cache_path.mkdir(exist_ok=True)
    chdir(repo_cache_path)

    repo = "opendp"
    repo_path = Path(repo)
    if not repo_path.exists():
        check_output(f"git clone https://github.com/opendp/{repo}.git".split(" "))
    chdir(repo_path)
    rewind_to_clabot_commit()

    blames = []
    for root, dirs, files in Path(".").walk():
        for file in files:
            file_path = root/file
            if str(file_path).startswith('.git/'):
                # Fresh checkout, so shouldn't have any generated files to ignore.
                continue
            if file_path.is_dir():
                continue
            print(f'scan {file_path}')
            try:
                blame = check_output(f"git blame --show-email {file_path}".split(" "), text=True)
            except UnicodeDecodeError:
                print(f'\tdecoding error: skip {file_path}')
                continue
            blames += [f"{file_path}: {line}" for line in blame.splitlines()]
    blame_path.write_text("\n".join(blames))


def get_counts(blame_path):
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
    special_txt = (Path(__file__).parent.parent / special_file).read_text()
    contributors = [re.sub(r'\s*#.*', '', line) for line in special_txt.splitlines() if line and not line.startswith('#')]
    return contributors

def main():
    data_cache_path = Path(__file__).parent / '.data-cache'
    data_cache_path.mkdir(exist_ok=True)
    blame_path = data_cache_path / 'blame.txt'
    counts = get_counts(blame_path)

    contributors = get_contrib()
    for c in contributors:
        del counts[c]

    specials = get_special()
    for s in specials:
        del counts[s]

    subject = 'lines of code in opendb repo when .clabot was added'
    assertion = f'covered by CLA (or author is listed in {special_file})'

    if not counts:
        print(f'All {subject} are {assertion}: yay!')
        exit(0)

    print(f'Some {subject} are not {assertion}: boo!')
    for (k, v) in counts.most_common():
        print(f"{k}: {v}")
        print(f"https://github.com/opendp/opendp/pulls?q=is%3Apr+author%3A{k}")
    exit(1)

if __name__ == '__main__':
    main()