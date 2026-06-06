import asyncio
import os
import json
from rnet import Impersonate, Client, Proxy, BlockingClient
from tenacity import retry, stop_after_attempt


class Extractor:
    def __init__(self) -> None:

        self.proxy = os.getenv("mobileproxyuk")
        print("mobileproxyuk =", self.proxy)

        proxies = None

        if self.proxy:
            if "://" in self.proxy and ":" in self.proxy.split("://")[-1]:
                try:
                    proxies = [
                        Proxy.http(self.proxy),
                        Proxy.https(self.proxy)
                    ]
                except Exception as e:
                    print("⚠️ Proxy invalid, running without proxy:", e)
                    proxies = None
            else:
                print("⚠️ Proxy format invalid, ignoring proxy")

        self.session = Client()
        self.session.update(
            impersonate=Impersonate.Firefox135,
            proxies=proxies
        )

        self.blocking = BlockingClient()
        self.blocking.update(
            impersonate=Impersonate.Firefox135,
            proxies=proxies
        )

    @retry(stop=stop_after_attempt(3))
    async def fetch(self, url):
        print(f"Fetching {url}")
        resp = await self.session.get(url)

        try:
            return await resp.json()
        except Exception:
            return await resp.text()

    async def fetch_all(self, urls):
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return list(zip(urls, results))

    def save_to_json(self, data, filename="output.json"):
        """Save scraped data to JSON file"""
        cleaned = []

        for url, result in data:
            # convert non-serializable errors
            if isinstance(result, Exception):
                result = str(result)

            cleaned.append({
                "url": url,
                "data": result
            })

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=4)

        print(f"✅ Data saved to {filename}")

    @retry(stop=stop_after_attempt(3))
    def blocking_fetch(self, url):
        resp = self.blocking.get(url)
        print(f"Blocking fetch for {url} returned status {resp.status_code}")

        try:
            return resp.json()
        except Exception:
            return resp.text()


async def main():
    urls = [
        "https://www.adidas.co.uk/api/products/HQ7551",
        "https://www.adidas.co.uk/api/products/HQ7551?sitePath=uk&locale=en-GB"
    ]

    e = Extractor()

    data = await e.fetch_all(urls)

    for url, result in data:
        print(f"\nURL: {url}\nData: {result}\n")

    # ✅ SAVE TO JSON FILE
    e.save_to_json(data, "adidas_products.json")


if __name__ == "__main__":
    asyncio.run(main())