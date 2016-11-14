import asyncio
import aiohttp
import aiofiles
import logging
import os
import time

logger = logging.getLogger(__name__)

CHUNK_SIZE = 128


def get_timestamp():
    """Wrapper to be able to mock time.time"""
    return time.time()


class AsyncIODownloader:
    """Uses asyncio to asynchronously download files."""

    def __init__(self, file, destination):
        self.file = file
        self.destination = destination

        # To limit a number of simultaneous downloads
        self.semaphore = asyncio.Semaphore(20)

    def run(self):
        """Downloads all URLs from the input file in the event loop and waits
        for completion.
        """
        logger.debug("Downloading from %s to %s", self.file, self.destination)
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self._download_files(event_loop))

    async def _download_files(self, event_loop):
        """Reads the input file line be line and adds new tasks on the event
        loop to download and save files to disc.
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            async with aiofiles.open(self.file, mode='r') as f:
                async for line in f:
                    logger.debug("Read line: %s", line)
                    line = line.strip()
                    if not line:
                        continue
                    tasks.append(event_loop.create_task(
                        self._download_file(session, line)))

            await asyncio.wait(tasks)

    async def _download_file(self, session, url):
        """Fetches a URL in the given session.
        """
        with (await self.semaphore):
            logger.info("Fetching %s", url)
            async with session.get(url) as response:
                if response.status == 200:
                    filepath = self._get_filepath(url)
                    await self._write_file(filepath, response)
                else:
                    logger.error("Couldn't fetch %s (status %s)",
                                 url, response.status)

    def _get_filepath(self, url):
        """Returns an absolute path to the file based on the destination folder
        and a filename guessed from the url. If such a file already exists,
        adding timestamp to make it unique.
        """
        filepath = os.path.join(self.destination, url.split('/')[-1])
        if os.path.exists(filepath):
            logger.warning("%s already exists, renaming...", filepath)
            name, extension = os.path.basename(filepath).rsplit('.', 1)
            filepath = os.path.join(
                os.path.dirname(filepath),
                '{}-{}.{}'.format(name, get_timestamp(), extension))
        return filepath

    @staticmethod
    async def _write_file(filepath, response):
        """Reads out the content from the given response by chunks and writes
        it to disk.
        """
        logger.debug("Writing file %s", filepath)
        async with aiofiles.open(filepath, mode='wb') as f:
            chunk = await response.content.read(CHUNK_SIZE)
            while chunk:
                await f.write(chunk)
                chunk = await response.content.read(CHUNK_SIZE)
