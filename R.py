import Utils
import pandas as pd

def R1(metadata_list, repository_choice):
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
