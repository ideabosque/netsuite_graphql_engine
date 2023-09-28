## Introduction

The **NetSuite GraphQL Engine** simplifies the interaction with the NetSuite SuiteTalk API by providing a GraphQL interface. It empowers developers to effortlessly query and manipulate NetSuite data using GraphQL syntax, facilitating seamless integration of NetSuite's powerful features into their Python applications.

### Key Features

Discover the powerful capabilities of the NetSuite GraphQL Engine Python module:

- **Effortless Data Retrieval**: Easily query and retrieve data from your NetSuite account using user-friendly GraphQL queries, simplifying data access and extraction.

- **Data Manipulation**: Seamlessly create, update, or delete records within your NetSuite account using GraphQL mutations, offering flexibility in managing your NetSuite data.

- **Robust Error Handling**: Experience a smooth development process with robust error handling and graceful authentication mechanisms, ensuring your interactions with NetSuite are trouble-free.

This module is meticulously designed to elevate your NetSuite GraphQL experience further. It facilitates:

- **Asynchronous Execution**: Harness the power of asynchronous calls facilitated by AWS Lambda functions, optimizing performance and responsiveness in handling NetSuite data.

- **Efficient Caching**: Leverage AWS DynamoDB in conjunction with the PynamoDB library for efficient caching, reducing latency and minimizing redundant data requests.

By seamlessly integrating with the [SuiteTalk Connector](https://github.com/ideabosque/suitetalk_connector) for seamless API communication and employing PynamoDB for caching, you can unite the simplicity of GraphQL with the effectiveness of asynchronous operations and caching, delivering an exceptional performance-enhanced NetSuite experience.

## Installation

To easily install the NetSuite GraphQL Engine using pip and Git, execute the following command in your terminal:

```shell
$ python -m pip install git+ssh://git@github.com/ideabosque/silvaengine_utility.git@main#egg=silvaengine_utility
$ python -m pip install git+ssh://git@github.com/ideabosque/silvaengine_dynamodb_base.git@main#egg=silvaengine_dynamodb_base
$ python -m pip install NetSuite-GraphQL-Engine
```

## Configuration

Configuring the NetSuite GraphQL Engine requires setting up specific files and environment variables. Follow these steps to ensure proper configuration:

### AWS DynamoDB Tables

To enable efficient caching and data management, create the following AWS DynamoDB tables:

1. **`nge-function_request`**: This table uses a partition key (`function_name`) and a sort key (`request_id`).

2. **`nge-record_staging`**: Configure this table with a partition key (`record_type`) and a sort key (`internal_id`). Additionally, create a local secondary index named `updated_at-index` with a partition key (`record_type`) and a sort key (`updated_at`).

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

Before setting up the NetSuite GraphQL Engine, ensure you have the `netsuitemappings_soap.json` file properly configured. Refer to the [SuiteTalk Connector documentation](https://github.com/ideabosque/suitetalk_connector) for guidance on configuring this file to suit your specific NetSuite environment.


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

### ASYNC_FUNCTION_NAME

This specifies the AWS Lambda function responsible for executing asynchronous calls.

### Sample Configuration

To help you get started quickly, here's a sample configuration script that sets up the NetSuite GraphQL Engine using environment variables and the `netsuitemappings_soap.json` file:

```python
import logging
import os
import sys
import json
import path
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
    "ASYNC_FUNCTION_NAME": "silvaengine_agenttask",
}

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

# Initialize the NetSuite GraphQL Engine
netsuite_graphql_engine = NetSuiteGraphQLEngine(logger, **config_settings)
```

Ensure that you have the required Python packages installed, including `dotenv`. You can install them using the following command:

```shell
$ python -m pip install dotenv
```

This script demonstrates how to configure the NetSuite GraphQL Engine by loading environment variables and specifying various settings, including authentication details, API version, and caching options. Customize these settings according to your specific requirements and use case.

By following this sample configuration, you can quickly set up the NetSuite GraphQL Engine for seamless interaction with your NetSuite data while referencing the [SuiteTalk Connector documentation](https://github.com/ideabosque/suitetalk_connector) for configuration details.

## Usage

Utilizing the NetSuite GraphQL Engine is straightforward. Below, you'll find examples that illustrate how to construct GraphQL queries and mutations for seamless interaction with NetSuite data.

### Loading the GraphQL Schema

Begin by loading the GraphQL schema into a document parameter. This schema defines the structure of your queries and mutations.

```graphql
fragment SelectValueInfo on SelectValueType {
    value
    valueId
}

fragment FunctionRequestInfo on FunctionRequestType {
    functionName
    requestId
    recordType
    variables
    status
    data
    internalIds
    log
    requestPageSize
    pageNumber
    totalRecords
    createdAt
    updatedAt
}

query ping {
    ping
}

query getSelectValues(
    $recordType: String!,
    $field: String!,
    $sublist: String    
) {
    selectValues(
        recordType: $recordType,
        field: $field,
        sublist: $sublist
    ) {
        ...SelectValueInfo
    }
}

query getRecord(
    $recordType: String!,
    $id: String!,
    $useExternalId: Boolean,
    $requestId: String,
    $cacheDuration: Decimal
) {
    record(
        recordType: $recordType,
        id: $id,
        useExternalId: $useExternalId,
        requestId: $requestId,
        cacheDuration: $cacheDuration
    ) {
        ...FunctionRequestInfo
    }
}

query getRecordByVariables(
    $recordType: String!,
    $field: String!,
    $value: String!,
    $operator: String,
    $requestId: String,
    $cacheDuration: Decimal
) {
    recordByVariables(
        recordType: $recordType,
        field: $field,
        value: $value,
        operator: $operator,
        requestId: $requestId,
        cacheDuration: $cacheDuration
    ) {
        ...FunctionRequestInfo
    }
}

query getRecords(
    $recordType: String!,
    $cutDate: String,
    $hours: Decimal,
    $vendorId: String,
    $subsidiary: String,
    $itemDetail: Boolean,
    $inventoryDetail: Boolean,
    $internalIds: [String],
    $requestId: String,
    $cacheDuration: Decimal,
    $manualDispatch: Boolean,
    $requestPageSize: Int,
    $pageNumber: Int
) {
    records(
        recordType: $recordType,
        cutDate: $cutDate,
        hours: $hours,
        vendorId: $vendorId,
        subsidiary: $subsidiary,
        itemDetail: $itemDetail,
        inventoryDetail: $inventoryDetail,
        internalIds: $internalIds,
        requestId: $requestId,
        cacheDuration: $cacheDuration,
        manualDispatch: $manualDispatch,
        requestPageSize: $requestPageSize,
        pageNumber: $pageNumber
    ) {
        ...FunctionRequestInfo
    }
}

mutation insertUpdateRecord(
    $recordType: String!,
    $entity: JSON!,
    $transactionRecordType: String,
    $requestId: String
) {
    insertUpdateRecord(
        recordType: $recordType,
        entity: $entity,
        transactionRecordType: $transactionRecordType,
        requestId: $requestId
    ) {
        record{
            ...FunctionRequestInfo
        }
    }
}
```

This GraphQL schema provides you with the tools to construct queries and mutations to interact with your NetSuite data. Each query or mutation is named and can accept variables for customization.

### Using the Payload for Querying or Mutating Data

You can use the following payload structure to execute GraphQL queries or mutations programmatically:

```python
payload = {
    "query": document,
    "variables": variables,
    "operation_name": "getSelectValues",
}
```

Parameters:
- `query`: The GraphQL query or mutation document you've loaded earlier.
- `variables`: Any variables needed for your GraphQL query or mutation.
- `operation_name`: The name of the operation to be executed, corresponding to a named query or mutation in your GraphQL schema.

These parameters allow you to customize your GraphQL requests as needed, making your interactions with NetSuite data highly flexible.

### Example: Querying 'select_values'

Let's dive into an example of querying the `select_values` operation. This operation allows you to retrieve value/ID metrics for a specific field within a designated NetSuite record type, including the option to specify a sublist, such as 'itemList.'

**Parameters:**
- `recordType`: Specifies the NetSuite record type you intend to query.
- `field`: Identifies the specific field within the chosen record type for which you want to obtain values.
- `sublist`: Optionally, you can specify a sublist, such as 'itemList,' to narrow down your query further.

```python
    variables = {
        "recordType": "salesOrder",
        "field": "custcol_tc_ver",
        "sublist": "itemList",
    }
    payload = {
        "query": document,
        "variables": variables,
        "operation_name": "getSelectValues",
    }
    response = netsuite_graphql_engine.netsuite_graphql(**payload)
    print(json.loads(response)["data"]["selectValues"])
```

This example vividly illustrates how GraphQL empowers you to efficiently retrieve dropdown option values/IDs while offering exceptional flexibility for managing NetSuite data.

### Example: Querying 'record'

Let's explore querying with the `record` operation, which empowers you to fetch any NetSuite record using either its internal or external ID.

**Parameters:**
- `recordType`: Specifies the NetSuite record type you intend to query.
- `id`: Identifies the record using either its internal or external ID.
- `useExternalId`: Indicates whether the provided ID is an external ID.
- `requestId`: Optionally, you can include an async request ID, which is used for asynchronous data retrieval.
- `cacheDuration`: Specify the cache duration in hours. If set to 0, data retrieval bypasses the cache.

```python
variables = {
    "recordType": "salesOrder",
    "id": "123456",  # Replace with your desired internal or external ID.
    "useExternalId": False,  # Set to 'True' if using an external ID.
    "requestId": "async_request_123",  # Optional async request ID.
    "cacheDuration": 2,  # Cache data for 2 hours (adjust as needed).
}
payload = {
    "query": document,
    "variables": variables,
    "operation_name": "getRecord",
}
response = netsuite_graphql_engine.netsuite_graphql(**payload)
print(json.loads(response)["data"]["record"])
```

You can also trigger the async function as follows:

```python
params = {
    "request_id": "async_request_123",
}
netsuite_graphql_engine.netsuite_get_record_async(**params)
```

This example underscores the efficiency of querying NetSuite records, offering you the flexibility to choose between internal and external IDs, enable asynchronous data retrieval, and exercise cache control for precise data management.

### Example: Querying 'recordByVariables'

Now, let's delve into an example of querying the `recordByVariables` operation. This operation enables you to retrieve records based on specific criteria, including the field, value, and operator used for the query.

**Parameters:**
- `recordType`: Specifies the NetSuite record type you wish to query.
- `field`: Identifies the field used in the record query.
- `value`: Specifies the value to be matched in the query.
- `operator`: Defines the operator to be used in the query (e.g., "is," "contains").
- `requestId`: Optionally, you can include an async request ID, which is used for asynchronous data retrieval.
- `cacheDuration`: Specify the cache duration in hours. If set to 0, data retrieval bypasses the cache.

```python
variables = {
    "recordType": "salesOrder",
    "field": "tranId",
    "value": "SO-XXX-1234",
    "operator": "is",
    "cacheDuration": 0,  # Set to 0 to bypass caching.
    "requestId": "async_request_123",  # Optional async request ID.
}
payload = {
    "query": document,
    "variables": variables,
    "operation_name": "getRecordByVariables",
}
response = netsuite_graphql_engine.netsuite_graphql(**payload)
print(json.loads(response)["data"]["recordByVariables"])
```

You can also trigger the async function as follows:

```python
params = {
    "request_id": "async_request_123",
}
netsuite_graphql_engine.netsuite_get_record_by_variables_async(**params)
```

This example vividly illustrates how to query NetSuite records based on specific criteria, offering you the flexibility to define the field, value, and operator for your query. Additionally, it provides control over caching and allows you to opt for asynchronous data retrieval, making it a powerful tool for tailored data access.

### Example: Querying "records"

This example demonstrates how to query records in NetSuite, starting from a specified cut date and extending to the end of the time period.

**Parameters:**
- `recordType`: Specifies the NetSuite record type you intend to query.
- `cutDate`: Defines the cut-off date for record retrieval. Records modified after this date will be included in the results.
- `hours`: Specifies the time duration, in hours, from the cut date for retrieving records. Use 0 to include all records from the cut date onwards.
- `vendorId`: (Optional) Specifies the vendor for data querying.
- `subsidiary`: (Optional) Specifies the subsidiary for data querying.
- `itemDetail`: (Optional) Specifies whether to request item detail (Boolean).
- `inventoryDetail`: (Optional) Specifies whether to request inventory detail (Boolean).
- `internalIds`: (Optional) Specifies internal IDs for querying records. If set, the cutDate parameter will not be used.
- `requestId`: (Optional) You can include an async request ID, which is utilized for asynchronous data retrieval.
- `cacheDuration`: Specifies the cache duration in hours. Setting it to 0 bypasses cache for data retrieval.
- `manualDispatch`: Enables manual asynchronous dispatch, useful for handling large datasets.
- `requestPageSize`: Determines the page size for pagination of the result set.
- `pageNumber`: Specifies the page index for the result set when using pagination.

```python
variables = {
    "recordType": "salesOrder",
    "cutDate": "2023-07-24T16:32:24-08:00",
    "hours": 0,
    "cacheDuration": 0,
    "manualDispatch": True,
    "requestId": "async_request_123",
    "requestPageSize": 10,
    "pageNumber": 2,
}
payload = {
    "query": document,
    "variables": variables,
    "operation_name": "getRecords",
}
response = netsuite_graphql_engine.netsuite_graphql(**payload)
print(json.loads(response)["data"]["records"])
```

You can also trigger the async function for handling this query as follows:

```python
params = {
    "request_id": "async_request_123",
}
netsuite_graphql_engine.netsuite_get_records_async(**params)
```

This example showcases how to efficiently retrieve records from NetSuite by specifying a cut-off date, allowing for fine-grained control over data retrieval. It also supports pagination and asynchronous data retrieval for handling large datasets.

### Example: Mutation 'insertUpdateRecord'

This example illustrates how to use the 'insertUpdateRecord' mutation to either insert or update a record entity in NetSuite.

**Parameters:**
- `recordType`: Specifies the NetSuite record type you want to interact with.
- `entity`: Represents the data to be inserted or updated in JSON format.
- `transactionRecordType`: Optional. If the 'recordType' is 'task', this parameter is required to specify the associated transaction record type.
- `requestId`: Optionally, you can include an async request ID, which is used for asynchronous data retrieval.

```python
## Insert/update a sales order.
variables = {
    "recordType": "salesOrder",
    "entity": {
        "billingAddress": {
            "addr1": "123 Random St",
            "attention": "John Doe",
            "city": "Randomville",
            "country": "_randomCountry",
            "firstName": "John",
            "lastName": "Doe",
            "state": "Random State",
            "zip": "12345",
        },
        "class": "Random Class",
        "customFields": {
            "custbody_credit_card_type": "Random Type",
            "custbody_inside_delivery": False,
            "custbody_lift_gate": False,
            "custbody_delivery_type": "Random Delivery",
            "custbody_fob_remarks": "Random Remarks",
            "custbody_freight_terms": "Random Terms",
            "custbody_order_type": "Random Order Type",
        },
        "email": "john.doe@random.com",
        "entityStatus": "CUSTOMER-Closed Won",
        "firstName": "John",
        "items": [
            {
                "customFields": {},
                "price": "19.99",
                "qty": "2.0000",
                "sku": "random-001",
            }
        ],
        "lastName": "Doe",
        "nsCustomerId": "987654",
        "otherRefNum": "0987654321",
        "paymentMethod": "Random Payment",
        "shipDate": 30,
        "shipMethod": "Random Ship Method",
        "shippingAddress": {"attention": " ", "country": "_randomCountry"},
        "source": "Random Source",
        "subsidiary": "Random Subsidiary",
    },
    "requestId": "async_request_123",
}
payload = {
    "query": document,
    "variables": variables,
    "operation_name": "insertUpdateRecord",
}
response = netsuite_graphql_engine.netsuite_graphql(**payload)
print(json.loads(response)["data"]["insertUpdateRecord"]["record"])
```

You can also trigger the async function to handle this mutation as follows:

```python
params = {
    "request_id": "async_request_123",
}
netsuite_graphql_engine.netsuite_insert_update_record_async(**params)
```

This example demonstrates how to insert or update records in NetSuite using GraphQL. It provides a detailed JSON representation of the entity to be inserted or updated, along with optional parameters such as the associated transaction record type and async request ID for asynchronous processing.

## License

The NetSuite GraphQL Engine is licensed under the MIT License.

```
MIT License

Copyright (c) [Year] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Support

For support and inquiries related to the NetSuite GraphQL Engine, please refer to the following resources:

- **GitHub Repository**: [Link to GitHub Repository](https://github.com/ideabosque/netsuite_graphql_engine)
- **Issues**: If you encounter any issues or have questions, please open an issue on the GitHub repository.
- **Documentation**: Detailed documentation and usage instructions can be found in the repository's README and Wiki.

We welcome your contributions and feedback to improve this module and make it even more valuable for the community.

Feel free to adapt and modify these sections based on your specific requirements and the structure of your project.