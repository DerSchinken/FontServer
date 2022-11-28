from flask import Flask, render_template, request, send_from_directory, make_response, Response
from src.fonts_downloader import get_font, update_fonts
from werkzeug.security import check_password_hash
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from _thread import start_new_thread
from dotenv import dotenv_values
from os import urandom, path
import requests
import sqlite3
import time

app = Flask(__name__)
cors = CORS(app, resources={r"/fonts/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
auth = HTTPBasicAuth()

src_root = __file__.replace("\\", "/").replace("/src/server.py", "") + "/src"
config = dotenv_values(f"{src_root.replace('/src', '')}/server.env")
google_api_key = config["GOOGLE_API_KEY"]
google_fonts = requests.get(f"https://www.googleapis.com/webfonts/v1/webfonts?key={google_api_key}").json()["items"]


@app.route("/css", methods=["GET"])
def get_font_script() -> Response:
    """
    Serves the font loading script
    """
    font_family = request.args.get("family", None)
    if not font_family or font_family == "ExampleFont" and not font_available(font_family):
        return page_not_found()
    if not path.exists(path.join(src_root, "fonts", font_family)):
        if get_font(font_family) == 404:
            return page_not_found()

    with open(path.join(src_root, "fonts", font_family.replace(" ", "+"), "style.css"), "r") as f:
        script = f.read()

    response = make_response(script)
    response.mimetype = "text/css"

    return response


@app.route("/view/<fontname>")
@auth.login_required
def view(fontname: str) -> Response:
    """
    View font

    :param fontname: Font name
    """
    return Response(
        render_template(
            "view.html",
            fontname=fontname.replace(" ", "+"),
            fontname_unformatted=fontname,
            domain_name=(config["DOMAIN_NAME"] + f":{config['PORT']}" if config["PORT"] != "80" else "")
        )
    )


@app.route("/fonts/<fontname>/<filename>")
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_font_file(fontname: str, filename: str) -> Response:
    """
    Serves the font files

    :param fontname: Font name
    :param filename: Font File
    """
    if path.exists(path.join(src_root, "fonts", fontname, "fonts", filename)):
        return send_from_directory(src_root+"/fonts", fontname+"/fonts/"+filename)

    if not get_font(fontname) == 404 and font_available(fontname):
        return send_from_directory(src_root+"/fonts", fontname+"/fonts/"+filename)

    return page_not_found(tried_url=f"fonts/{fontname}/{filename}")


@app.route('/')
@auth.login_required
def index() -> Response:
    """
    Homepage listing all available fonts
    """
    available_fonts = []
    for font in google_fonts["items"]:
        available_fonts.append(font["family"])
    # TODO list of all available fonts and import link generator
    return Response(render_template("index.html", available_fonts=available_fonts))


@app.errorhandler(404)
def page_not_found(e: Exception = None, tried_url: str = None) -> Response:
    """
    404 Page

    :param e: Ignored exception
    :param tried_url: Url that was tried by the user
    """
    ignore(e)
    return Response(render_template("404.html", tried_url=str(tried_url)), 404)


@auth.verify_password
def verify_password(username: str, password: str or bytes) -> bool:
    """
    Verification function for BasicHttpAuth

    :param username: Username
    :param password: Password
    """
    db = sqlite3.connect(src_root+"/"+"fontserver.db")
    users = db.execute("SELECT * FROM users").fetchall()

    for user_data in users:
        if user_data[0] == username:
            return check_password_hash(user_data[1], password)


def font_updater(t: int = 604800) -> None:
    """
    Update fonts periodically every {t} seconds

    :param t: time to wait before next update (in seconds)
    """
    global google_fonts
    while True:
        update_fonts()
        time.sleep(t)
        google_fonts = requests.get(
            f"https://www.googleapis.com/webfonts/v1/webfonts?key={google_api_key}"
        ).json()["items"]


def download_all_fonts() -> None:
    """
    Download all existing google fonts
    """
    for font in google_fonts:
        get_font(font["family"])
        time.sleep(0.1)


def font_available(fontname: str) -> bool:
    """
    Check if [fontname] is available

    :param fontname: font name
    """
    for font in google_fonts:
        if font["family"] == fontname:
            return True

    return False


def ignore(*args, **kwargs) -> None:
    """
    Ignore function so pycharm doesn't complain about unused variables
    """
    for arg in args:
        str(arg)
        break
    for kwarg in kwargs:
        str(kwarg)
        break


def start(host: str, port: int, secret_key: str, debug: bool = False) -> None:
    """
    Start the server

    :param host: Host
    :param port: Port
    :param secret_key: Secret key
    :param debug: Debug
    """
    download_all_fonts()
    app.config["secret_key"] = urandom(24) if secret_key is None else secret_key
    start_new_thread(font_updater, ())
    app.run(
        host=host,
        port=port,
        debug=debug
    )


if __name__ == "__main__":
    start_new_thread(update_fonts, ())
    new_secret_key = urandom(64).hex()
    print(f"Your secret key is '{new_secret_key}'")
    app.config["secret_key"] = new_secret_key

    app.run("0.0.0.0", 80, True)
