import pandas as pd
import utils


# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Set display width to show the entire dataframe without truncation
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)


def check_metadata_richness(metadata_list):
    """
    Check if metadata are richly described with a plurality of accurate and relevant attributes.

    Parameters:
    - metadata_list (list): List of metadata records.

    Returns:
    - results (dict): Summary of the richness check.
    """
    key_attributes = [
        'experiment_protocol', 'machine_model', 'species', 'drug_regime',
        'manufacturer', 'brand', 'experimental_conditions', 'study_design'
    ]

    results = {
        'total_records': len(metadata_list),
        'records_with_all_attributes': 0,
        'records_with_missing_attributes': 0,
        'missing_attributes_summary': {}
    }

    for attribute in key_attributes:
        results['missing_attributes_summary'][attribute] = 0

    # Check each metadata record
    for metadata in metadata_list:
        attributes_present = True
        for attribute in key_attributes:
            if attribute not in metadata or not metadata[attribute]:
                results['missing_attributes_summary'][attribute] += 1
                attributes_present = False

        if attributes_present:
            results['records_with_all_attributes'] += 1
        else:
            results['records_with_missing_attributes'] += 1

    if results['total_records'] > 0:
        results['percentage_with_all_attributes'] = (
                (results['records_with_all_attributes'] / results['total_records']) * 100
        )
        results['percentage_with_missing_attributes'] = (
                (results['records_with_missing_attributes'] / results['total_records']) * 100
        )
    else:
        results['percentage_with_all_attributes'] = 0
        results['percentage_with_missing_attributes'] = 0

    return results['percentage_with_all_attributes']

def R1(metadata_list, repository_choice):

    """
    Evaluate the reusability principle R1 by checking metadata completeness.

    Args:
        metadata_list (list): A list of metadata entries to check for completeness.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating metadata completeness.
    """

    score = check_metadata_richness(metadata_list)
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
        output, index = utils.find_list_in_list(metadata_list[0], ["authors"])
        if index:
            provenance += 1        
        output, index = utils.find_list_in_list(metadata_list[0], ["email"])
        if index:
            provenance += 1
        output, index = utils.find_list_in_list(metadata_list[0], ["title"])
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