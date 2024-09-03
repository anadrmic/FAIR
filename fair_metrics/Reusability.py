import utils

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
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["schema_version", "status"])
    if repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["supp"])
    if repository_choice == "6":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["supp"])
    score = all_required_percentage/100
    log_reusability_evaluation("R1", all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count, score)
    utils.print_evaluation("R1", "Reusability: Metadata completeness", score, "Metadata is complete" if score == 1 else "Metadata is incomplete: it does not include the type of object nor the metadata specify the content of the data technical properties of its data file and format.")
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
    if repository_choice == "1":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, community_standards_fields)
    if repository_choice == "2":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_geo(metadata, ["suppFile"])
    if repository_choice == "3":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, [])
    if repository_choice.startswith("4"):
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["schema_version", "status"])
    if repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, [])
    if repository_choice == "6":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, [])
    score = all_required_percentage/100
    log_reusability_evaluation("R1.1", all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count, score)
    explanation = (
        "All community standards fields present" if score == 1 else
        "Some community standards fields present" if score > 0 else
        "(Meta)data do not contain license information represented using an appropriate metadata element: No community standards fields present"
    )
    utils.print_evaluation("R1.1", "Reusability: Use of community standards", score, explanation)
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
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["author"])
    if repository_choice == "2":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_geo(metadata, ["authors"])
    if repository_choice == "3":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["publicationInfo"])
    if repository_choice.startswith("4"):
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["submitted_by", "award"])
    if repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["lab"])
    if repository_choice == "6":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, ["submitter_id"])
    score = all_required_percentage/100
    log_reusability_evaluation("R1.2", all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count, score)
    explanation = (
        "All provenance metadata present" if score == 1 else
        "Some provenance metadata present" if score == 0.5 else
        "No provenance metadata present: no author, email or title specified."
    )
    utils.print_evaluation("R1.2", "Reusability: Provenance metadata completeness", score, explanation)
    return score


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

