from setuptools import setup, find_packages

setup(
    name="subsevenzip",
    version="0.1",
    description="7-Zip decompressor",
    author="Daniel Svensson",
    author_email="dsvensson@gmail.com",
    license="ISC",
    packages=find_packages(),
    test_suite="nose.collector",
    setup_requires=[
        "coverage",
        "flake8",
        "nose"
    ],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only"
    ]
)
