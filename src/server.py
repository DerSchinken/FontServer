from flask import Flask, render_template, request, send_from_directory
from fonts_dowlader import get_font, update_fonts
from _thread import start_new_thread
from os import urandom, path
import requests
import sqlite3
import time

app = Flask(__name__)
db = sqlite3.connect("fonts.sqlite3")


@app.route("/font", methods=["GET"])
def get_font():
    font = request.args.get("family", None)
    if not font:
        return page_not_found()
    # TODO serve css font import script


@app.route("/fonts/<fontname>/<filename>")
def get_font_file(fontname, filename):
    if path.exists(path.join("fonts/", fontname, filename)):
        return send_from_directory("fonts", fontname+'/'+filename)
    # TODO download fonts and serve them


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e=None, tried_url=None):
    return render_template("404.html", tried_url=str(tried_url)), 404


def font_updater(t: int = 604800):
    """
    Update fonts periodically every {t} seconds

    :param t: time to wait before next update (in seconds)
    """
    while True:
        update_fonts()
        time.sleep(t)


if __name__ == "__main__":
    secret_key = urandom(64).hex()
    print(f"Your secret key is '{secret_key}'")
    app.config["secret_key"] = secret_key

    app.run("0.0.0.0", 80, True)
