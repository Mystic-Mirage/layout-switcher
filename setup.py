from setuptools import setup

setup(
    name="layout_switcher",
    version="0.1",
    entry_points={
        "console_scripts": [
            "layout-switcher = layout_switcher:run",
        ]
    },
    install_requires=[
        "python-xlib",
        "pyxhook",
        "xkbgroup",
    ],
)
