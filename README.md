# LinkedOut

LinkedOut publishes a static, searchable archive of LinkedIn posts at
<https://linkedout.cz/>. The public site currently has one person, `grumpy`
(Pavel Simerda), and the deployed archive ends at **2024-09-11 22:48:07**.

## How It Works

There are two repositories:

- This repository contains the generator, templates, deployment script, and
  dependency lock file.
- The separate `unrecruitment/data` repository contains private LinkedIn
  exports and the generated `users/*/posts.yaml` files. It is cloned into this
  repository as `data/` during deployment via `GIT_DATA_REPO`.

The data flow is:

1. Request a complete LinkedIn data export.
2. `data/update.py` reads the export's shares CSV with pandas, removes
   duplicate dates, removes NaN fields, and writes `posts.yaml`.
3. `generate.py` reads each `data/users/*/posts.yaml` and `name` file.
4. Jinja templates produce static HTML under `build_dir/static/`.
5. Netlify publishes that directory. The site is generated from GitHub; the
   deployment script optionally fetches the data repository first.

The generated site has an index at `/`, and a post list at
`/out/<user>/posts/`. Each post links back to its LinkedIn post and has a
date-based anchor. The browser-side keyword search requires every entered
space-separated keyword to occur in a post.

## Updating The Archive

Keep LinkedIn exports out of both Git repositories. They contain personal
data. The root `.gitignore` also excludes generated output.

For an export in the format the updater currently understands:

```sh
cd data
./update.py ../Complete_LinkedInDataExport_MM-DD-YYYY.zip
git diff
git diff --stat
git add users/<user>/posts.yaml
git commit -m "update posts from LinkedIn export"
git push
```

Do not treat this as an append-only operation. LinkedIn can revise the text,
links, or metadata of posts that are already in the YAML. Before committing,
inspect the complete diff, including older dates, and check at least:

- the number of records before and after;
- the oldest and newest dates;
- changes to records before the previous newest date;
- deleted records, duplicate timestamps, and changes to `ShareLink`;
- meaningful text or visibility changes that affect the public archive.

For a quick date-range check, run this from the project root before and after
the update (using the appropriate data path):

```sh
python3 - <<'PY'
import yaml
with open('data/users/grumpy/posts.yaml') as stream:
    posts = yaml.safe_load(stream)['posts']
dates = sorted(posts)
print(len(dates), dates[0], dates[-1])
PY
```

Record important retroactive changes in the data-repository commit message
body, or in a changelog if one is introduced. A commit that only says
"update posts" is not enough when an old post changed. If the diff is
unexpected, stop before pushing and compare the source CSV and the previous
YAML. The exact policy for retaining or explaining LinkedIn's historical
edits is still undecided; see **Decisions To Fill In**.

The updater runs once for every person under `data/users/`; when an argument
is supplied, it applies that same archive to each person. For multiple people,
confirm that this is intended before running it. The no-argument form reads
the latest archive already stored below each user directory and rewrites the
YAML file:

```sh
cd data
./update.py
```

After updating data, test the generator from the project root:

```sh
pipenv sync
pipenv run ./generate.py
python3 -m http.server --directory build_dir/static/
```

Open `http://localhost:8000/`. `make` is a shortcut for generation, and
`make httpserver` generates and starts the local server. The `Makefile`'s
stylesheet symlink is a legacy local-development detail; deployment copies
`overlay/` into the build instead.

## Deployment

Netlify runs `deploy.sh`. It:

1. Clones or fast-forwards `GIT_DATA_REPO` into `data/` when that variable is
   set.
2. Installs/synchronizes Pipenv dependencies.
3. Runs the generator.
4. Copies `overlay/` (privacy page and favicon) into the generated site.

The repository has no `netlify.toml`; the Netlify site configuration therefore
needs to point at `deploy.sh` and publish `build_dir/static`. The current
deployment settings and the exact data-repository URL are not recorded here.

## Current Export Status

The untracked export supplied with this checkout is
`Complete_LinkedInDataExport_07-06-2026.zip`. It contains 2,123 shares through
`2026-07-05 08:54:16`, but LinkedIn names its CSV `Shares_551084893.csv`.
`data/linkedin/archives.py` now locates the single CSV whose filename begins
with `Shares`, while still supporting the old exact `Shares.csv` name. It
fails explicitly if no shares CSV or more than one candidate is present.
The local update produced 2,119 unique posts through that date. The four-row
difference is due to duplicate timestamps removed by the updater.

## Decisions To Fill In

These choices were not recoverable from the repository and should be settled
before the next publishing run:

- Netlify site name/account, build command, publish directory, and the exact
  `GIT_DATA_REPO` value.
- Whether the data repository is intentionally public or must remain private,
  and who is allowed to trigger a deployment.
- Whether a new export should replace the existing archive completely or be
  merged with prior YAML while preserving posts missing from the export.
- Whether historical changes found during an update should be accepted as
  authoritative, manually reviewed one by one, or tracked in a separate
  changelog; define the minimum detail required for that record.
- Whether the updater's current `Shares*.csv` matching rule is sufficient if
  LinkedIn supplies more than one shares-like file in a future export.
- Whether posts with missing visibility or other metadata should be published;
  the visibility filter is currently only a TODO in `generate.py`.
- Whether generated `build_dir/` should remain local-only or be published as
  a separate artifact for inspection.
- How to handle a post collision when two posts have the same second-level
  timestamp, since that timestamp is used as the HTML id.

## Important Files

- `generate.py`: converts YAML data into static HTML.
- `data/update.py`: converts a LinkedIn export into per-user YAML.
- `data/linkedin/archives.py`: ZIP/CSV parsing and pandas data handling.
- `templates/`: page and post-list templates.
- `deploy.sh`: Netlify build entry point.
- `overlay/`: files copied into the final static site.
- `Pipfile` / `Pipfile.lock`: Python dependencies.
