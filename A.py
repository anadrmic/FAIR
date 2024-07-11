import pandas as pd
import requests
import xml.etree.ElementTree as ET

def find_repo_in_re3_data (repository_name):
    re3data_repos    = "https://www.re3data.org/api/v1/repositories"
    re3data_r = requests.get(re3data_repos)
    re3data_root = ET.fromstring(re3data_r.text)
    for i in range (0, len(re3data_root)):
        if re3data_root[i][1].text == repository_name: # first index is a <repository> group, 
                                                       # second index is for the tags inside (<id>, <name>, <link>)
            return 1
    return 0

def A1(request_status):
    score = 1 if request_status == 200 else 0
    df = pd.DataFrame({
        "Principle": ["A1"],
        "Description": ["Accessibility: Request status"],
        "Score": [score],
        "Explanation": ["Successful request: API request returned the status 200." if score else "Request failed: API request returned the status 400."]
    })
    print(df.head())
    return score

def A1_1(request_status):
    score = 1 if A1(request_status) == 1 else 0
    df = pd.DataFrame({
        "Principle": ["A1.1"],
        "Description": ["Accessibility: Check after A1"],
        "Score": [score],
        "Explanation": ["Follow-up check successful: API request returned the status 200." if score else "Follow-up check failed: API request returned the status 400."]
    })
    print(df.head())
    return score

def A1_2(request_status):
    score = 1 if A1(request_status) == 1 else 0
    df = pd.DataFrame({
        "Principle": ["A1.2"],
        "Description": ["Accessibility: Another check after A1"],
        "Score": [score],
        "Explanation": ["Additional check successful: API request returned the status 200." if score else "Additional check failed: API request returned the status 400."]
    })
    print(df.head())
    return score

def A2(repository_name):
    score = find_repo_in_re3_data(repository_name)

    df = pd.DataFrame({
        "Principle": ["A2"],
        "Description": ["Accessibility: Repository name check"],
        "Score": [score],
        "Explanation": ["Repository is known to be accessible: the repository available on re3data." if score else "Repository is not known to be accessible: the repository not available on re3data."]
    })
    print(df.head())  
    return score
