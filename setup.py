from setuptools import setup, find_packages

setup(
    name="rumpy",
    version="0.0.5",
    keywords=["rumpy", "rumsystem", "quorum"],
    description="python sdk for [quorum](https://github.com/rumsystem/quorum)",
    license="GPL-3.0 License",
    install_requires=[],
    packages=["rumpy"],  # 要打包的项目文件夹
    include_package_data=True,  # 自动打包文件夹内所有数据
    author="liujuanjuan1984",
    author_email="qiaoanlu@163.com",
    url="https://github.com/liujuanjuan1984/rumpy",
    # packages = find_packages(include=("*"),),
)
