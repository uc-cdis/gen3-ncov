from setuptools import setup, find_packages


setup(
    name="gen3-augur",
    author="Yilin Xu",
    author_email="yilinxu@uchicago.edu",
    version=0.1,
    url="https://github.com/yilinxu/gen3-augur",
    description="Utility tools for data accessing from gen3 and data processing with augur",
    license="Apache 2.0",
    packages=find_packages(exclude=["*test*"]),
    package_data={"": ["config/country_region_mapper.csv"]},
    include_package_data=True,
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points=""" 
        [console_scripts]
        gen3-augur=gen3_augur_pyutils.__main__:main
    """,
)
