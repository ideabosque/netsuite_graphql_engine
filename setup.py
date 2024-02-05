"""
# NetSuite-GraphQL-Engine
=====================

"""
from setuptools import find_packages, setup

setup(
    name="NetSuite-GraphQL-Engine",
    version="0.0.4.beta.1",
    url="https://github.com/ideabosque/netsuite_graphql_engine",
    license="MIT",
    author="Idea Bosque",
    author_email="ideabosque@gmail.com",
    description="The **NetSuite GraphQL Engine** enables Python developers to interact with the NetSuite SuiteTalk API using GraphQL, simplifying data access and integration into their applications.",
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "SuiteTalk-Connector>=0.0.3",
        "graphene",
        "pynamodb",
        "boto3",
        "silvaengine_utility",
        "silvaengine_dynamodb_base",
        "deepdiff",
    ],
    keywords=[
        "GraphQL",
        "NetSuite",
        "SuiteTalk",
        "Integration",
        "API",
    ],  # arbitrary keywords
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
