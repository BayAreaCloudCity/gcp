import setuptools

setuptools.setup(
    name='cloud-city-gcp',
    version='1.0',
    install_requires=[
        "geopy==2.4.1",
        "cloudevents==1.10.1",
        "functions-framework==3.5.0"
    ],
    packages=setuptools.find_packages()
)
