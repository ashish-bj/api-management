import os
import json
import re
import requests
from openai import AzureOpenAI
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage

# Retrieve environment variables from Azure DevOps pipeline variables
# Assuming the variables are set in the pipeline as AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
#api_key = os.getenv("AZURE-OPENAI-API-KEY")
#azure_endpoint = os.getenv("AZURE-OPENAI-ENDPOINT")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORGANIZATION= os.getenv("GITHUB_ORGANIZATION")
REPO = os.getenv("GITHUB_REPOSITORY")  # Format: "owner/repo"
PR_NUMBER = os.getenv("PR_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#print(azure_endpoint)

# Set up the headers with the authentication token
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# GitHub API endpoint to get PR details
pr_url = f"https://api.github.com/repos/ashish-bj/{REPO}/pulls/{PR_NUMBER}/files"

# Fetch PR details
response = requests.get(pr_url, headers=headers)

if response.status_code == 200:
    pr_data = response.json()

    print(pr_data)

    # Fetch the list of changed files in the PR
     files = response.json()
    changes = []
    
    for file in files:
        filename = file["filename"]
        patch = file.get("patch", "")  # Contains code diffs
        #print(patch)
        cleaned_text = re.sub(r"^@@.*@@\n?", "", patch, flags=re.MULTILINE)
        changes.append(f"File: {filename}\nChanges:\n{cleaned_text}\n\n")
        
        #print("file " + filename +" has following changes:")
        #print(cleaned_text)
        #print(filename)
        #print(patch)
    print(changes)
