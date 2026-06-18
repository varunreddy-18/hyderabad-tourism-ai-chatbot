from ddgs import DDGS


class WebSearch:

    def search(self, query, max_results=5):

        results = []

        try:

            with DDGS() as ddgs:

                search_results = list(
                    ddgs.text(
                        query,
                        max_results=max_results
                    )
                )

                for result in search_results:

                    results.append({
                        "title": result.get("title", ""),
                        "body": result.get("body", ""),
                        "url": result.get("href", "")
                    })

        except Exception as e:

            print("Web Search Error:", e)

        return results


if __name__ == "__main__":

    searcher = WebSearch()

    results = searcher.search(
        "Charminar timings today"
    )

    print("\nRESULT COUNT:", len(results))

    for r in results:

        print("\n" + "=" * 80)
        print("TITLE:", r["title"])
        print("BODY:", r["body"])
        print("URL:", r["url"])