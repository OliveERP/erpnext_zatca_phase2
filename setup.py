from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in erpnext_zatca/__init__.py
from erpnext_zatca import __version__ as version

setup(
	name='erpnext_zatca',
	version=version,
	description='Integration of ERPNExt of ZATCA System',
	author='Webmekanics Pakistan',
	author_email='sajid@webmekanics.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
