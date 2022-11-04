from src.FastDownload import FastDownloader
from dotenv import dotenv_values
from os import listdir
import requests

root = __file__.replace("\\", "/").replace("/src/fonts_downloader.py", "")

google_fonts_service_url = 'https://fonts.googleapis.com/css?family='
host = dotenv_values(f"{root}/server.env")["DOMAIN_NAME"]
src_root = f"{root}/src"


def get_font(font_family: str) -> None or int:
    """
    Download font from Google Fonts
    """
    font_family = font_family.replace(" ", "+")
    script_url = f"{google_fonts_service_url}{font_family}"
    font_script = requests.get(script_url).text

    if "400" in font_script and "Missing font family" in font_script:
        return 404

    font_urls = []
    for line in font_script.split("src:"):
        if line.split(")")[0].replace("url(", "").replace(" ", "").startswith("https://"):
            font_urls.append(line.split(")")[0].replace("url(", "").replace(" ", ""))

    font_downloader = FastDownloader(f"{src_root}/fonts/{font_family}/fonts", overwrite=True, max_threads=5)
    font_downloader.download(font_urls.copy())
    font_downloader.wait_to_finish()

    for font_url in font_urls:
        font_script = font_script.replace(font_url, f"{host}/fonts/{font_family}/{font_url.split('/')[-1]}")
    with open(f"{src_root}/fonts/{font_family}/style.css", "w") as f:
        f.write(font_script)


def update_fonts():
    """
    Update all fonts in the fonts directory
    """
    for font in listdir("fonts"):
        if font == "ExampleFont":
            continue
        get_font(font.replace(" ", "+"))
