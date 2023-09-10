## Introduction

The **NetSuite GraphQL Engine** simplifies the interaction with the NetSuite SuiteTalk API by providing a GraphQL interface. It empowers developers to effortlessly query and manipulate NetSuite data using GraphQL syntax, facilitating seamless integration of NetSuite's powerful features into their Python applications.

### Key Features

- Query and fetch data from NetSuite with intuitive GraphQL queries.
- Create, update, or delete records in your NetSuite account using GraphQL mutations.
- Handle authentication and error handling gracefully for a seamless development experience.

This module is designed to enhance your NetSuite GraphQL experience by supporting asynchronous calls and caching using AWS DynamoDB through the PynamoDB library. By leveraging the [SuiteTalk Connector](https://github.com/ideabosque/suitetalk_connector) for API communication and PynamoDB for caching, you can combine the convenience of GraphQL with the efficiency of asynchronous calls and caching for optimal performance.

## Installation

To easily install the NetSuite GraphQL Engine using pip and Git, execute the following command in your terminal:

```shell
$ python -m pip install 'git+ssh://git@github.com/ideabosque/netsuite_graphql_engine.git@main#egg=netsuite_graphql_engine'
```

## Configuration

Configuring the NetSuite GraphQL Engine requires setting up specific files and environment variables. Follow these steps to ensure proper configuration:

### AWS DynamoDB Tables

To enable efficient caching and data management, create the following AWS DynamoDB tables:

1. **`nge-function-request`**: This table uses a partition key (`function_name`) and a sort key (`request_id`).

2. **`nge-record-staging`**: Configure this table with a partition key (`record_type`) and a sort key (`internal_id`). Additionally, create a local secondary index named `updated_at-index` with a partition key (`record_type`) and a sort key (`updated_at`).

### .env File

Create a `.env` file in your project directory with the following content:

```plaintext
region_name=YOUR_AWS_REGION
aws_access_key_id=YOUR_AWS_ACCESS_KEY_ID
aws_secret_access_key=YOUR_AWS_SECRET_ACCESS_KEY
ACCOUNT=YOUR_NETSUITE_ACCOUNT_ID
CONSUMER_KEY=YOUR_CONSUMER_KEY
CONSUMER_SECRET=YOUR_CONSUMER_SECRET
TOKEN_ID=YOUR_TOKEN_ID
TOKEN_SECRET=YOUR_TOKEN_SECRET
```

Replace the placeholders (`YOUR_AWS_REGION`, `YOUR_AWS_ACCESS_KEY_ID`, `YOUR_AWS_SECRET_ACCESS_KEY`, `YOUR_NETSUITE_ACCOUNT_ID`, `YOUR_CONSUMER_KEY`, `YOUR_CONSUMER_SECRET`, `YOUR_TOKEN_ID`, and `YOUR_TOKEN_SECRET`) with your actual AWS region, AWS Access Key ID, AWS Secret Access Key, NetSuite account ID, consumer key, consumer secret, token ID, and token secret.

Certainly! Here's the enhanced configuration section with the URL for the SuiteTalk Connector reference:

### Configuration Files

Before setting up the NetSuite GraphQL Engine, ensure you have the `netsuitemappings_soap.json` file properly configured. Refer to the [SuiteTalk Connector documentation](https://github.com/ideabosque/netsuite_connector) for guidance on configuring this file to suit your specific NetSuite environment.


### ASYNC_FUNCTIONS Mapping

The `"ASYNC_FUNCTIONS"` mapping associates GraphQL resolver function names with their corresponding asynchronous functions. This enables non-blocking execution of GraphQL queries and mutations, enhancing the server's responsiveness.

For example:

```python
"ASYNC_FUNCTIONS": {
    "resolve_record": "netsuite_get_record_async",
    "resolve_record_by_variables": "netsuite_get_record_by_variables_async",
    # Add more mappings as needed...
},
```

Each key represents a GraphQL resolver function, and the associated value is the name of the asynchronous function that handles potentially time-consuming tasks, such as interacting with the NetSuite API.

### Sample Configuration

To help you get started quickly, here's a sample configuration script that sets up the NetSuite GraphQL Engine using environment variables and the `netsuitemappings_soap.json` file:

```python
import logging
import os
import sys
import json
from dotenv import load_dotenv
from netsuite_graphql_engine import NetSuiteGraphQLEngine

# Load environment variables from a .env file
load_dotenv()

# Define the configuration settings
config_settings = {
    "region_name": os.getenv("AWS_REGION"),
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "ACCOUNT": os.getenv("NETSUITE_ACCOUNT_ID"),
    "CONSUMER_KEY": os.getenv("NETSUITE_CONSUMER_KEY"),
    "CONSUMER_SECRET": os.getenv("NETSUITE_CONSUMER_SECRET"),
    "TOKEN_ID": os.getenv("NETSUITE_TOKEN_ID"),
    "TOKEN_SECRET": os.getenv("NETSUITE_TOKEN_SECRET"),
    "VERSION": "2023_1_0",  # NetSuite API version
    "TIMEZONE": "America/Los_Angeles",
    "CREATE_CUSTOMER": False,  # Example configuration
    "CREATE_CUSTOMER_DEPOSIT": ["VISA", "Master Card"],  # Example configuration
    "LIMIT_PAGES": 0,  # Example configuration
    "NETSUITEMAPPINGS": json.load(
        open(
            f"{os.path.abspath(os.path.dirname(__file__))}/netsuitemappings_soap.json",
            "r",
        )
    ),
    "ASYNC_FUNCTIONS": {
        "resolve_record": "netsuite_get_record_async",
        "resolve_record_by_variables": "netsuite_get_record_by_variables_async",
        "resolve_records": "netsuite_get_records_async",
        "insert_update_record": "netsuite_insert_update_record_async",
    },
}

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

# Initialize the NetSuite GraphQL Engine
netsuite_graphql_engine = NetSuiteGraphQLEngine(logger, **config_settings)
```

This script demonstrates how to configure the NetSuite GraphQL Engine by loading environment variables and specifying various settings, including authentication details, API version, and caching options. Customize these settings according to your specific requirements and use case.

By following this sample configuration, you can quickly set up the NetSuite GraphQL Engine for seamless interaction with your NetSuite data while referencing the [SuiteTalk Connector documentation](https://github.com/ideabosque/netsuite_connector) for configuration details.

