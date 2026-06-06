import asyncio
import os
from rnet import Impersonate, Client, Proxy, BlockingClient
from tenacity import retry, stop_after_attempt


class Extractor:
    def __init__(self) -> None:

        self.proxy = os.getenv("mobileproxyuk")
        print("mobileproxyuk =", self.proxy)

        # Proxy setup (SAFE)
        proxies = None

        if self.proxy:
            # basic validation to avoid InvalidPort crash
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

        # Async client
        self.session = Client()
        self.session.update(
            impersonate=Impersonate.Firefox135,
            proxies=proxies
        )

        print("Session created")

        # Blocking client
        self.blocking = BlockingClient()
        self.blocking.update(
            impersonate=Impersonate.Firefox135,
            proxies=proxies
        )

    @retry(stop=stop_after_attempt(3))
    async def fetch(self, url):
        print(f"Fetching {url}")
        resp = await self.session.get(url)

        # safer JSON handling
        try:
            return await resp.json()
        except Exception:
            return await resp.text()

    async def fetch_all(self, urls):
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return list(zip(urls, results))

    @retry(stop=stop_after_attempt(3))
    def blocking_fetch(self, url):
        resp = self.blocking.get(url)
        print(f"Blocking fetch for {url} returned status {resp.status_code}")

        try:
            return resp.json()
        except Exception:
            return resp.text


async def main():
    urls = [
        "https://www.adidas.co.uk/api/products/HQ7551",
        "https://www.adidas.co.uk/api/products/HQ7551?sitePath=uk&locale=en-GB"
    ]

    e = Extractor()

    data = await e.fetch_all(urls)

    for url, result in data:
        print(f"\nURL: {url}\nData: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())