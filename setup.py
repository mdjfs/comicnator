from setuptools import setup

setup(
    name="MarvelComicNator",
    version="0.0.4",
    description="Marvel Comics",
    author="Marcos de Jesus Fuenmayor Soto",
    author_email="marcos.fuenmayorhtc@gmail.com",
    packages=["comicnator"],
    package_data={
        "comicnator": [
            "templates/*.html",
            "templates/base/*.html",
            "static/favicon.ico",
            "static/*.jpg",
            "static/css/*.png",
            "static/css/*.gif",
            "static/css/*.jpg",
            "static/css/*.css",
            "static/css/iepngfix.htc",
            "static/js/*.js",
            "static/init/*.csv",
        ]
    },
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-login",
        "flask_jsglue",
        "wtforms",
        "flask_sqlalchemy",
        "werkzeug",
        "click",
    ],
)
