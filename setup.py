import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_mailer',
    'pyramid_zodbconn',
    'pyramid_tm',
    'fanstatic',
    'ZODB3',
    'Babel',
    'repoze.folder',
    'colander',
    'deform',
    'slugify',
    'lingua',
    'webhelpers',
    'pytz',
    'betahaus.pyracont >= 0.1a3',
    'iso8601',
    ]

setup(name='MadeToMeasure',
      version='0.1dev',
      description='MadeToMeasure',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Made to Measure develpopment team',
      author_email='robin@betahaus.net',
      url='https://github.com/GlobalActionPlan/MadeToMeasure',
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
      debug_instance = madetomeasure.scripts.debug:debug_instance
      """,
      paster_plugins=['pyramid'],
      message_extractors = { '.': [
          ('**.py',   'lingua_python', None ),
          ('**.pt',   'lingua_xml', None ),
          ]},
      )

