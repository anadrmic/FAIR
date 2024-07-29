import evaluate
import repositories
import assess
import statistics

print("Evaluating the whole ARRAY EXPRESS database: \n")

# Initialize repository choice and keywords
repository_choice = "1"
keywords = []

# Retrieve metadata
metadata_list, request_status, url = repositories.retrieve_metadata(repository_choice, keywords)

# Assess the metadata to get scores
scores = assess.assess(metadata_list, keywords, repository_choice, url, request_status)

# Calculate statistics
average_score = statistics.mean(scores)
std_dev_score = statistics.stdev(scores)
median_score = statistics.median(scores)
max_score = max(scores)
min_score = min(scores)
variance_score = statistics.variance(scores)

# Print statistics
print("\nStatistics for the evaluation scores:")
print(f"Average Score: {average_score}")
print(f"Standard Deviation: {std_dev_score}")
print(f"Median Score: {median_score}")
print(f"Maximum Score: {max_score}")
print(f"Minimum Score: {min_score}")
print(f"Variance: {variance_score}")
