from distutils.core import setup

setup(name='ITC503Control',
      version='1.0.0',
      description='GUI to control the ITC503 temperature controler',
      long_description=open('README.txt').read(),
      author='Siwick Lab',
      author_email='sebastian.hammer@mail.mcgill.ca',
      url='',
      packages=['itc503', 'lib.remotectrl'],
      install_requires=['numpy', 'PyQT5', 'pyqtgraph']
      data_files=[('ui', ['ITC503UI.ui', 'bm/b2.gif'])]
     )