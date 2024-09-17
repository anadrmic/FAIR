import requests
import xml.etree.ElementTree as ET
import utils 

def find_repo_in_re3_data(repository_name):
    """
    Check if a repository name exists in the re3data database.

    Args:
        repository_name (str): The name of the repository to search for.

    Returns:
        int: 1 if the repository is found, 0 otherwise.
    """
    re3data_repos = "https://www.re3data.org/api/v1/repositories"
    response = requests.get(re3data_repos)
    
    if response.status_code != 200:
        return 0
    
    root = ET.fromstring(response.text)
    
    for repo in root.findall("repository"):
        repo_name = repo.find("name")
        if repo_name is not None and repo_name.text == repository_name:
            return 1
    return 0


def write_accessibility_log(principle, description, score, explanation):
    """
    Write the accessibility evaluation log to a file.

    Args:
        principle (str): The principle being evaluated.
        description (str): Description of the evaluation.
        score (int): The score of the evaluation.
        explanation (str): Explanation of the result.
    """
    with open("results/Accessibility.txt", "a") as file:
        file.write(f"\n{principle}: {description}\n")
        file.write(explanation + "\n")
        file.write(f"The score is: {score}.\n")


def A1(request_status):
    """
    Evaluate the accessibility principle A1 by checking the request status.

    Args:
        request_status (int): The status code of the request.

    Returns:
        int: 1 if the request status is 200, 0 otherwise.
    """
    score = 1 if request_status == 200 else 0
    explanation = (f"Successful request: API request returned the status {request_status}." 
                   if score else f"Request failed: API request returned the status {request_status}.")
    
    write_accessibility_log("A1", "Evaluating the accessibility principle A1 by checking if the metadata are retrievable by their identifiers using HTTPS protocol, checking the request status.", 
                            score, explanation)
    
    utils.print_evaluation("A1", "Accessibility: Request status", score, explanation)
    return score

def A1_1(request_status):
    """
    Evaluate the accessibility principle A1.1 by performing a follow-up check after A1.

    Args:
        request_status (int): The status code of the request.

    Returns:
        int: 1 if the request status is 200, 0 otherwise.
    """
    score = A1(request_status)
    explanation = (f"Follow-up check successful: API request returned the status {request_status}." 
                   if score else f"Follow-up check failed: API request returned the status {request_status}.")
    
    write_accessibility_log("A1.1", "Evaluating the accessibility principle A1.1 by performing a follow-up check after A1.", 
                            score, explanation)
    
    utils.print_evaluation("A1.1", "Accessibility: Check after A1", score, explanation)
    
    return score

def A1_2(request_status):
    """
    Evaluate the accessibility principle A1.2 by performing another check after A1.

    Args:
        request_status (int): The status code of the request.

    Returns:
        int: 1 if the request status is 200, 0 otherwise.
    """
    score = A1_1(request_status)
    explanation = ("Additional check successful: API request returned the status 200." 
                   if score else f"Additional check failed: API request returned the status {request_status}.")
    
    write_accessibility_log("A1.2", "Evaluating the accessibility principle A1.2 by performing another check after A1.", 
                            score, explanation)
    
    utils.print_evaluation("A1.2", "Accessibility: Another check after A1", score, explanation)
    
    return score

def A2(repository_choice):
    """
    Evaluate the accessibility principle A2 by checking if a repository name exists in re3data.

    Args:
        repository_choice (str): The identifier for the repository to search for.

    Returns:
        int: 1 if the repository is found, 0 otherwise.
    """
    repositories = {
        "1": "Array Express",
        "2": "Gene Expression Omnibus",
        "3": "GWAS Catalog",
        "4": "ENCODE",
        "5": "GDC",
        "6": "ICGC"
    }
    
    repo_name = repositories.get(repository_choice)
    if not repo_name:
        return 0
    
    score = find_repo_in_re3_data(repo_name)
    explanation = ("Repository is known to be accessible: the repository is available on re3data."
                   if score else "Repository is not known to be accessible: the repository is not available on re3data.")
    
    write_accessibility_log("A2", "Evaluating the accessibility principle A2 by checking if a repository name exists in re3data.", 
                            score, explanation)
    
    utils.print_evaluation("A2", "Accessibility: Repository name check", score, explanation)
    
    return score
