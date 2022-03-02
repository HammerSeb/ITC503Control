from gettext import find
from setuptools import setup, find_packages

setup(name='ITC503Control',
      version='1.0.0',
      description='GUI to control the ITC503 temperature controler',
      long_description=open('README.txt').read(),
      author='Siwick Lab',
      author_email='sebastian.hammer@mail.mcgill.ca',
      url='https://github.com/HammerSeb/ITC503Control',
      packages= find_packages(),
      install_requires=['numpy', 'PyQT5', 'pyqtgraph', 'uedinst@git+https://github.com/Siwick-Research-Group/uedinst.git'],
      include_package_data = True
     )