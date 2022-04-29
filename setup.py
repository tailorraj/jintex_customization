from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in jintex_customization/__init__.py
from jintex_customization import __version__ as version

setup(
	name="jintex_customization",
	version=version,
	description="Stock and Purchase Management",
	author="Raaj Tailor",
	author_email="raaj@akhilaminc.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
