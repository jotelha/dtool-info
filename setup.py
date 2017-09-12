from setuptools import setup

url = "https://github.com/jic-dtool/dtool-info"
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-info",
    packages=["dtool_info"],
    version=version,
    description="Dtool plugin for getting information about datasets",
    long_description=readme,
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    url=url,
    install_requires=[],
    entry_points={
        "dtool.cli": [
            "diff=dtool_info.dataset:diff",
        ],
    },
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)