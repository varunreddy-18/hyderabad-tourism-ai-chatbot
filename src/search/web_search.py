from ddgs import DDGS
import requests
from lxml import html
from urllib.parse import urlparse


class WebSearch:

    def _fetch_page_text(self, url, timeout=5):
        """Attempt to fetch page HTML and extract readable text using lxml."""
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "HyderabadTourismBot/1.0"})
            if resp.status_code != 200:
                return ""
            doc = html.fromstring(resp.content)
            # Extract textual content; join paragraph texts but avoid scripts/styles
            paragraphs = doc.xpath('//p//text()') or doc.xpath('//*//text()')
            text = "\n".join([p.strip() for p in paragraphs if p.strip()])
            # keep only a reasonable slice
            if len(text) > 2000:
                text = text[:2000]
            return text
        except Exception:
            return ""

    def _normalize_url(self, url):
        try:
            p = urlparse(url)
            return p.scheme + "://" + p.netloc + p.path
        except Exception:
            return url

    def search(self, query, max_results=5):

        results = []
        seen_urls = set()
        seen_titles = set()

        # Build a more targeted DDGS query for recommendation or locality-sensitive searches
        q = query.strip()
        q_lower = q.lower()

        ddgs_query = q

        try:
            # Heuristic: if user is asking about restaurants/food, bias the query toward recommendation pages
            if any(k in q_lower for k in ["restaurant", "restaurants", "cafe", "cafes", "food", "eat", "where to eat"]):
                # If the user already specified a city (e.g., hyderabad) keep it; otherwise add Hyderabad to focus results
                if "hyderabad" not in q_lower and "charminar" not in q_lower:
                    ddgs_query = f"{q} Hyderabad recommendations OR " + q
                else:
                    ddgs_query = q
                # prefer pages that include lists, reviews, or 'best' indicators
                ddgs_query = ddgs_query + " (best OR top OR " + "recommend OR review)"

            # If user is asking about timings / today / open now, prefer queries that include 'open now', 'timings'
            elif any(k in q_lower for k in ["today", "timings", "open now", "open", "current", "latest"]):
                if "hyderabad" not in q_lower and "charminar" not in q_lower:
                    ddgs_query = f"{q} Hyderabad"
                else:
                    ddgs_query = q

            # Otherwise use the user's query verbatim
            else:
                ddgs_query = q

            # Use DDGS with the constructed ddgs_query
            with DDGS() as ddgs:
                search_results = list(
                    ddgs.text(
                        ddgs_query,
                        max_results=max_results
                    )
                )

                for result in search_results:
                    title = result.get("title", "")
                    body = result.get("body", "") or ""
                    url = result.get("href", "") or ""

                    norm = self._normalize_url(url)
                    if norm in seen_urls:
                        continue
                    seen_urls.add(norm)

                    # Skip completely empty hits
                    if not title and not body and not url:
                        continue

                    # If DDGS body/snippet is empty or very short, try to fetch the page
                    fetched = ""
                    if (not body or len(body.strip()) < 200) and url and url.startswith("http"):
                        fetched = self._fetch_page_text(url)
                    if fetched:
                        body = fetched
                        source_type = "page"
                    else:
                        # mark whether the content came only from DDGS snippet
                        source_type = "snippet"

                    # dedupe near-duplicate titles
                    title_norm = (title or "").strip().lower()
                    if title_norm in seen_titles:
                        # if same title but we fetched a fuller page text, prefer that; otherwise skip
                        if source_type == "page":
                            # allow it and continue; but keep seen_titles so we don't add many duplicates
                            pass
                        else:
                            continue
                    seen_titles.add(title_norm)

                    # Keep results only if we have at least some content or a URL
                    if not body and not url:
                        continue

                    results.append({
                        "title": title,
                        "body": body,
                        "url": url,
                        "source_type": source_type
                    })

        except Exception as e:
            print("Web Search Error:", e)

        # return both the constructed ddgs_query and results so callers can log diagnostics
        return {"search_query": ddgs_query, "results": results}


if __name__ == "__main__":

    searcher = WebSearch()

    out = searcher.search(
        "Charminar timings today"
    )

    results = out.get("results", [])
    print("\nSEARCH QUERY:", out.get("search_query"))
    print("\nRESULT COUNT:", len(results))

    for r in results:
        print("\n" + "=" * 80)
        print("TITLE:", r.get("title"))
        print("SOURCE_TYPE:", r.get("source_type"))
        print("BODY:", (r.get("body") or "")[:300])
        print("URL:", r.get("url"))