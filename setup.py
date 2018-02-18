from setuptools import setup


requires = (
    'tabulate',
)

setup(
    name='hours',
    version='0.0',
    description='Stupid script to track stupid hours',
    py_modules=('hours',),
    install_requires=requires,
)
