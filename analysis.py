import os
import json
import re
import requests
from openai import AzureOpenAI

# Retrieve environment variables from Azure DevOps pipeline variables
# Assuming the variables are set in the pipeline as AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
api_key = os.getenv("AZURE-OPENAI-API-KEY")
azure_endpoint = os.getenv("AZURE-OPENAI-ENDPOINT")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORGANIZATION= os.getenv("GITHUB_ORGANIZATION")
REPO = os.getenv("GITHUB_REPOSITORY")  # Format: "owner/repo"
PR_NUMBER = os.getenv("PR_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(azure_endpoint)

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
    
    
# Check if the environment variables are set, raise an error if not
if not api_key or not azure_endpoint:
    raise ValueError("Azure OpenAI API key and endpoint must be set in the environment variables.")

# Set the environment variables for the Azure OpenAI client
os.environ["AZURE_OPENAI_API_KEY"] = api_key
os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint

# Initialize the Azure OpenAI client with the API key and endpoint
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-05-01-preview",  # Specify the API version to use
)
assistant = client.beta.assistants.create(
    name="CI/CD Troubleshooting Assistant",  # Name of the assistant
    instructions="You are an AI assistant that reviews the code changes and summerises it.",  # Instructions for the assistant
    tools=[{"type": "code_interpreter"}],  # Add tools if necessary, e.g., [{"type": "code_interpreter"}]
    model="gpt-4o",  # Replace with your deployed model's name
)

# Create a thread for the conversation
thread = client.beta.threads.create()


message = client.beta.threads.messages.create(
    thread_id=thread.id,  # ID of the thread
    role="user",  # Role of the message sender
    content=f"You are a codeowner reviewing a pull request. Analyze the following code changes and summarize them. Code is in array form derived from pull request files API: \"{changes}\""  # Content of the message
)

# Run the thread and poll for the result
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,  # ID of the thread
    assistant_id=assistant.id,  # ID of the assistant
    instructions="Explain what has changed, potential impacts, check for syntax, identify code type, check if best practice is not followed, check for potential bug or vulernability, and highlight if passwords are hardcoded"  # Instructions for the assistant
)

if run.status == "completed":
    # Retrieve and save the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread.id)  # List all messages in the thread

   for msg in messages:
    if msg.role == "assistant":
        content = msg.content 
        print(content)
