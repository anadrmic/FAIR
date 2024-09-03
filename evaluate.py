from repositories import retrieve_metadata
from assess import assess
import os
import utils

def initialize():
    """
    Initialize the application by gathering user input for repository selection and search criteria.

    Returns:
        tuple: A tuple containing the repository choice and keywords for the search.
    """
    print("\nWelcome to the FAIR metrics assessment tool!\n")
    print("Please select a data repository from the options below:")
    repositories = {
        '1': "ArrayExpress",
        '2': "Gene Expression Omnibus",
        '3': "GWAS Catalog",
        '4': "ENCODE",
        '5': "GENOMIC DATA COMMONS",
        '6': "ICGC"
    }

    for key, value in repositories.items():
        print(f"{key}. {value}")

    repository_choice = input("\nEnter the number corresponding to your choice: ").strip()

    while repository_choice not in repositories:
        print("Invalid choice. Please enter a number between 1 and 6.")
        repository_choice = input("Enter the number corresponding to your choice: ").strip()

    if repository_choice == "4":
        repository_choice = handle_encode_choice(repository_choice)
        print("\n")

    keywords = handle_keyword_choice()
    print("\n")

    path = "results/"
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)  
        if os.path.isfile(file_path):  
            utils.initialize_output_file(file_path)
    return repository_choice, keywords


def handle_encode_choice(repository_choice):
    """
    Handle specific choices for the ENCODE repository.

    Args:
        repository_choice (str): The current repository choice.

    Returns:
        str: Updated repository choice including entity specification.
    """
    print("\nFor the ENCODE repository, you can assess either biosamples or experiments.")
    print("1. Biosamples")
    print("2. Experiments")
    entity = input("Enter the number corresponding to your choice: ").strip()

    while entity not in ['1', '2']:
        print("Invalid choice. Please enter either 1 or 2.")
        entity = input("Enter the number corresponding to your choice: ").strip()

    return repository_choice + entity


def handle_keyword_choice():
    """
    Handle the user's decision to assess the whole database or specific keywords.

    Returns:
        list: A list of keywords for the search or an empty list if assessing the whole database.
    """
    print("\nDo you want to assess the whole database or use specific keywords?")
    whole_db_answer = input("Enter 'y' for the whole database or 'n' for specific keywords: ").strip().lower()

    while whole_db_answer not in ['y', 'n']:
        print("Invalid input. Please enter 'y' or 'n'.")
        whole_db_answer = input("Enter 'y' for the whole database or 'n' for specific keywords: ").strip().lower()

    keywords = []
    if whole_db_answer == 'n':
        print("\nEnter specific keywords for your search (one per entry). Type 'done' when finished:")
        while True:
            keyword = input("Enter a keyword (or 'done' to finish): ").strip()
            if keyword.lower() == 'done':
                break
            elif keyword:
                keywords.append(keyword)

    return keywords


def main():
    """
    Main function to run the FAIR metrics assessment tool.
    """
    repository_choice, keywords = initialize()
    metadata_list, request_status, url = retrieve_metadata(repository_choice, keywords)
    scores = assess(metadata_list, keywords, repository_choice, url, request_status)

    print("\nAssessment complete! Here are your scores:")
    print(scores)


if __name__ == "__main__":
    main()
