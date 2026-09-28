"""
collect_jobs.py
Collects data-role job postings in India from the Adzuna API.
Output: data/raw/jobs_raw_<date>.json and data/raw/jobs_<date>.csv
"""

import os
import json
import time
from datetime import date

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/{page}"
ROLES = [
    "data analyst",
    "business analyst",
    "data scientist",
    "data engineer",
    "machine learning engineer",
    "ai engineer",
]
RESULTS_PER_PAGE = 50
MAX_PAGES = 8          # 8 pages x 50 = up to 400 jobs per role
SLEEP_SECONDS = 3      # stay well under the free-tier rate limit

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def fetch_page(role: str, page: int) -> list:
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what_phrase": role,
        "results_per_page": RESULTS_PER_PAGE,
        "content-type": "application/json",
    }
    resp = requests.get(BASE_URL.format(page=page), params=params, timeout=30)
    if resp.status_code != 200:
        print(f"  ! {role} page {page}: HTTP {resp.status_code} - {resp.text[:150]}")
        return []
    return resp.json().get("results", [])


def flatten(job: dict, search_role: str) -> dict:
    return {
        "job_id": job.get("id"),
        "search_role": search_role,
        "title": job.get("title"),
        "company": (job.get("company") or {}).get("display_name"),
        "location": (job.get("location") or {}).get("display_name"),
        "location_area": " > ".join((job.get("location") or {}).get("area", [])),
        "category": (job.get("category") or {}).get("label"),
        "contract_time": job.get("contract_time"),
        "contract_type": job.get("contract_type"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "salary_is_predicted": job.get("salary_is_predicted"),
        "created": job.get("created"),
        "description": job.get("description"),
        "url": job.get("redirect_url"),
    }


def main():
    if not APP_ID or not APP_KEY:
        raise SystemExit("Missing ADZUNA_APP_ID / ADZUNA_APP_KEY in .env")

    all_raw, rows = [], []
    for role in ROLES:
        print(f"Collecting: {role}")
        for page in range(1, MAX_PAGES + 1):
            results = fetch_page(role, page)
            if not results:
                break
            all_raw.extend(results)
            rows.extend(flatten(j, role) for j in results)
            print(f"  page {page}: {len(results)} jobs")
            time.sleep(SLEEP_SECONDS)

    today = date.today().isoformat()
    with open(os.path.join(RAW_DIR, f"jobs_raw_{today}.json"), "w", encoding="utf-8") as f:
        json.dump(all_raw, f, ensure_ascii=False)

    df = pd.DataFrame(rows)
    before = len(df)
    df = df.drop_duplicates(subset="job_id")
    df["collected_on"] = today
    out_path = os.path.join(RAW_DIR, f"jobs_{today}.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")

    print(f"\nDone. {before} rows fetched, {len(df)} unique jobs saved to {out_path}")
    print(df["search_role"].value_counts())


if __name__ == "__main__":
    main()