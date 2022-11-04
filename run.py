from dotenv import dotenv_values
from src import server

config = dotenv_values("server.env")

server.app.config["secret_key"] = config["secret_key"]

if __name__ == "__main__":
    server.app.run(
        host=config["host"],
        port=config["port"],
        debug=config["debug"]
    )
