# CI Data Source Integration Pattern

confidence: high
discovered_by: Farnsworth (TechCrunch integration), Bender (implementation)
date: 2026-05-19

## Pattern

Scripts often exist but aren't wired into the CI pipeline. Prevent script-orphaning by following this pattern:

1. **Define DataSource adapter** with standardized interface:
   - `get_name()` → source name (e.g., "techcrunch", "github")
   - `get_rate_limits()` → rate limit policy
   - `crawl(since, until)` → structured output (list of dicts)

2. **Wire script into workflow** immediately after creation:
   - Add explicit step in CI that calls the script
   - Set input parameters (dates, topics, output paths)
   - Capture exit codes and log output
   - Integrate output into next pipeline stage

3. **Document integration point** in PRD:
   - Which workflow file calls it
   - Input parameters and environment variables
   - Output format and schema
   - Rate limit behavior and retry policy

4. **Test the wire** before PR merge:
   - Run the workflow end-to-end
   - Verify script actually executes (not skipped by conditions)
   - Check output format matches downstream consumer expectations

## When to Use

- Creating new data crawlers (RSS, APIs, GitHub)
- Adding new analysis stages (preprocessing, enrichment)
- Integrating external tools or scripts into CI/CD
- Multi-stage pipelines where data flows from stage to stage

## Implementation

### DataSource Adapter Pattern

```python
class TechCrunchSource:
    """TechCrunch RSS data source following the DataSource protocol."""

    def get_name(self) -> str:
        return "techcrunch"

    def get_rate_limits(self) -> dict:
        return {"requests_per_minute": 10}

    def crawl(
        self,
        since: datetime,
        until: datetime,
        feed_url: str = FEED_URL,
    ) -> list[dict[str, Any]]:
        """Crawl TechCrunch RSS feed and return structured articles."""
        feed = fetch_feed(feed_url)
        articles: list[dict[str, Any]] = []

        for entry in feed.entries:
            pub_date = parse_published_date(entry)
            if pub_date is None or pub_date < since or pub_date >= until:
                continue

            article = {
                "title": getattr(entry, "title", ""),
                "url": getattr(entry, "link", ""),
                "published_at": iso_timestamp(pub_date),
                "categories": extract_categories(entry),
                "summary": extract_summary(entry),
                "github_links": extract_github_urls(entry),
                "entities": extract_entities(entry.title),
            }
            article["relevance_score"] = compute_relevance_score(article)
            articles.append(article)

        return articles
```

### Workflow Integration

```yaml
crawl-techcrunch:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Crawl TechCrunch RSS
      env:
        TOPIC: ai-ml
        OUTPUT: data/raw/ai-ml/${{ needs.weekly.outputs.week }}-techcrunch.json
      run: python scripts/techcrunch_crawler.py \
        --topic "$TOPIC" \
        --output "$OUTPUT" \
        --since "${{ needs.weekly.outputs.since }}" \
        --until "${{ needs.weekly.outputs.until }}"
    
    - name: Upload crawl results
      uses: actions/upload-artifact@v3
      with:
        name: techcrunch-crawl
        path: data/raw/
        retention-days: 7
```

### Output Schema Documentation

```markdown
## TechCrunch Crawler Output

**File:** `data/raw/{topic}/{week}-techcrunch.json`

**Schema:**
```json
{
  "week": "2026-W21",
  "source": "techcrunch",
  "crawled_at": "2026-05-19T19:31:31Z",
  "articles": [
    {
      "title": "...",
      "url": "https://techcrunch.com/...",
      "published_at": "2026-05-19T12:00:00Z",
      "categories": ["ai", "ml"],
      "summary": "...",
      "github_links": ["https://github.com/owner/repo"],
      "entities": ["OpenAI", "Anthropic"],
      "relevance_score": 0.85
    }
  ],
  "metadata": {
    "total_articles": 250,
    "relevant_articles": 45,
    "github_links_found": 12
  }
}
```
```

## Examples

From `scripts/techcrunch_crawler.py`:

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl TechCrunch RSS feed for SquadScope"
    )
    parser.add_argument("--topic", default="general")
    parser.add_argument("--output", default=None)
    parser.add_argument("--since", default=None)
    parser.add_argument("--until", default=None)
    args = parser.parse_args(argv)

    now = datetime.now(UTC)
    since = (
        datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=UTC)
        if args.since
        else now - timedelta(days=7)
    )
    until = (
        datetime.strptime(args.until, "%Y-%m-%d").replace(tzinfo=UTC)
        if args.until
        else now
    )

    source = TechCrunchSource()
    articles = source.crawl(since=since, until=until)
    output = build_output(articles, crawled_at=now)

    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = raw_dir(args.topic)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{week_slug(now)}-techcrunch.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Crawled {output['metadata']['total_articles']} articles → {out_path}")
    return 0
```

### Config-Driven Parallel RSS Sources

For small sets of external RSS feeds in the weekly Actions pipeline, prefer one config file plus bounded in-process parallel fetches over one job per feed. This avoids repeated checkout/setup/artifact overhead, keeps a single enrichment artifact contract, and lets maintainers add or remove sources without editing workflow topology.

## Notes

- Standardize output schemas across all data sources for seamless pipeline integration
- Test scripts locally before adding to workflow to catch parameter/path issues
- Document rate limit behavior so workflow can be tuned for cost/speed tradeoffs
- Use artifact uploads to pass data between workflow jobs (cleaner than file system)
