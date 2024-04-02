from deepdiff import DeepDiff


class Bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


info_str = "\n \nt1: Production, t2: Acceptance"
info_message = f"{Bcolors.BOLD}{Bcolors.WARNING}{info_str}"


def get_difference_in_json_list(acc_list, prd_list):
    list_differences = []

    for prd_value in prd_list:
        for acc_value in acc_list:
            if prd_value["id"] == acc_value["id"]:
                value_diff = DeepDiff(prd_value, acc_value, ignore_order=True)
                if value_diff != {}:
                    list_differences.append(value_diff.tree)

    return list_differences
