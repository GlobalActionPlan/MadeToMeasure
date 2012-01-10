import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_mailer',
    'repoze.zodbconn',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'repoze.retry',
    'ZODB3',
    'WebError',
    'Babel',
    'repoze.folder',
    'colander',
    'deform',
    'slugify',
    'lingua',
    'webhelpers',
    'pytz',
    'betahaus.pyracont',
    ]

setup(name='MadeToMeasure',
      version='0.0',
      description='MadeToMeasure',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="madetomeasure",
      entry_points = """\
      [paste.app_factory]
      main = madetomeasure:main
      [console_scripts]
      fix_nonpersistent_variants = madetomeasure.scripts.fix_nonpersistent_variants:fix_nonpersistent_variants
      """,
      paster_plugins=['pyramid'],
      message_extractors = { '.': [
          ('**.py',   'lingua_python', None ),
          ('**.pt',   'lingua_xml', None ),
          ('**.zcml',   'lingua_zcml', None ),
          ]},
      )

