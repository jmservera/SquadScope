# Exponential Backoff with Jitter and Retry-After Headers

confidence: high
discovered_by: Farnsworth, Bender (GitHub crawler phase)
date: 2026-05-19

## Pattern

Implement resilient HTTP retry logic that combines:
1. Exponential backoff (2^attempt, capped at 60s) for deterministic delay
2. Random jitter (0.3–1.7s) to prevent thundering herd
3. Server-provided Retry-After header (HTTP 429, 503) takes precedence
4. Secondary rate limit detection with enforced minimum backoff (8s + 0.0–5s jitter)
5. Rate limit state tracking (X-RateLimit-Remaining, X-RateLimit-Reset)

## When to Use

- External HTTP requests to rate-limited APIs (GitHub GraphQL, RSS feeds, third-party crawlers)
- Handling HTTP 429, 500, 502, 503, 504 responses
- Distributed systems where retry storms can amplify load (thundering herd)
- API quota exhaustion scenarios with server-provided retry guidance

## Implementation

```python
# Exponential backoff calculation
base_delay = min(2**attempt, 60)  # Cap at 60 seconds
jitter = random.uniform(0.3, 1.7)
delay = base_delay + jitter

# Honor Retry-After header (seconds)
if "Retry-After" in response_headers:
    retry_after = float(response_headers["Retry-After"])
    delay = max(retry_after, 1.0)

# Secondary rate limit: enforce minimum
if "secondary rate limit" in response_body.lower():
    delay = max(delay, 8.0 + random.uniform(0.0, 5.0))

# Cap total delay to prevent indefinite waits
delay = min(delay, max_delay_seconds)

# Sleep and retry
time.sleep(delay)
```

## Examples

From `scripts/crawl.py` (GitHub GraphQL crawler):

```python
def _sleep_before_retry(
    self,
    attempt: int,
    headers: dict[str, str] | None,
    body: str,
    query: str,
    retry_limit: int,
    max_delay_seconds: float,
) -> None:
    reset_delay = self._reset_delay(headers)
    retry_after = None
    if headers and headers.get("Retry-After"):
        try:
            retry_after = max(float(headers["Retry-After"]), 1.0)
        except ValueError:
            retry_after = None
    
    base_delay = min(2**attempt, 60)
    jitter = random.uniform(0.3, 1.7)
    delay = retry_after or reset_delay or (base_delay + jitter)
    if "secondary rate limit" in body.lower():
        delay = max(delay, 8.0 + random.uniform(0.0, 5.0))
    delay = min(delay, max_delay_seconds)
    
    log(f"Retrying {query} in {delay:.1f}s (attempt {attempt + 1}/{retry_limit}).")
    time.sleep(delay)
```

State tracking pattern:
```python
self.rate_limit_reset = max(self.rate_limit_reset or 0, int(time.time() + retry_after))
```

Retryable status codes:
```python
RETRYABLE_STATUSES = {403, 429, 500, 502, 503, 504}
```
