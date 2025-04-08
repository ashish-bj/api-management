import os
import requests
import re
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

api_key = os.getenv("AZURE-OPENAI-API-KEY")
azure_endpoint = os.getenv("AZURE-OPENAI-ENDPOINT")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORGANIZATION= os.getenv("GITHUB_ORGANIZATION")
REPO = os.getenv("GITHUB_REPOSITORY")  # Format: "owner/repo"
PR_NUMBER = os.getenv("PR_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not api_key or not azure_endpoint:
    raise ValueError("Azure OpenAI API key and endpoint must be set in the environment variables.")
  
#os.environ["AZURE_OPENAI_ENDPOINT"] = "https://YOUR-ENDPOINT.openai.azure.com/"

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
        # Convert to string
        diff_text = "\n".join(changes)
        print(diff_text)
        
# client = AzureOpenAI(
#     api_key=os.environ["AZURE_OPENAI_API_KEY"],
#     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#     api_version="2024-05-01-preview",  # Specify the API version to use
# )
       
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",  # or your deployment
    api_version="2024-12-01-preview",  # or your api version
    api_key=os.environ["AZURE-OPENAI-API-KEY"],
    azure_endpoint=os.environ["AZURE-OPENAI-ENDPOINT"],
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

messages = [

    SystemMessage(
        content="You are a pull request reviwer!"
    ),
    HumanMessage(
        content="You are a helpful assistant that review github pull requests. You analyze the code changes and provide insights. check for syntax errors, explain what changes are about & its impact, check for vulnerabilities or potential bug & also check for hardcoded passwords. provide summary in shortest possible format for codeowners to make decision of approve pull request or not. Depending upon critical issues observed, conclude summary with 'Merge Pull Reuest = Yes' or 'Merge Pull Request = No' "
    ),
    HumanMessage(content=diff_text),
]
ai_msg = llm.invoke(messages)
#ai_msg
print(ai_msg.content)

#check for pr review outcome
# with open('output.log') as f:
#     if 'Merge Pull Request = No' in f.read():
#         print("true")
#         pr-url = f"https://api.github.com/repos/ashish-bj/{REPO}/pulls/{PR_NUMBER}"
#         payload = {
#             "state":"closed"  # Replace with {} if you want to clear it
#         }
#         requests.patch(pr-url, headers=headers, json=payload)
