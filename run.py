from werkzeug.security import generate_password_hash
from dotenv import dotenv_values
from src import server
import sqlite3

src_root = '/'.join(__file__.replace('\\', '/').split('/')[:-1]) + "/src"
db = sqlite3.connect(src_root + '/' + "fontserver.db")
config = dotenv_values("server.env")

try:
    db.execute("create table users (username text, password text)")
    print("Creating new user...")
    user = input("Username: ")
    password = input("Password: ")

    db.execute(f"insert into users values('{user}', '{generate_password_hash(password)}')").fetchall()
except sqlite3.OperationalError:
    data_present = db.execute("select count(*) from users").fetchall()[0][0]
    if not data_present:
        print("Creating new user...")
        user = input("Username: ")
        password = input("Password: ")
        db.execute(f"insert into users values('{user}', '{generate_password_hash(password)}')").fetchall()
db.commit()
db.close()


def start():
    debug = True if config["DEBUG"] == "1" else False
    server.start(
        host=config["DOMAIN_NAME"],
        port=config["PORT"],
        secret_key=config["SECRET_KEY"],
        debug=debug
    )


if __name__ == "__main__":
    debug = True if config["DEBUG"] == "1" else False
    server.start(
        host=config["DOMAIN_NAME"],
        port=config["PORT"],
        secret_key=config["SECRET_KEY"],
        debug=debug
    )
