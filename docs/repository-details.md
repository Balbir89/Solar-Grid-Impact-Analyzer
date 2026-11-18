# Repository details

**Description:** Python and SQL energy analytics with leakage-tested load forecasting, constrained battery dispatch, investment sensitivity analysis and a reproducible dashboard.

**Topics:** `python`, `sql`, `sqlite`, `data-analysis`, `time-series`, `forecasting`, `scikit-learn`, `solar-energy`, `battery-storage`, `financial-modeling`, `docker`, `github-actions`

Set these in the repository's About settings after merging the reviewed changes.

## Publishing the dashboard

1. Merge the reviewed pull request after the Validate analytics workflow passes.
2. Open repository Settings → Pages. Under Build and deployment, choose **GitHub Actions**.
3. Open Actions → **Publish dashboard** → Run workflow, selecting **main**.
4. Open the deployment URL returned by that successful run.

The intended site URL is https://balbir89.github.io/Solar-Grid-Impact-Analyzer/ . It is not claimed to be live until the Pages deployment succeeds.

CI runs on pull requests and pushes to main or portfolio branches. It tests Python/SQL, reconstructs the evidence, and builds/smoke-tests Docker. CD is intentionally an explicit workflow run and accepts main only. No paid hosting account is required.
