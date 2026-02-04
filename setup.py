from setuptools import setup, find_packages

setup(
	name="jintex_customization",
	version="0.0.1",
	description="Stock and Purchase Management",
	author="Raaj Tailor",
	author_email="raaj@akhilaminc.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=["frappe"],
)
