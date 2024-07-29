from repositories import retrieve_metadata
from assess import assess


def initialize():

    print("Which data repository do you want to use?")
    print("1. ArrayExpress")
    print("2. Gene Expression Omnibus")
    print("3. GWAS Catalog")
    print("4. ENCODE")
    print("5. GENOMIC DATA COMMONS")
    print("6. ICGC")

    repository_choice = input("Enter the number corresponding to your choice: ")
    while repository_choice not in ['1', '2', '3', '4', '5', '6']:
        print("Invalid choice. Please enter either 1, 2, 3, 4, 5 or 6.")
        repository_choice = input("Enter the number corresponding to your choice: ")

    keywords = []
    print("\nEnter specific keywords for your search (one per entry). Enter 'done' when finished:")
    while True:
        keyword = input("Enter a keyword (or 'done' to finish): ")
        if keyword.lower() == 'done':
            break
        keywords.append(keyword)

    return repository_choice, keywords


def main():

    repository_choice, keywords = initialize()
    metadata_list, request_status, url = retrieve_metadata(repository_choice, keywords)
    scores = assess(metadata_list, keywords, repository_choice, url, request_status)
    print(scores)


if __name__ == "__main__":

    main()
