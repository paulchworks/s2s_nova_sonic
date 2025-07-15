import json
import urllib.parse
import boto3
import requests
import datetime
import sys
import os
from zoneinfo import ZoneInfo
from requests.auth import HTTPBasicAuth
import ast 
import logging
from typing import Dict, Any
from http import HTTPStatus
from dotenv import load_dotenv


def main(summary, volunteerInterest, phone_number, area, sentiment):
    # Load environment variables from .env file
    load_dotenv()

    # Get the knowledge base ID
    JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'paul.chow.kum.siong@outlook.com')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')  # No default for security
    PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY', 'CD')
    ISSUE_TYPE_ID = os.getenv('JIRA_ISSUE_TYPE_ID', '10003')
    JIRA_DOMAIN = os.getenv('JIRA_DOMAIN', 'paulchdemo')

    # Get Singapore time
    now = datetime.datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d %H:%M:%S")

    # Set JIRA API URL
    url = f"https://{JIRA_DOMAIN}.atlassian.net/rest/api/2/issue/"

    try:
        # Build JIRA payload
        payload = json.dumps({
            "fields": {
                "project": {
                    "key": PROJECT_KEY
                },
                "summary": f"New request about {volunteerInterest} was triggered on {now} by Digital Concierge Agent",
                "description": f"Summary:\n{summary}\n\nCaller Contact No: {phone_number}\nArea: {area}\nSentiment: {sentiment}",
                "issuetype": {
                    "id": ISSUE_TYPE_ID
                }
            }
        })
        
        # Define headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Send to JIRA
        jira_response = requests.post(
            url,
            data=payload,
            headers=headers,
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        )

        print(f"Status Code: {jira_response.status_code}")
        print(json.dumps(jira_response.json(), indent=4))
        
        response_body = {
            'TEXT': {
                'body': f'The function {function} was called successfully with parameters: {summary}!'
            }
        }
        output = {
            "statusCode": HTTPStatus.OK,
            "body": json.dumps(response_body),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        return output

    except Exception as e:
        error = {"error": f"Error creating case: {str(e)}"}
        print(json.dumps(error))
        return 1


if __name__ == "__main__":
    sys.exit(main("Inernational Roaming Plans"))
