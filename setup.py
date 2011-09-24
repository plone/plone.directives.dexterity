from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='plone.directives.dexterity',
      version=version,
      description="Grok-like directives for creating Dexterity content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok plone dexterity content',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://code.google.com/p/dexterity',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.directives'],
      include_package_data=True,
      zip_safe=False,
      tests_require=[
        'plone.mocktestcase',
      ],
      install_requires=[
          'setuptools',
          'five.grok',
          'plone.dexterity>=1.0.1',
          'plone.directives.form>=1.0b3',
          'zope.deferredimport',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
