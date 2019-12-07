from comicnator import create_app


def run():
    app = create_app()
    app.run(host="localhost", port=5000)


if __name__ == "__main__":
    run()
