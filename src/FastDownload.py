from time import time as get_current_time
from os import path, makedirs
from threading import Thread
from requests import Session


def convert_bytes(size: int) -> str:
    """
    Convert bytes to human-readable format

    :param size: bytes
    """
    for s in ["bytes", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {s}"
        size /= 1024


class FastDownloader:
    """
    Downloads a list of files with threading
    can also give extra information about the download process
    """
    _downloader = Session()
    _total_download_time = 0
    _total_downloaded = 0
    _total_size = 0
    _total_time = 0
    _threads = []

    def __init__(
            self,
            output_dir: str = "downloaded",
            overwrite: bool = False,
            max_threads: int = "inf",
            info: bool = False
    ) -> None:
        """
        Configures the downloader and creates the output directory if not already existing

        :param output_dir: The directory where the files will be saved
        :param max_threads: The maximum amount of threads that can be used
        :param info: If True, prints information about the download process
        """
        self._output_dir = output_dir
        self._overwrite = overwrite
        if max_threads == "inf":
            max_threads = float("inf")
        self._max_threads = max_threads
        self._info = info

        if not path.exists(self._output_dir):
            makedirs(self._output_dir)

    def download(self, urls: list[str]) -> None:
        """
        Downloads all files from the given urls

        :param urls: A list of urls (the list of files to download)
        """
        urls = urls.copy()
        if len(urls) - len(list(set(urls))) > 0:  # Detect duplicates
            if self._info:
                print(f"Found {len(urls) - len(list(set(urls)))} duplicated url(s). Removing and continuing...")
            urls = list(set(urls))  # remove all duplicates

        while len(self._threads) <= self._max_threads and urls:
            self._threads.append(
                Thread(target=self._download, args=(urls.pop(),))
            )
            self._threads[-1].start()
        else:
            if urls:
                self.wait_to_finish()
                self.download(urls)

    def wait_to_finish(self) -> None:
        """
        Waits for all threads to finish and resets the threads list
        """
        for thread in self._threads:
            thread.join()

        self._threads = []

    def statistics(self) -> list:
        """
        Returns a list containing the total downloaded files,
        the total size of all downloaded files in bytes,
        the time it would have taken to download all files in seconds.
        """
        return [self._total_downloaded, self._total_size, self._total_download_time]

    def _download(self, url: str) -> None:
        """
        The actual download function

        :param url: The url of the file to download
        """
        start_time = get_current_time()
        file = self._downloader.get(url)
        filename = url.split("/")[-1]
        # Check if the file already exists
        if path.exists(path.join(self._output_dir, filename)) and not self._overwrite:
            duplicate = 1
            old_filename = filename
            # Generate new filename in the format "{filename} ({duplicate number}).{extension}"
            while path.exists(path.join(self._output_dir, filename)):
                filename = f"{''.join(old_filename.split('.')[:-1])} ({duplicate}).{old_filename.split('.')[-1]}"
                duplicate += 1
            if self._info:
                print(f"File {old_filename} already exists! Renaming to {filename}")

        # Write the file to the output directory
        with open(f"{self._output_dir}/{filename}", "wb") as f:
            f.write(file.content)
            # Update the statistics
            self._total_size += f.tell()
            if self._info:
                print(f"Downloaded {url} -> {self._output_dir}/{filename}   ({convert_bytes(f.tell())})")
        self._total_downloaded += 1
        self._total_download_time += get_current_time() - start_time
