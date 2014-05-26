from setuptools import setup, find_packages

requires = ['six']

# Do we need importlib?  (Python 2.6)
try:
    import importlib  # noqa
except ImportError:
    requires.append('importlib')


setup(
    name='Tern',
    version='0.1.0',
    description='A simple way to version control your database.',
    author='Theron Luhn',
    author_email='theron@luhn.com',
    url='https://github.com/luhn/tern',
    packages=find_packages(),
    entry_points=dict(
        console_scripts=[
            'tern = tern.__main__:main',
        ],
    ),
    requires=requires,
)
