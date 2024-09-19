from tabulate import tabulate
import fair_metrics.Findability as F
import fair_metrics.Accessibility as A
import fair_metrics.Interoperability as I
import fair_metrics.Reusability as R
import matplotlib.pyplot as plt
import numpy as np


def assess(metadata, keywords, repository_choice, url, request_status):
    """
    Assess the FAIR metrics for a dataset.

    Args:
        metadata (dict): The metadata to be assessed.
        keywords (list): Keywords for findability assessment.
        repository_choice (str): The repository choice identifier.
        url (str): The URL of the dataset.
        request_status (int): The HTTP status code of the dataset request.

    Returns:
        list: A list of scores for the assessed metrics.
    """
    data = [
        ["F1 score", round(F.F1(url), 2)],
        ["F2 score", round(F.F2(metadata, repository_choice), 2)],
        ["F3 score", round(F.F3(metadata, repository_choice), 2)],
        ["F4 score", round(F.F4(metadata, repository_choice), 2)],
        ["A1 score", round(A.A1(request_status), 2)],
        ["A1.1 score", round(A.A1_1(request_status), 2)],
        ["A1.2 score", round(A.A1_2(request_status), 2)],
        ["A2 score", round(A.A2(repository_choice), 2)],
        ["I1 score", round(I.I1(metadata), 2)],
        ["I2 score", round(I.I2(metadata, repository_choice), 2)],
        ["I3 score", round(I.I3(metadata, repository_choice), 2)],
        ["R1 score", round(R.R1(metadata, repository_choice), 2)],
        ["R1.1 score", round(R.R1_1(url), 2)],
        ["R1.2 score", round(R.R1_2(metadata, repository_choice), 2)],
    ]

    print(tabulate(data, headers=["Metric", "Score"], tablefmt="fancy_grid"))

    with open("results/scores.txt", "w") as file:
        file.write(tabulate(data, headers=["Metric", "Score"], tablefmt="plain"))

    scores = {row[0]: row[1] for row in data}

    plot_fair_scores(scores)

    return [row[1] for row in data]


def plot_fair_scores(scores):
    """
    Generate a bar graph for FAIR principles scores.

    Args:
        scores (dict): A dictionary of scores for each metric.
    """
    F_score = np.mean([scores['F1 score'], scores['F2 score'], scores['F3 score'], scores['F4 score']])
    A_score = np.mean([scores['A1 score'], scores['A1.1 score'], scores['A1.2 score'], scores['A2 score']])
    I_score = np.mean([scores['I1 score'], scores['I2 score'], scores['I3 score']])
    R_score = np.mean([scores['R1 score'], scores['R1.1 score'], scores['R1.2 score']])

    principles = ['F', 'A', 'I', 'R']
    average_scores = [F_score, A_score, I_score, R_score]

    pastel_colors = ['#a2c2e2', '#7da3c0', '#6a9cc0', '#4d9dc4']

    plt.figure(figsize=(8, 6))
    bars = plt.bar(principles, average_scores, color=pastel_colors)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.01, round(yval, 4), ha='center', va='bottom')

    plt.xlabel('FAIR Principles')
    plt.ylabel('Average Score')
    plt.title('Average Scores for FAIR Principles')
    plt.ylim(0, 1.2)

    plt.savefig('results/fair_principles_scores.png', format='png', dpi=300)

    plt.show()
