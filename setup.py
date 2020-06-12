from setuptools import find_packages, setup

setup(
    name="layout_switcher",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["layout-switcher = layout_switcher:main"]
    },
    install_requires=["python-xlib", "pyxhook", "xkbgroup"],
)
