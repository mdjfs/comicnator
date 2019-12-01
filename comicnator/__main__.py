from comicnator import app
import netifaces as net

if __name__ == "__main__":
    address_host = net.ifaddresses("wlp2s0")[net.AF_INET][0]["addr"]
    app.run(host=address_host, port=5500)
