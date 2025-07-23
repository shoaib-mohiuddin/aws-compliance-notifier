import os
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email(sender, recipients, subject, body_text, attachment_path):
    ses = boto3.client('ses')

    if isinstance(recipients, str):
        recipients = [recipients]

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    body = MIMEText(body_text, 'plain')
    msg.attach(body)

    with open(attachment_path, 'rb') as file:
        part = MIMEApplication(file.read())
        part.add_header('Content-Disposition', 'attachment', 
                        filename=os.path.basename(attachment_path))
        msg.attach(part)

    try:
        response = ses.send_raw_email(
          Source=sender,
          Destinations=recipients,
          RawMessage={'Data': msg.as_string()}
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("Failed to send email:", e)
