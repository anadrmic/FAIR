import utils
import requests
from bs4 import BeautifulSoup

def check_required_fields_ae(json_elements):
    total_count = len(json_elements)
    missing_fields_count = {field: 0 for field in ["value"]}
    if total_count == 0:
        return "No JSON elements provided.", 0, 0, {}
    all_required_count = 0
    missing_all_count = 0
    for element in json_elements:
        try:
            if element["section"]["subsections"][3]["attributes"][0]["value"]:
                all_required_count += 1
            elif element["section"]["subsections"][3]["attributes"][1]["value"]:
                all_required_count += 1
            else:
                missing_all_count += 1
                missing_fields_count["value"] += 1
        except:
            missing_all_count += 1
            missing_fields_count["value"] += 1         
    all_required_percentage = (all_required_count / total_count) * 100 if total_count > 0 else 0
    missing_all_percentage = (missing_all_count / total_count) * 100 if total_count > 0 else 0
    return all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count

def check_re3data_license(repo_url):
    response = requests.get(repo_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        icons = soup.find_all('img', alt=True)
        for icon in icons:
            alt_text = icon['alt'].lower()
            if 'license' in alt_text:
                return 1  
        return 0  
    else:
        print(f"Error: Unable to access {repo_url}. Status code: {response.status_code}")
        return 0 

def log_reusability_evaluation(principle, all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count, score):
    """
    Log the reusability evaluation to a file.

    Args:
        principle (str): The principle being evaluated.
        all_required_percentage (float): Percentage of entities with all required fields.
        missing_all_percentage (float): Percentage of entities missing all required fields.
        missing_fields_count (dict): Count of missing fields by field name.
        all_required_count (int): Number of entities with all required fields.
        total_count (int): Total number of entities.
        missing_all_count (int): Number of entities missing all required fields.
    """
    with open("results/Reusability.txt", "a") as file:
        file.write(f"\n{principle}:    Evaluating the reusability principle {principle} for a given dataset by searching for predefined keywords in metadata to assess its completeness.\n")
        file.write(f"{all_required_percentage:.2f}% of entities have all required fields ({all_required_count} out of {total_count}).\n")
        file.write(f"{missing_all_percentage:.2f}% of entities are missing all required fields ({missing_all_count} out of {total_count}).\n")
        file.write("\nBreakdown of missing fields:\n")
        for field, count in missing_fields_count.items():
            file.write(f"{count} entities are missing '{field}' field.\n")
        file.write(f"The score is: {score}.\n")

def log_reusability_evaluation_2(principle, score):
    """
    Log the reusability evaluation to a file.

    Args:
        principle (str): The principle being evaluated.
        all_required_percentage (float): Percentage of entities with all required fields.
        missing_all_percentage (float): Percentage of entities missing all required fields.
        missing_fields_count (dict): Count of missing fields by field name.
        all_required_count (int): Number of entities with all required fields.
        total_count (int): Total number of entities.
        missing_all_count (int): Number of entities missing all required fields.
    """
    with open("results/Reusability.txt", "a") as file:
        file.write(f"\n{principle}:    Evaluating the reusability principle {principle} for a given dataset by searching for predefined keywords in metadata to assess its completeness.\n")
        file.write(f"The repository has a valid licence at stated at re3data.\n")
        file.write(f"The score is: {score}.\n")


def R1(metadata, repository_choice):
    """
    Evaluate the reusability principle R1 by checking metadata completeness.

    Args:
        metadata (list): A list of metadata entries to check for completeness.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating metadata completeness.
    """
    if repository_choice == "1":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["supp"])
    if repository_choice == "2":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_geo(metadata, ["suppFile"])
    if repository_choice == "3":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["supp"])
    if repository_choice.startswith("4"):
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["schema_version"])
    if repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json_gdc(metadata, ["data_format"])
    if repository_choice == "6":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["supp"])
    score = all_required_percentage/100
    log_reusability_evaluation("R1", all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count, score)
    utils.print_evaluation("R1", "Reusability: Metadata completeness", score, "Metadata is complete" if score == 1 else "Metadata is incomplete: it does not include the type of object nor the metadata specify the content of the data technical properties of its data file and format.")
    return score

def R1_1(url):

    """
    Evaluate the reusability principle R1.1 by checking the use of community standards.

    Args:
        metadata (dict): The metadata to check for community standards fields.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating the presence of community standards fields.
    """
    score = check_re3data_license(url)
    log_reusability_evaluation_2("R1.1", score)
    explanation = (
        "All community standards fields present" if score == 1 else
        "Some community standards fields present" if score > 0 else
        "(Meta)data do not contain license information represented using an appropriate metadata element: No community standards fields present"
    )
    utils.print_evaluation("R1.2", "Reusability: Use of community standards", score, explanation)
    return score

def R1_2(metadata, repository_choice):

    """
    Evaluate the reusability principle R1.2 by checking provenance metadata completeness.

    Args:
        metadata (list): A list of metadata entries to check for provenance.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The score indicating the completeness of provenance metadata.
    """

    if repository_choice == "1":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = check_required_fields_ae(metadata)
    if repository_choice == "2":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_geo(metadata, ["author"])
    if repository_choice == "3":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["author"])
    if repository_choice.startswith("4"):
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["lab"])
    if repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json_gdc(metadata, ["lab"])
    if repository_choice == "6":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["lab"])
    score = round(all_required_percentage/100, 2)
    log_reusability_evaluation("R1.2", all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count, score)
    explanation = (
        "All provenance metadata present" if score == 1 else
        "Some provenance metadata present" if score == 0.5 else
        "No provenance metadata present: no author, email or title specified."
    )
    utils.print_evaluation("R1.2", "Reusability: Provenance standards metadata completeness", score, explanation)
    return score

