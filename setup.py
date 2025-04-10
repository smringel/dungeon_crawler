from setuptools import setup, find_packages

setup(
    name="dungeon_crawler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
    ],
    entry_points={
        "console_scripts": [
            "dungeon-crawler=dungeon_crawler.main:main",
        ],
    },
    author="Seth Ringel",
    description="A simple dungeon crawler game",
    keywords="game, pygame, dungeon crawler",
    python_requires=">=3.6",
)
