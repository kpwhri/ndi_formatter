from distutils.core import setup
import setuptools

setup(name='ndi_formatter',
      version='0.1',
      description='Format data for NDI requests.',
      url='https://bitbucket.org/dcronkite/ndi_formatter',
      author='dcronkite',
      author_email='dcronkite-gmail',
      license='MIT',
      classifiers=[  # from https://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
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