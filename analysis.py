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
    content=f"You are a codeowner reviewing a pull request. Analyze the following code changes and summarize them. Code is in array form derived from pull request files API. give summary in the following format: files, changes, summary: \"{changes}\""  # Content of the message
)

# Run the thread and poll for the result
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,  # ID of the thread
    assistant_id=assistant.id,  # ID of the assistant
    instructions="Provide summary with what has changed in code, what code will be doing, potential impacts of the code, highlight syntax errors, explain type of code, highlight if best practices are not followed, check for potential bugs or vulernabilities, and highlight if passwords are hardcoded"  # Instructions for the assistant
)

# Define output file
output_file = "output.json"

if run.status == "completed":
    # Retrieve and save the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread.id)  # List all messages in the thread
    assistant_output = {
        "assistant_output": {
            "files": "",  # Placeholder for error explanation
            #"changes": "",  # Placeholder for error cause
            "summary": "",  # Placeholder for error solution
        }
    }
    for msg in messages:
        if msg.role == "assistant":
            content = msg.content
            print(content)
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)  # Join list items into a single string
            content = str(content)  # Convert content to string
            print(content)
            Parse the content to extract explanation, cause, and solution
            if "File:" in content:
                file_start = content.find("File:") + len("File:")
                changes_start = content.find("Changes:")
                summary_start = content.find("Summary:")
                #potential_impact = content.find("**Potential Impacts**")
                # output_behaviour = content.fine("**Output Behavior**")
                # considerations = content.fine("**Contextual Considerations**")
                # best_practice = content.fine("**Best Practices Check**")
                # hardcoding = content.fine("**Hardcoded Passwords**)
                # error_handling = content.fine("**Error Handling**")                
                # code_type = content.find("**Code Type**")
                
                assistant_output["assistant_output"]["files"] = content[file_start:changes_start].strip().replace("\\n", "\n").replace("\\'", "'")
                assistant_output["assistant_output"]["summary"] = content[summary_start + len("Summary:"):].strip().replace("\\n", "\n").replace("\\'", "'")
                #assistant_output["assistant_output"]["summary"] = content[potential_impact + len("**Potential Impacts**"):].strip().replace("\\n", "\n").replace("\\'", "'")
                print(assistant_output)
    # Write the assistant's output to a JSON file
    with open(output_file, "w") as file:
        json.dump(assistant_output, file, indent=4)
    print(f"Output has been written to {output_file}")
            # if "File:" in content:
            #     # Extract File: content
            #     file_pattern = r"File:\s*([^\n]+)"
            #     changes_pattern = r"Changes:\s*([^\[]+)"
            #     summary_pattern = r"Summary:\s*([^\n]+)"
                
            #     # Use regular expression to capture relevant sections
            #     file_match = re.search(file_pattern, content)
            #     changes_match = re.search(changes_pattern, content)
            #     summary_match = re.search(summary_pattern, content)
                
            #     # Extract the 'File:' content
            #     if file_match and changes_match:
            #         file_content = file_match.group(1).strip().replace("\\n", "\n").replace("\\'", "'")
            #         assistant_output["assistant_output"]["files"] = file_content
                
            #     # Extract 'Changes:' content and ensure it is displayed on separate lines
            #     if changes_match:
            #         # Grab the changes content
            #         changes_content = changes_match.group(1).strip().replace("\\n", "\n").replace("\\'", "'")
                    
            #         # Make the changes more readable
            #         # - Split by line and remove extra empty lines
            #         formatted_changes = "\n".join([line.strip() for line in changes_content.splitlines() if line.strip()])
                    
            #         # Add bullet points to each line of the changes for clarity
            #         readable_changes = "\n".join([f"- {line}" for line in formatted_changes.splitlines()])
                
            #         assistant_output["assistant_output"]["changes"] = readable_changes
                
            #     # Extract 'Summary:' content
            #     if summary_match:
            #         summary_content = summary_match.group(1).strip().replace("\\n", "\n").replace("\\'", "'")
            #         assistant_output["assistant_output"]["summary"] = summary_content
                
            #     # Print the assistant_output to verify the results
            #     print(assistant_output) 
