import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)


def test_dashboard_is_executable_html():
    parser = Tags()
    parser.feed((ROOT / "docs/index.html").read_text())
    assert "script" in parser.tags
    assert "svg" in parser.tags


def test_sql_is_plain_sql():
    for path in (ROOT / "sql").glob("*.sql"):
        assert "```" not in path.read_text()


def test_no_hardcoded_api_credentials_or_notebook_outputs():
    for folder in ("src", "notebooks"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and path.suffix in (".py", ".ipynb"):
                content = path.read_text()
                assert not re.search(
                    r'(?i)(?:api_key|appid)\s*[=:]\s*["\x27][a-z0-9]{20,}', content
                )
                if path.suffix == ".ipynb":
                    notebook = json.loads(content)
                    assert all(not cell.get("outputs") for cell in notebook["cells"])


def test_snapshot_is_honest_about_data():
    path = ROOT / "reports/metrics.json"
    if path.exists():
        report = json.loads(path.read_text())
        assert report["scenario"].startswith("Synthetic")
        assert report["forecast"]["horizon_hours"] == 1
        assert report["quality"]["balance_failures"] == 0
