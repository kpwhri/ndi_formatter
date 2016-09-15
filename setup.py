from distutils.core import setup
import setuptools
import os

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'),
          encoding='utf-8') as f:
    long_description = f.read()

setup(name='ndi_formatter',
      version='1.0.1',
      description='Format data for National Death Index (NDI) requests.',
      long_description=long_description,
      url='https://bitbucket.org/dcronkite/ndi_formatter',
      author='dcronkite',
      author_email='dcronkite@gmail.com',
      license='MIT',
      classifiers=[  # from https://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3 :: Only',
      ],
      keywords='ndi formatting',
      entry_points={
          'console_scripts':
              [
                  'ndi-formatter = ndi_formatter.format:main',
              ]
      },
      install_requires=[],
      extras_require={
          'sas7bdat_parsing': ['sas7bdat'],
          'date_inference': ['dateutil']
      },
      package_dir={'': 'src'},
      packages=setuptools.find_packages('src'),
      zip_safe=False
      )
