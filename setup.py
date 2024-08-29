import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ustcjwxt",
    version="v0.0.5",
    author="brealid",
    author_email="brealid@mail.ustc.edu.cn",
    description="ustc jwxt api, for study only",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brealid/ustcjwxt-python-lib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "requests",
    ]
)