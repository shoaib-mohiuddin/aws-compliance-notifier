"""
This module provides a function to write CSV data to a file.
"""

import csv
from library.helpers.send_email import send_email


def write_csv(sender, recipients, module_output):
    """
    Writes the module output to a CSV file and invoke email module.
    Args:
        sender (str): Email address of the sender.
        recipients (list): List of recipient email addresses.
        module_output (dict): Output from the module containing CSV data and metadata.
    """
    if not module_output:
        print("No data to email.")
        return

    fieldnames = module_output["csv_data"]
    filename = module_output["filename"]
    csv_path = f"/tmp/{filename}"

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames[0].keys())
        writer.writeheader()
        writer.writerows(fieldnames)

    send_email(
        sender=sender,
        recipients=recipients,
        subject=module_output["subject"],
        body_text=module_output["body_text"],
        attachment_path=csv_path
    )
