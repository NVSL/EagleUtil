from setuptools import setup
import os
from codecs import open
import sys

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'VERSION.txt'), encoding='utf-8') as f:
    version = f.read()


setup(name='EagleUtil',
      version=version,
      description="A bad library for dealing with Eagle files.  Use Swoop instead",
      long_description=long_description,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Operating System :: MacOS",
          "Operating System :: POSIX",
          "Operating System :: POSIX :: Linux",
          "Operating System :: Unix",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
          "Topic :: System",
          "Topic :: System :: Hardware",
      ],
      author="NVSL, University of California San Diego",
      author_email="swanson@cs.ucsd.edu",
      test_suite="Test",
      packages = ["EagleUtil"],
      package_dir={
          'EagleUtil' : 'EagleUtil',
      },
      package_data={
          "" : ["*.rst"],
      },
      install_requires=["lxml>=3.4.2"],
      entry_points={
          'console_scripts': [
            'devFamily = EagleTools.devFamily:main',
            'dumpTags = EagleTools.dumpTags:main',
            'extractLibraries = EagleTools.extractLibraries:main',
            'listEagle = EagleTools.listEagle:main'
        ]
        },
      keywords = "PCB Eagle CAD printed circuit boards schematic electronics CadSoft",

)


