import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indelible_log",
    version="0.4.6",
    author="Jeff Rhyason",
    author_email="jeff@indelible.systems",
    description="client for Indelible managed persistent store and synchronizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://indelible.systems",
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Topic :: Database",
        'Intended Audience :: Developers',
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    install_requires=['requests', 'pynacl'],
    project_urls={
      # TODO 'Source': 'https://code.ndlbl.net/...'
    }
)


