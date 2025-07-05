from setuptools import setup, find_packages

setup(
    name="campus-agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "python-dotenv",
        "werkzeug",
    ],
)