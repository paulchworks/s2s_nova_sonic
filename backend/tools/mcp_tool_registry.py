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

# mcp_tool_registry.py
from typing import Annotated, Union
from pydantic import Field
from mcp_server import mcp_server
import logging
from . import knowledge_base_lookup
from . import retrieve_user_profile
from . import case_creation

logger = logging.getLogger(__name__)

# Knowledge Base Lookup Tool
@mcp_server.tool(
    name="lookup",
    description="Runs query against a knowledge base about MINDS to retrieve information."
)
async def lookup_tool(
    query: Annotated[str, Field(description="the query to search")]
) -> dict:
    """Look up information in the knowledge base"""
    try:
        logger.info(f"Knowledge base lookup query: {query}")
        results = knowledge_base_lookup.main(query)
        return results  
    except Exception as e:
        logger.error(f"Error in knowledge base lookup: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}

# User Profile Search Tool
@mcp_server.tool(
    name="userProfileSearch",
    description="Search for a user's records and involvement with the organization by phone number"
)
async def user_profile_search_tool(
    phone_number: Annotated[Union[int, str], Field(description="the user's phone number")]
) -> dict:
    """Search for user profile and account information"""
    try:
        phone_str = str(phone_number)
        # logger.info(f"User profile search for: {phone_str}")
        results = retrieve_user_profile.main(phone_str)
        return results  
    except Exception as e:
        logger.error(f"Error in user profile search: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}

# Case Creation Tool
@mcp_server.tool(
    name="CaseCreation",
    description="Send the summary of a conversation to JIRA for further processing"
)
async def case_creation_tool(
    summary: Annotated[Union[int, str], Field(description="conversation summary")],
    volunteerInterest: Annotated[Union[int, str], Field(description="volunteer interest")],
    phone_number: Annotated[Union[int, str], Field(description="caller contact number")],
    area: Annotated[Union[int, str], Field(description="caller area")],
    sentiment: Annotated[Union[int, str], Field(description="caller sentiment")]
) -> dict:
    """Search for user profile and account information"""
    try:
        phone_number = str(phone_number)
        summary = str(summary)
        volunteerInterest = str(volunteerInterest)
        area = str(area)
        # logger.info(f"User profile search for: {phone_str}")
        results = case_creation.main(summary, volunteerInterest, phone_number, area, sentiment)
        return results  
    except Exception as e:
        logger.error(f"Error in user profile search: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}