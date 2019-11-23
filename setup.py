from setuptools import setup

setup(
    name="MarvelComicNator",
    version="0.0.2",
    description="Marvel Comics",
    author="Marcos de Jesus Fuenmayor Soto",
    author_email="marcos.fuenmayorhtc@gmail.com",
    packages=["comicnator"],
    install_requires=[
        "flask",
        "sqlalchemy",
        "flask_jsglue",
        "wtforms",
        "flask_sqlalchemy",
        "werkzeug",
    ],
)
