import pandas as pd
import requests
import xml.etree.ElementTree as ET


# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Set display width to show the entire dataframe without truncation
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)


def find_repo_in_re3_data(repository_name):

    """
    Check if a repository name exists in the re3data database.

    Args:
        repository_name (str): The name of the repository to search for.

    Returns:
        int: 1 if the repository is found, 0 otherwise.
    """

    re3data_repos = "https://www.re3data.org/api/v1/repositories"
    re3data_r = requests.get(re3data_repos)
    re3data_root = ET.fromstring(re3data_r.text)
    for i in range(len(re3data_root)):
        if re3data_root[i][1].text == repository_name:  # first index is a <repository> group,
                                                        # second index is for the tags inside (<id>, <name>, <link>)
            return 1

    return 0


def A1(request_status):

    """
    Evaluate the accessibility principle A1 by checking the request status.

    Args:
        request_status (int): The status code of the request.

    Returns:
        int: 1 if the request status is 200, 0 otherwise.
    """

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

    """
    Evaluate the accessibility principle A1.1 by performing a follow-up check after A1.

    Args:
        request_status (int): The status code of the request.

    Returns:
        int: 1 if the request status is 200, 0 otherwise.
    """

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

    """
    Evaluate the accessibility principle A1.2 by performing another check after A1.

    Args:
        request_status (int): The status code of the request.

    Returns:
        int: 1 if the request status is 200, 0 otherwise.
    """

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

    """
    Evaluate the accessibility principle A2 by checking if a repository name exists in re3data.

    Args:
        repository_name (str): The name of the repository to search for.

    Returns:
        int: 1 if the repository is found, 0 otherwise.
    """

    score = find_repo_in_re3_data(repository_name)

    df = pd.DataFrame({
        "Principle": ["A2"],
        "Description": ["Accessibility: Repository name check"],
        "Score": [score],
        "Explanation": ["Repository is known to be accessible: the repository available on re3data." if score else "Repository is not known to be accessible: the repository not available on re3data."]
    })
    print(df.head())  

    return score

