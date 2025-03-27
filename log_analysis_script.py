import os
import requests
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langgraph import LangGraph

# Fetch logs from Azure DevOps using REST API
def get_pipeline_logs(organization, project, build_id, pat):
    url = f"https://dev.azure.com/ashishjadhav0331/ashishjadhav/_apis/build/builds/17/logs?api-version=6.0"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {pat}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching logs: {response.status_code}")

# Cleanse and filter logs
def cleanse_logs(log_data):
    cleaned_logs = []
    for entry in log_data:
        if 'error' in entry or 'warning' in entry:  # Simple filtering
            cleaned_logs.append(entry)
    return cleaned_logs

# Set up Langchain for log analysis
def analyze_logs_with_langchain(logs):
    openai_api_key = "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"  # Ensure the API key is set in the environment variables
    llm = OpenAI(api_key=openai_api_key)

    log_analysis_prompt = """
    You are a log analyzer. Given the following log entries, summarize the key issues and categorize the logs into errors, warnings, and info.
    Logs: {logs}
    """

    prompt = PromptTemplate(input_variables=["logs"], template=log_analysis_prompt)
    chain = ConversationChain(llm=llm, prompt=prompt)

    log_text = "\n".join(logs)  # Convert log list into a single string
    result = chain.run(log_text)
    return result

# Visualize logs using LangGraph
def create_log_graph(logs):
    graph = LangGraph()

    for log in logs:
        if 'error' in log.lower():
            graph.add_node('Error', log)
        elif 'warning' in log.lower():
            graph.add_node('Warning', log)
        else:
            graph.add_node('Info', log)

    graph.visualize()

def main():
    # Fetch and analyze pipeline logs from Azure DevOps
    organization = os.getenv("AZURE_ORG")  # Set this in your pipeline environment
    project = os.getenv("AZURE_PROJECT")  # Set this in your pipeline environment
    build_id = os.getenv("BUILD_ID")  # Pass the build ID dynamically in the pipeline
    pat = "DkfCNB8KfxphK0ELJOS0F3llAos5wAeMoVwSUKa8aoL06rnuHaEaJQQJ99BCACAAAAAAAAAAAAASAZDO22co"  # Set the Personal Access Token (PAT) for Azure DevOps

    logs = get_pipeline_logs(organization, project, build_id, pat)
    cleaned_logs = cleanse_logs(logs)
    
    # Log analysis using Langchain
    analysis_result = analyze_logs_with_langchain(cleaned_logs)
    print("Log Analysis Result:")
    print(analysis_result)

    # Visualize the logs with LangGraph
    create_log_graph(cleaned_logs)

if __name__ == "__main__":
    main()
