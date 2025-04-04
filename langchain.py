import os
import re
import requests
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage
from langchain_core.messages import HumanMessage

# GitHub API token (personal access token with the necessary permissions)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# GitHub repository information
OWNER = os.getenv("GITHUB_ORGANIZATION")
REPO = os.getenv("GITHUB_REPOSITORY")  # Format: "owner/repo"
PR_NUMBER = 12  # PR number (replace with the PR you want to inspect)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up the headers with the authentication token
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# GitHub API endpoint to get PR details
pr_url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/files"

# Fetch PR details
response = requests.get(pr_url, headers=headers)

if response.status_code == 200:
    pr_data = response.json()
    
    print("Pull Request Files and Changes:")

    # List to store file changes
    changes = []

    # Process files and extract patches
    for file in pr_data:
        filename = file["filename"]
        patch = file.get("patch", "")  # Contains code diffs
        cleaned_text = re.sub(r"^@@.*@@\n?", "", patch, flags=re.MULTILINE)
        changes.append(f"File: {filename}\nChanges:\n{cleaned_text}\n\n")
    
    print("\n".join(changes))

    # Initialize LangChain model
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)

    # Prepare prompt with changes from PR
    prompt = (
        "You are a codeowner reviewing a pull request. "
        "Analyze the following code changes and summarize them in simple terms. "
        "Explain what has changed, why it might have been changed, and any potential impacts. "
        "Check for syntax, identify code type, check if best practices are followed, check for potential bugs, and highlight if passwords are hardcoded.\n\n"
        f"{' '.join(changes)}"
    )

    # Send the request to LangChain model for analysis
    response = llm([HumanMessage(content=prompt)])

    # Print the model's analysis
    print("\nAnalysis of the PR Changes:")
    print(response.content)

else:
    print(f"Error: Unable to fetch pull request details. Status Code: {response.status_code}")
