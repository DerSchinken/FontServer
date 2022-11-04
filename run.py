from dotenv import dotenv_values
from src import server

config = dotenv_values("server.env")

server.app.config["secret_key"] = config["SECRET_KEY"]

if __name__ == "__main__":
    server.app.run(
        host=config["HOST"],
        port=config["PORT"],
        debug=config["DEBUG"]
    )
