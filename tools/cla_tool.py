import argparse
import datetime
import glob
import json
import os
import os.path
import sys


def log(message, command=False):
    prefix = "$" if command else "#"
    print(f"{prefix} {message}", file=sys.stderr)


def get_date():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(val, out_dir, out_name, out_ext="json"):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{out_name}.{out_ext}")
    with open(out_path, "w") as fout:
        json.dump(val, fout, indent=4)
        fout.write("\n")


def sign(args, company=False):
    date = args.date or get_date()
    signature = dict(
        version=args.sig_version,
        date=date,
        github_id=args.github_id,
        cla=args.cla,
        name=args.name,
        attestation=args.attestation,
    )
    if company:
        extra = dict(
            company=args.company,
            representative_name=args.representative_name,
            representative_attestation=args.representative_attestation,
        )
        signature = {**signature, **extra}
    log(f"signature = {signature}")
    write_json(signature, args.sig_dir, args.github_id)


def sign_individual(args):
    log("*** SIGNING FOR INDIVIDUAL ***")
    sign(args, False)


def sign_company(args):
    log("*** SIGNING FOR COMPANY ***")
    sign(args, True)


def get_contributors(sig_dir):
    return [path[len(sig_dir)+1:-5] for path in glob.glob(os.path.join(sig_dir, "*.json"))]


def generate_config(args):
    log("*** GENERATING CLA-BOT CONFIG ***")
    int_contribs = get_contributors(args.int_sig_dir)
    ind_contribs = get_contributors(args.ind_sig_dir)
    com_contribs = get_contributors(args.com_sig_dir)
    contribs = sorted(int_contribs + ind_contribs + com_contribs)
    # We need github-actions in the list for automated PRs.
    contribs += ["github-actions[bot]"]
    write_json(contribs, args.conf_dir, args.contributors_file)


def _main(argv):
    def nonempty_str(arg):
        arg = arg.strip()
        if not arg:
            raise argparse.ArgumentTypeError("Empty string!")
        return arg

    def attestation(arg):
        arg = nonempty_str(arg)
        if not arg.upper() == "I AGREE":
            raise argparse.ArgumentTypeError("Attestation must be \"I AGREE\"!")
        return arg

    parser = argparse.ArgumentParser(description="OpenDP CLA tool")
    subparsers = parser.add_subparsers(dest="COMMAND", help="Command to run")
    subparsers.required = True

    subparser = subparsers.add_parser("sign-int", help="Sign CLA for internal contributor")
    subparser.set_defaults(func=sign_individual)
    subparser.add_argument("-V", "--sig-version", default="1.0.0")
    subparser.add_argument("-d", "--date", type=nonempty_str)
    subparser.add_argument("-g", "--github-id", type=nonempty_str, required=True)
    subparser.add_argument("-u", "--cla", default="https://opendp.org/files/opendifferentialprivacy/files/cla_opendp_project_2021.pdf")
    subparser.add_argument("-n", "--name", type=nonempty_str, required=True)
    subparser.add_argument("-a", "--attestation", type=nonempty_str, required=True)
    subparser.add_argument("-s", "--sig-dir", default="signatures/internal")

    subparser = subparsers.add_parser("sign-ind", help="Sign CLA for individual contributor")
    subparser.set_defaults(func=sign_individual)
    subparser.add_argument("-V", "--sig-version", default="1.0.0")
    subparser.add_argument("-d", "--date", type=nonempty_str)
    subparser.add_argument("-g", "--github-id", type=nonempty_str, required=True)
    subparser.add_argument("-u", "--cla", default="https://opendp.org/files/opendifferentialprivacy/files/cla_opendp_project_2021.pdf")
    subparser.add_argument("-n", "--name", type=nonempty_str, required=True)
    subparser.add_argument("-a", "--attestation", type=attestation, required=True)
    subparser.add_argument("-s", "--sig-dir", default="signatures/individual")

    subparser = subparsers.add_parser("sign-com", help="Sign CLA for company contributor")
    subparser.set_defaults(func=sign_company)
    subparser.add_argument("-V", "--sig-version", default="1.0.0")
    subparser.add_argument("-d", "--date", type=nonempty_str)
    subparser.add_argument("-g", "--github-id", type=nonempty_str, required=True)
    subparser.add_argument("-u", "--cla", default="https://opendp.org/files/opendifferentialprivacy/files/cla_opendp_project_2021.pdf")
    subparser.add_argument("-n", "--name", type=nonempty_str, required=True)
    subparser.add_argument("-a", "--attestation", type=attestation, required=True)
    subparser.add_argument("-X", "--company", type=nonempty_str, required=True)
    subparser.add_argument("-N", "--representative-name", type=nonempty_str, required=True)
    subparser.add_argument("-A", "--representative-attestation", type=attestation, required=True)
    subparser.add_argument("-s", "--sig-dir", default="signatures/company")

    subparser = subparsers.add_parser("gen-conf", help="Generate cla-bot config")
    subparser.set_defaults(func=generate_config)
    subparser.add_argument("-s1", "--int-sig-dir", default="signatures/internal")
    subparser.add_argument("-s2", "--ind-sig-dir", default="signatures/individual")
    subparser.add_argument("-s3", "--com-sig-dir", default="signatures/company")
    subparser.add_argument("-c", "--conf-dir", default=".")
    subparser.add_argument("-f", "--contributors-file", default="contributors")

    args = parser.parse_args(argv[1:])
    args.func(args)


def main():
    _main(sys.argv)


if __name__ == "__main__":
    main()
