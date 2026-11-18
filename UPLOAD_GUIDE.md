# Upload this upgrade to your existing GitHub repository

The folder in this download is the complete replacement working tree. It does not include Git history, a Python environment, API keys or generated working databases. Your existing public repository has not been changed.

## 1. Open the package

1. Download and unzip `Solar_Grid_Recruiter_Ready.zip` on your computer.
2. Open the enclosed `Solar-Grid-Impact-Analyzer` folder.
3. Start with `README.md`. Results, methods and limitations are already written.

## 2. Create a review branch with GitHub Desktop

1. Open GitHub Desktop and sign in to your own GitHub account.
2. Choose **File → Clone repository → URL** and paste:
   `https://github.com/Balbir89/Solar-Grid-Impact-Analyzer.git`
3. Clone into a new local folder. This keeps the update separate from any older working copy.
4. Choose **Branch → New branch**, name it `portfolio/solar-grid-rebuild`, then create it from `main`.
5. Choose **Repository → Show in Finder** (or **Show in Explorer**).
6. Copy the **contents** of the downloaded project folder into this clone. Replace matching files. Include hidden files and folders: on macOS press **Command + Shift + .** to show `.github`, `.gitignore` and `.dockerignore`. Keep the clone's existing `.git` directory.
7. Remove the following retired files from the clone if they are present. Their original versions remain in Git history; the original dataset and one screenshot are already preserved under `data/reference/` and `docs/assets/` in this upgrade:

```text
1_Simulate_Energy_Data.ipynb
2_EDA_Pre_processing.ipynb
3_Feature_Engineering_Model_Training.ipynb
4_Deployment_App.html
weather_data_fetcher_py.ipynb
simulated_eon_grid_data.csv
dashboard.png
images/dashboard.png
images:dashboard.png
sql/solar_grid_kpi_analysis.sql
```

8. Return to GitHub Desktop. Review **Changes**: you should see the package, SQL, tests, docs, workflows, Dockerfile and replacement README.
9. Enter the commit summary **Rebuild solar analytics with SQL, causal forecasting and battery economics**. Commit to the new branch.
10. Click **Publish branch**, then **Create Pull Request**. Use the title **Rebuild solar analytics as a reproducible investment case study**.
11. On GitHub, wait for **Validate analytics** to pass before merging. It includes the Docker check that could not be run in the preparation environment.

Do not upload the ZIP itself as the repository source. GitHub needs the extracted files and their folder structure.

## 3. Set the repository description and topics

On the repository's **Code** page, use the gear beside **About**.

**Description:**

Python and SQL energy analytics with leakage-tested load forecasting, constrained battery dispatch, investment sensitivity analysis and a reproducible dashboard.

**Topics:**

`python` `sql` `sqlite` `data-analysis` `time-series` `forecasting` `scikit-learn` `solar-energy` `battery-storage` `financial-modeling` `docker` `github-actions`

## 4. Publish the dashboard after merging

1. Open **Settings → Pages**.
2. Under **Build and deployment**, select **GitHub Actions** as the source.
3. Open **Actions → Publish dashboard → Run workflow**, select `main`, and run it.
4. Wait for a successful deployment. Use the URL returned by the deployment, then put that URL in the repository's **About → Website** field.
5. Open the deployed page. Change the month, capacity and capital-cost selections. Check the page on your phone too.

The expected project URL is `https://balbir89.github.io/Solar-Grid-Impact-Analyzer/`, but it is **not claimed to be live** until deployment succeeds.

## 5. One required account action

Revoke or rotate the weather API credential previously committed in `weather_data_fetcher_py.ipynb`. Deleting the notebook does not disable the old credential. This upgrade does not require any API key. See `docs/SECURITY.md`.

## Local preview

From the extracted project folder, run `python3 simple_server.py` and open `http://localhost:8000`. That serves the committed dashboard without installing analytics packages. For a complete analytical rebuild, follow the Python 3.12 commands in `README.md`.

See `docs/validation-status.md` for the checks completed and the remaining remote checks.
