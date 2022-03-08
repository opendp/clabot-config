# Configuration for the OpenDP CLA management bot

The OpenDP Project requires a [Contributor License Agreement](https://docs.opendp.org/en/stable/developer/cla.html) from all contributors.
We use the GitHub Application [cla-bot](https://colineberhardt.github.io/cla-bot) to manage the checking of CLAs and tagging of pull requests.
This repository contains the configuration files for `cla-bot`, as well as some utilities to simplify administration.

## Configuration

The configuration here is shared across any `opendp` repos that opt into the CLA requirement.
This way, contributors that sign the CLA in the scope of one repo will be verified for other repos that have opted in.

> Note that `cla-bot` can be enabled for *all* repositories in an organization, by installing the app at the organization level.
> We've chosen **not** to do this yet, to avoid hassles with scratch repos and legacy projects.
> Instead, we expect individual repos to opt into CLA checking on an as-needed basis.

### Enabling CLA checking for a repo

To enable `cla-bot` functionality on a repo, these are the steps:

1. Install the `cla-bot` app for the repo.
   1. Go to [the `cla-bot` GitHub App page](https://github.com/apps/cla-bot).
   2. Click "Configure".
   3. Follow the instructions to enable the app **for the target repo only**.
2. Copy the file [`.clabot`](.clabot) from here to the root of the other repo.

### Files in this repo

* [`.clabot`](.clabot): The main `cla-bot` configuration file.
  This contains entries for the `contributors` URL, and the `message` text that is shown to new contributors.
  *The `.clabot` file must be copied to the root of any repositories that want to enable CLA checking.*
* [`contributors.json`](contributors.json): The set of contributors who have signed the CLA.
  This consists of a JSON list, where each element is a GitHub ID.
  It is generated from the signature files below.
* [`signatures/`](signatures): A directory containing signature files (in subdirectories).
  Each signature file contains a JSON object with the properties of the signature.
  * [`signatures/internal/<GITHUB_ID>.json`](signatures/internal): The directory of signature files for internal (Harvard) contributors.
    This been seeded with current OpenDP team members.
  * [`signatures/individual/<GITHUB_ID>.json`](signatures/individual): The directory of signature files for individual (external) contributors.
    (Empty to start.)
  * [`signatures/company/<GITHUB_ID>.json`](signatures/company): The directory of signature files for company (external) contributors.
    (Empty to start.)

## Tools

Rather than managing signatures and config files manually, we’d like to make things as simple as possible, so we have some tools to automate the process.

### [`cla_tool.py`](tools/cla_tool.py)

This is a script to automate the capturing of CLA signatures and generation of `cla-bot` config files.

```
$ python tools/cla_tool.py -h
usage: cla_tool.py [-h] {sign-int,sign-ind,sign-com,gen-conf} ...

OpenDP CLA tool

positional arguments:
{sign-int,sign-ind,sign-com,gen-conf}
Command to run
sign-int            Sign CLA for internal contributor
sign-ind            Sign CLA for individual contributor
sign-com            Sign CLA for company contributor
gen-conf            Generate cla-bot config

optional arguments:
-h, --help            show this help message and exit
```

It is called by the [GitHub workflows](#github-workflows) to perform the actual work. It also can be run manually to perform [maintenance tasks](#maintenance-tasks).

### GitHub workflows

This repo contains two GitHub workflows, [sign-individual.yml](.github/workflows/sign-individual.yml) and [sign-company.yml](.github/workflows/sign-company.yml).
These workflows have the `on: workflow_dispatch` trigger, so they can be invoked manually.
The idea is that these workflows function as a “quick-and-dirty” way for contributors to sign the appropriate CLA with minimal intervention from the OpenDP team.

Whenever a new contributor submits their first PR to any repo in the `opendp` organization, `cla-bot` will notice and post a message to the PR.
(This message comes from the [`.clabot`](.clabot) config file.)
The message directs the contributor to [our CLA page](https://docs.opendp.org/en/stable/developer/cla.html), which explains to the contributor how to  run the workflows and signing the CLA.

When the contributor runs the workflow, it will collect the contributor’s info in form fields, then run the [cla_tool.py](#cla_toolpytoolscla_toolpy) script.
The script will update the [config files](#files) and generate a separate PR (on **this** repo) to commit the config changes.
Someone on the OpenDP team will then need to perform two manual steps:

1. Merge the second PR, updating the `cla-bot` config.
2. Re-run the `cla-bot` validation on the first PR, by adding a comment containing the text `@clabot check`.

At that point, if everything has gone well, the contributor will be blessed, `cla-bot` will label the first PR `cla-signed`, and code review can proceed as normal.

## Maintenance Tasks

This setup is designed to be automated and low maintenance, but there may be some manual tasks required periodically.

### Adding internal contributors

As noted above, there’s a separate signature directory for internal (Harvard) contributors.
There’s no self-service web workflow for internal people to add themselves, so new entries must be added manually.
To do this, run the following:

```
$ python tools/cla_tool.py sign-int -g <GITHUB_ID> -n <CONTRIBUTOR_NAME> -a "ON FILE"
$ python tools/cla_tool.py gen-conf
```

Then commit the resulting changes back to this repo.

### Adding contributors manually

If someone is having problems with the self-service web workflow, they can be added manually, similar to internal people above:

```
$ # FOR INDIVIDUAL CONTRIBUTORS
$ python tools/cla_tool.py sign-ind -g <GITHUB_ID> -n <CONTRIBUTOR_NAME> -a "I AGREE"
$ # OR FOR COMPANY CONTRIBUTORS
$ python tools/cla_tool.py sign-com -g <GITHUB_ID> -n <CONTRIBUTOR_NAME> -a "I AGREE" -X <COMPANY_NAME> -N <REPRESENTATIVE_NAME> -A "I AGREE"
$ python tools/cla_tool.py gen-conf
```

Then commit the resulting changes back to this repo.

### Removing contributors

*TBD*. Need to check on the requirements around this.
If anyone does request to be removed, we’ll probably want to create another directory for these people, to track that their previous contributions were OK.

## Other

The sources for the CLA forms themselves live in the [OpenDP repository](https://github.com/opendp/opendp/tree/main/docs/cla).
There are instructions there for updating and publishing the CLA forms to the docs websiste.
