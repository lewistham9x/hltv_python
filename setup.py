from setuptools import setup, find_packages

# Dependencies
install_requirements = [
    "lxml==4.6.3",
    "requests==2.26.0",
    "pandas==1.3.2",
    "python-dateutil==2.8.2"
]

test_requirements = [
    "pytest>=6"
]

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
    package_dir= {"" : "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python 3.7",
        "Programming Language :: Python 3.8",
        "Programming Language :: Python 3.9",
    ],
    
    install_require=install_requirements,
    test_require=test_requirements,
)
