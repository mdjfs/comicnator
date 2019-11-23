from comicnator import app
from comicnator.models import db

import netifaces as net

if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    address_host = net.ifaddresses("wlp2s0")[net.AF_INET][0]["addr"]
    app.run(host=address_host, port=5000)
