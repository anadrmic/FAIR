from tabulate import tabulate
import fair_metrics.Findability as F
import fair_metrics.Accessibility as A
import fair_metrics.Interoperability as I
import fair_metrics.Reusability as R


def assess(metadata, keywords, repository_choice, url, request_status):

    data = [
        ["F1 score", F.F1(url)],
        ["F2 score", F.F2(keywords, metadata, repository_choice)],
        ["F3 score", F.F3(metadata, repository_choice)],
        ["F4 score", F.F4(metadata, repository_choice)],
        ["A1 score", A.A1(request_status)],
        ["A1.1 score", A.A1_1(request_status)],
        ["A1.2 score", A.A1_2(request_status)],
        ["A2 score", A.A2(repository_choice)],
        ["I1 score", I.I1(metadata)],
        ["I2 score", I.I2(metadata, repository_choice)],
        ["I3 score", I.I3(metadata)],
        ["R1 score", R.R1(metadata, repository_choice)],
        ["R1.1 score", R.R1_1(metadata, repository_choice)],
        ["R1.2 score", R.R1_2(metadata, repository_choice)],
        ["R1.3 score", R.R1_3(metadata, repository_choice)]
    ]
    print(tabulate(data, headers=["Metric", "Score"], tablefmt="fancy_grid"))

    return [row[1] for row in data]
