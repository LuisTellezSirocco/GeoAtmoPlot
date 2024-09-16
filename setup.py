from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
install_requires = (this_directory / "requirements.txt").read_text().splitlines()

# get version
with open("pyatmo/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            _, _, version = line.replace("'", "").split()
            version = version.replace('"', "")

setup(
    name="geoatmoplot",
    version=version,
    author="Luis Tellez Ramirez",
    author_email="luis.tellez@sirocco.energy",
    company="Sirocco Energy S.L.",
    description="Package for processing Invoice Data.",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[], #install_requires,  # requirements,
    maintainer="Luis Tellez Ramirez",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
