from comicnator import create_app


def run():
    app = create_app()
    app.run(host="192.168.43.140", port=5000)


if __name__ == "__main__":
    run()
