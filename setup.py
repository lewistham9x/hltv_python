from setuptools import setup, find_packages

setup(
    name="hltv-api",
    version="0.0.1",
    description="Unofficial HLTV API to query Counter Strike historical data",
    url="https://github.com/hoangvu01/hltv_python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Hoang Vu",
    author_email="vc.hoang01@gmail.com",
    license='MIT',
    install_requires=[
        "lxml==4.6.3",
        "requests==2.26.0",
        "pandas==1.3.2" 
    ],
    package_dir= {"" : "src"},
    packages=find_packages(where="src")
)
