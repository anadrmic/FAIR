import evaluate
import repositories


repository_name, keywords = evaluate.initialize()

metadata, repository_choice, url, request_status = repositories.retrieve_metadata(repository_name, keywords)
