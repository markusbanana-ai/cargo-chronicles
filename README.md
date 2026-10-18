# Cargo Chronicles

Road transport and shipping news from free sources in one place, with every term explained.
Live at <https://markusbanana-ai.github.io/cargo-chronicles/> once GitHub Pages is turned on (step 4).

The site is a set of plain files: no server, no database, no cookies. A small program runs every three
hours on GitHub, fetches the news, and saves it into the site. Hosting on GitHub Pages is free.

---

## Set it up (about 15 minutes, all free)

### 1. Create a GitHub account
Go to <https://github.com/signup> and create an account. Your username becomes part of the web
address, e.g. `markusbanana-ai.github.io/cargo-chronicles`.

### 2. Create a repository
1. Click **+** (top right) → **New repository**.
2. Name it `cargo-chronicles` (or anything you like).
3. Choose **Public**. (GitHub Pages is free for public repositories. Nothing in this project is private.)
4. Click **Create repository**.

### 3. Put the files in it
**Easiest:** connect GitHub to Claude and tell Claude the repository name — Claude can push the files for you.

**By hand:** on the repository page, click **uploading an existing file**, drag in everything from the
project folder and click **Commit changes**.
Note: some computers hide folders that start with a dot. If `.github/workflows/update.yml` did not come
along, click **Add file → Create new file**, type `.github/workflows/update.yml` as the name, paste the
file's content and commit.

### 4. Turn on the website
1. Repository → **Settings** → **Pages**.
2. Under *Build and deployment*, choose **Deploy from a branch**.
3. Branch: **main**, folder: **/docs** → **Save**.
4. After a minute or two the address appears at the top of that page.

### 5. Fetch the first real news
1. Repository → **Actions** tab. If asked, click **I understand my workflows, go ahead and enable them**.
2. Click **Update news** → **Run workflow** → **Run workflow**.
3. Wait about a minute. The sample headlines are replaced by live ones, and from now on it updates
   itself every three hours.

If the run fails with a permissions error: **Settings → Actions → General → Workflow permissions →
Read and write permissions → Save**, then run it again.

If updates ever stop (GitHub pauses scheduled jobs in quiet repositories), open the **Actions** tab and
click **Enable workflow**.

---

## Change things yourself

All of these can be edited directly on GitHub (open the file, click the pencil icon, commit):

| File | What it controls |
|---|---|
| `docs/data/sources.json` | Which news sources are read. Set `"enabled": false` to pause one. |
| `docs/data/segments.json` | The sections, the words that sort articles into them, and the "How to read this news" tips. |
| `docs/data/glossary.json` | All glossary terms: definition (`def`), example (`ex`), Norwegian name (`no`) and the words that trigger it (`m`). In `m`, a leading `=` means "match exact capitals" (for abbreviations like `=CMR`). |
| `docs/data/scenarios.json` | The events in Analytics → Cause & effect. |
| `docs/data/insights.json` | The situations behind “How to read this story” in each article and the “What is driving this section” themes. Generated from a script; small text edits are fine. |
| `docs/data/sea.json` | Shipping routes, chokepoints and what-if detours on the shipping map. |
| `docs/data/roadinfo.json` | Road descriptions, mountain passes, ferries, border crossings and ferry links on the road map. |
| `docs/data/roads.json` | Traffic counts from Statens vegvesen. Written automatically once a month by the **Update road traffic data** job; do not edit by hand. |

JSON is picky: keep the quotes and commas exactly as the surrounding lines. GitHub shows an error if
something is wrong, and you can always undo from the file's **History**.

---

## Privacy and legal (already handled)

- **No cookies, no tracking, no third-party requests.** Fonts and chart code are stored on the site
  itself, so visitors' browsers never contact Google or other companies. No cookie banner is needed.
  The only thing stored in the browser is the light/dark choice, and only if the visitor changes it.
- **Copyright.** The site shows the headline, the short summary each source publishes in its feed
  (max 240 characters), and a link. It never copies full articles or images.
- **Not advice.** The About page says the explanations and models are for learning.
- **Hidden from search engines** while it is just for you (a `noindex` line in `docs/index.html`).

### Before you share it with others
1. Remove the `<meta name="robots" ...>` line in `docs/index.html` if you want it findable on Google.
2. Add a contact email to the About page (in `docs/assets/app.js`, search for "Copyright and corrections"),
   so publishers can ask for changes.
3. Optional: buy a domain (a `.no` costs a few hundred kroner a year via a Norid registrar such as
   Domeneshop) and add it under **Settings → Pages → Custom domain**. Tick **Enforce HTTPS**.
4. If you ever add sign-ups, a newsletter or analytics, you will need a privacy policy and, for
   analytics cookies, a consent banner.

---

## How it works

```
.github/workflows/update.yml   runs every 3 hours on GitHub
        │
        ▼
scripts/update.py              reads feeds → sorts into sections → finds glossary terms
        │                      → translates other languages → fetches Brent & NOK rates
        ▼
docs/data/*.json               the data the website reads
.github/workflows/roads.yml    monthly: scripts/build_roads.py fetches road traffic (NVDB) into docs/data/roads.json
docs/index.html + assets/      the website itself (served by GitHub Pages)
```

`scripts/update.py` uses only Python's standard library. To run it on your own computer:
`python scripts/update.py` (or `python scripts/update.py --offline` to re-sort without fetching).

Data: news from the listed sources; Brent crude from the U.S. EIA via FRED; exchange rates from
Norges Bank; free translation via MyMemory; road traffic from Statens vegvesen (NVDB, NLOD licence);
chokepoint oil volumes from the EIA; coastlines from Natural Earth; map maths by d3-geo (ISC). Fonts: Barlow and IBM Plex (SIL Open Font License).
Charts: Chart.js (MIT).
