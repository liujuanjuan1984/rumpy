import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rumpy",
    version="0.1.2",
    author="liujuanjuan1984",
    author_email="qiaoanlu@163.com",
    description="python sdk for quorum: https://github.com/rumsystem/quorum",
    keywords=["rumpy", "rumsystem", "quorum"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liujuanjuan1984/rumpy",
    project_urls={
        "Github Repo": "https://github.com/liujuanjuan1984/rumpy",
        "Bug Tracker": "https://github.com/liujuanjuan1984/rumpy/issues",
        "About Quorum": "https://github.com/rumsystem/quorum",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pytest",
        "requests",
        "pandas",
        "pillow",
        "matplotlib",
        "sqlalchemy",
    ],
)
