#
# Copyright 2025 Amazon.com, Inc. and its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#   http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#

import boto3
import json
import logging
import os
import sys
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)
# Load environment variables from .env file
load_dotenv()

defaultResponse = {
    "status": "error",
    "response": "Sorry we couldn't associate the relevant volunteers and volunteering opportunities in our records with the area: {areaCoverage}. Could you provide an alternative area?",
}


def get_dynamodb_table_name():
    """
    Loads and returns the DynamoDB table name from the .env file.
    """

    # Get the DynamoDB table name
    table_name = os.getenv("DYNAMODB_TABLE_NAME")

    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME not found in .env file")

    return table_name


def lookup_area(areaCoverage: str):
    """
    Looks up associated volunteers and category in DynamoDB where the areaCoverage is the primary key.

    Args:
        areaCoverage (str): The area, available volunteers and categories to look up

    Returns:
        dict: The item found in DynamoDB

    Raises:
        ValueError: If AWS credentials are missing or invalid
        ConnectionError: If there's a network issue connecting to AWS
        RuntimeError: For other DynamoDB errors
    """
    try:
        table_name = get_dynamodb_table_name()

        # Create the boto3 client with explicit credentials
        dynamodb = boto3.resource("dynamodb")

        # Get the table
        table = dynamodb.Table(table_name)

        # Get the user info from the table
        response = table.get_item(Key={"areaCoverage": areaCoverage})

        # Check if the item was found
        if "Item" in response:
            return response["Item"]
        else:
            logger.info(f"No DDB entry found for area specified")
            # set the area received for look up and send message back to Sonic that we couldn't locate it in our records. Could you provide an alternative area?
            defaultResponse["areaCoverage"] = areaCoverage
            return defaultResponse

    except (ProfileNotFound, NoCredentialsError) as e:
        logger.error(f"AWS credential error: {str(e)}")
        raise ValueError(f"AWS credential error: {str(e)}")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "ResourceNotFoundException":
            logger.error(f"Table {table_name} not found: {error_message}")
            raise RuntimeError(f"DynamoDB table not found: {error_message}")
        elif error_code == "ProvisionedThroughputExceededException":
            logger.warning(f"DynamoDB throughput exceeded: {error_message}")
            raise ConnectionError(f"DynamoDB throughput exceeded: {error_message}")
        else:
            logger.error(f"DynamoDB ClientError: {error_code} - {error_message}")
            raise RuntimeError(f"DynamoDB error: {error_message}")

    except ConnectionError as e:
        error_message = e.response["Error"]["Message"]

        logger.error(f"Network error connecting to AWS: {error_message}")
        raise ConnectionError(f"Network error connecting to AWS: {error_message}")

    except Exception as e:
        error_message = e.response["Error"]["Message"]

        logger.error(f"Unexpected error querying DynamoDB: {error_message}")
        raise RuntimeError(f"Error querying DynamoDB: {error_message}")


def main(areaCoverage: str):
    """
    Main function to process area lookup requests.

    Args:
        areaCoverage (str): The area specified to look up

    Returns:
        dict: The lookup result if successful
        int: Error code (1) if an error occurred
    """
    if not areaCoverage:
        logger.error("No area provided")
        error = {"error": "No area provided"}
        print(json.dumps(error, indent=2))
        return 1

    try:
        # Sanitize the phone number
        clean_area = str(areaCoverage).replace("-", "").strip()

        if not clean_area.isdigit():
            logger.debug(f"Invalid area format.")
            return 1

        # Attempt to look up the phone number
        result = lookup_area(clean_area)

        # Prepare and return the result
        if result:
            output = {
                "area": areaCoverage,
                "clean_area": clean_area,
                "found": True,
                "data": result,
            }
        else:
            output = {
                "area": areaCoverage,
                "clean_number": clean_area,
                "found": False,
            }

        return result

    except ValueError as e:
        # Handle configuration/validation errors
        logger.error(f"Configuration error: {str(e)}")
        error = {"error": f"Configuration error: {str(e)}"}
        print(json.dumps(error, indent=2))
        return 1

    except ConnectionError as e:
        # Handle network/connection issues
        logger.error(f"Connection error: {str(e)}")
        error = {"error": f"Connection error: {str(e)}", "retriable": True}
        print(json.dumps(error, indent=2))
        return 1

    except RuntimeError as e:
        # Handle service-specific errors
        logger.error(f"Service error: {str(e)}")
        error = {"error": f"Service error: {str(e)}"}
        print(json.dumps(error, indent=2))
        return 1

    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception(f"Unexpected error in area lookup: {str(e)}")
        error = {"error": f"Unexpected error: {str(e)}"}
        print(json.dumps(error, indent=2))
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <areaCoverage>")
        sys.exit(1)

    phone_number = sys.argv[1]
    sys.exit(main(phone_number))
