import csv
from library.helpers.send_email import send_email

def write_csv_and_email(sender, recipients, module_output):
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
