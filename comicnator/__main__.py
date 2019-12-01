from comicnator import create_app


def run():
    app = create_app()
    app.run(host="127.0.0.1", port=8080)


if __name__ == "__main__":
    run()
