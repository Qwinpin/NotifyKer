import setuptools

with open("README_pypi.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="notifyker",
    version="2.0.3",
    author="Timur Sokhin",
    author_email="qwinpin@gmail.com",
    description="Notifications for ML libraries (Keras, Chainer) using telegram bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qwinpin/notifyker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='notifyker chainer keras telegram bot notification callback extentions'
)
