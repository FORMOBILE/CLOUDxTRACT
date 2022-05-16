from setuptools import find_packages, setup

setup(
    name="extractor",
    version="0.0.3",
    description="CloudXtractor",
    author="Martin Bochmann",
    author_email="martin.bochmann@hs-mittweida.de",
    license="proprietary and confidential",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests", "pytz",
                      "xmltodict", "pysimplegui", "iso8601", "nextcloud-api-wrapper"],
    zip_safe=False,
)
