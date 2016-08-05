from setuptools import setup

setup(
  name = 'parse-schema-validator',
  packages = ['parse_schema_validator'],
  entry_points = {
        'console_scripts': ['parse-schema-validator=parse_schema_validator.schema_validator:main']
  },
  version = '1.0.2',
  description = 'Tool for validating Parse classes on a Parse Server',
  author = 'Duncan Cunningham',
  author_email = 'duncanc4@gmail.com',
  license = 'MIT',
  url = 'https://github.com/sirnacnud/parse-schema-validator',
  download_url = 'https://github.com/sirnacnud/parse-schema-validator/archive/1.0.2.tar.gz',
  keywords = ['parse', 'schema', 'validator'],
  classifiers = [],
)