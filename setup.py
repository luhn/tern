from setuptools import setup, find_packages

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
    requires=[
    ],
)
