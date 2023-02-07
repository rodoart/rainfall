import aiohttp
import asyncio
import aiofiles

from pathlib import Path

# Only for notebooks
#import nest_asyncio
#nest_asyncio.apply()

# Only for Windows
from sys import platform
if  platform.startswith('win'):
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


mozilla = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'
}

from typing import List

def asyncronous_download_from_urls(
    url_list: list[str],
    download_dirs: List[Path],
    limit: int = 3,
    http_ok: List[int] = [200],
    header: dict = mozilla,
    encoding: str = 'utf-8'
) -> None:
    

    """Simultaneously downloads url lists. Only plain text files allowed.

    Args:
        url_list: List of urls to download.

        download_dirs: List of file destinies

        limit: of simultaneous downloads. Default 3.    

        http_ok: List of allowed http codes. Default is [200]

        header: Provide the header, following the usual syntax of requests library.

        encoding: Encoding of the text of the web page or file.

    Returns:
        A function that returns the path relative to a directory that can
        receive `n` number of arguments for expansion.
    """


    async def scrape(url_list, download_dirs):
        tasks = list()
        sem = asyncio.Semaphore(limit)

        async with aiohttp.ClientSession(trust_env=True, headers=header) as session:
            for url, download_dir in zip(url_list, download_dirs):
                task = asyncio.ensure_future(scrape_bounded(url, download_dir,
                                                            sem, session))
                tasks.append(task)

            result = await asyncio.gather(*tasks)

        return result

    async def scrape_bounded(url, download_dir, sem, session):
        async with sem:
            new_line = await scrape_one(url, download_dir, session)
            return new_line


    async def scrape_one(url, download_dir, session):
        file_name = url.rsplit('/', 1)[-1]

        try: 
            async with session.get(url, verify_ssl=False) as response:
                content = await response.text(encoding=encoding)
                
                # Saving files.
                async with aiofiles.open(download_dir.joinpath(file_name),
                                        mode = 'w') as f:
                    await f.write(content)

        except aiohttp.client_exceptions.ClientConnectorError:
            print('Scraping  failed due to the connection problem', url)
            return False

        if response.status not in http_ok:
            print('Scraping failed due to the return code ', url, response.status)
            return False        

        return file_name


    loop = asyncio.get_event_loop()
    lines = loop.run_until_complete(scrape(url_list, download_dirs))