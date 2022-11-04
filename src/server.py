from flask import Flask, render_template, request, send_from_directory, make_response
from src.fonts_downloader import get_font, update_fonts
from _thread import start_new_thread
from os import urandom, path
import time

app = Flask(__name__)

src_root = __file__.replace("\\", "/").replace("/src/server.py", "") + "/src"


@app.route("/css", methods=["GET"])
def get_font_script():
    """
    Serves the font loading script
    """
    font_family = request.args.get("family", None)
    if not font_family or font_family == "ExampleFont":
        return page_not_found()
    if not path.exists(path.join(src_root, "fonts", font_family)):
        if get_font(font_family) == 404:
            return page_not_found()

    with open(path.join(src_root, "fonts", font_family.replace(" ", "+"), "style.css"), "r") as f:
        script = f.read()

    response = make_response(script)
    response.mimetype = "text/css"

    return response


@app.route("/fonts/<fontname>/<filename>")
def get_font_file(fontname, filename):
    """
    Serves the font files
    """
    print(path.join(src_root, "fonts", fontname, filename))
    if path.exists(path.join(src_root, "fonts", fontname, "fonts", filename)):
        return send_from_directory(src_root+"/fonts", fontname+"/fonts/"+filename)

    return page_not_found(tried_url=f"fonts/{fontname}/{filename}")


@app.route('/')
def index():
    # TODO list of all available fonts and import link generator
    return render_template("index.html")


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
    start_new_thread(update_fonts, ())
    secret_key = urandom(64).hex()
    print(f"Your secret key is '{secret_key}'")
    app.config["secret_key"] = secret_key

    app.run("0.0.0.0", 80, True)
