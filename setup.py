from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name='gosmsge',
    version='1.0.3',
    description='Package for GoSMSGE that helps you to send messages to your clients',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Graey',
    project_urls={
        'Source': 'https://github.com/gosms-ge/gosmsge-python',
    },
    author_email='info@graey.ge',
    packages=find_packages(include=[
        'gosmsge'
    ]),
    install_requires=[
        'requests>=2.25.1',
        'requests-mock>=1.9.3'
    ],
    license='MIT',
    license_file='LICENSE',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
