import Utils
import pandas as pd

def R1(metadata_list, repository_choice):
    """
    Evaluate the reusability principle R1 by checking metadata completeness.

    Args:
        metadata_list (list): A list of metadata entries to check for completeness.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating metadata completeness.
    """
    score = R1_2(metadata_list, repository_choice)
    df = pd.DataFrame({
        "Principle": ["R1"],
        "Description": ["Reusability: Metadata completeness"],
        "Score": [score],
        "Explanation": ["Metadata is complete" if score == 1 else "Metadata is incomplete: it does not include the type of object nor the metadata specify the content of the data technical properties of its data file and format."]
    })
    print(df.head())
    return score

def R1_1(metadata, repository_choice):
    """
    Evaluate the reusability principle R1.1 by checking the use of community standards.

    Args:
        metadata (dict): The metadata to check for community standards fields.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating the presence of community standards fields.
    """
    community_standards_fields = ["license", "citation", "termsOfUse"]
    present_fields = [field for field in community_standards_fields if field in metadata]
    score = len(present_fields) / len(community_standards_fields)
    df = pd.DataFrame({
        "Principle": ["R1.1"],
        "Description": ["Reusability: Use of community standards"],
        "Score": [score],
        "Explanation": [
            "All community standards fields present" if score == 1 else
            "Some community standards fields present" if score > 0 else
            "(Meta)data do not contain license information represented using an appropriate metadata element: No community standards fields present"
        ]
    })
    print(df.head())
    return score

def R1_2(metadata_list, repository_choice):
    """
    Evaluate the reusability principle R1.2 by checking provenance metadata completeness.

    Args:
        metadata_list (list): A list of metadata entries to check for provenance.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating the completeness of provenance metadata.
    """
    provenance = 0
    try:
        output, index = Utils.find_list_in_list(metadata_list[0], ["authors"])
        if index:
            provenance += 1        
        output, index = Utils.find_list_in_list(metadata_list[0], ["email"])
        if index:
            provenance += 1
        output, index = Utils.find_list_in_list(metadata_list[0], ["title"])
        if index:
            provenance += 1
        if provenance == 3:
            score = 1
        elif provenance == 0:
            score = 0
        else:
            score = 0.5
    except:
        score = 0

    df = pd.DataFrame({
        "Principle": ["R1.2"],
        "Description": ["Reusability: Provenance metadata completeness"],
        "Score": [score],
        "Explanation": [
            "All provenance metadata present" if score == 1 else
            "Some provenance metadata present" if score == 0.5 else
            "No provenance metadata present: no author, email or title specified."
        ]
    })
    print(df.head())
    return score

def R1_3(metadata, repository_choice):
    """
    Evaluate the reusability principle R1.3 by checking if (meta)data meet domain-relevant community standards.

    Args:
        metadata (dict): The metadata to check for domain-relevant community standards.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        None: As the scoring is not provided for this metric.
    """
    score = None
    df = pd.DataFrame({
        "Principle": ["R1.3"],
        "Description": ["Reusability: (Meta)data meet domain-relevant community standards"],
        "Score": [score],
        "Explanation": [
            "Community standards present" if score == 1 else
            "Community standards not present: we do not provide a score for this metric."
        ]
    })
    print(df.head())
    return score
