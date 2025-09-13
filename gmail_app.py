from __future__ import print_function

import base64
import html
import os.path
import time
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
import pandas as pd
import pygetwindow as gw
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

from chrome_operations import schedule_drafts, search_in_chrome
from configs import *


def create_message(sender, to, subject, message_text, file_path):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    # Attach the PDF file
    with open(file_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(file_path)}',
        )
        message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


def schedule_drafts_op(service):
    results = service.users().drafts().list(userId='me').execute()
    if 'drafts' in results:
        num_of_drafts = len(results['drafts'])
        logger.info(f"Number of drafts: {num_of_drafts}")
        gmail_windows = gw.getWindowsWithTitle(' - Gmail')
        schedule_drafts(num_of_drafts, gmail_windows)


def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    emails_not_delivered = {}

    # send mail
    contacts_df = pd.read_csv('contacts.csv')
    for row in contacts_df.iterrows():
        if not (isinstance(row[1]['Company name'], float) and np.isnan(row[1]['Company name'])):
            if isinstance(row[1]['Email'], float) and np.isnan(row[1]['Email']):
                emails_not_delivered[(f"{row[1]['First name']} {row[1]['Last name']} "
                                      f"{row[1]['Company name']} LinkedIn")] = "NA"
            else:
                mail_body = MAIL_BODY.format(
                    name=row[1]['First name'],
                    company=row[1]['Company name'],
                    position=row[1]['position'],
                )

                subject = SUBJECT.format(
                    position=row[1]['position'],
                )

                message = create_message(
                    'officialshashank5@gmail.com',
                    row[1]['Email'],
                    subject,
                    mail_body,
                    RESUME_PATH
                )
                try:
                    service.users().messages().send(userId='me', body=message).execute()
                    logger.info(f"Mail sent to {row[1]['First name']}: {row[1]['Email']} for position {row[1]['position']} "
                                f"at {row[1]['Company name']}")
                except:
                    pass

    logger.info("All Emails Sent")
    logger.info(f"{TIME_DIFF_FAILURE} sec waiting time for capturing all the not delivered mails")
    time.sleep(TIME_DIFF_FAILURE)
    logger.info("Checking for any delivery fails")

    for row in contacts_df.iterrows():
        results = service.users().messages().list(userId='me', q=row[1]['Email']).execute()
        messages = results.get('messages', [])[:1] if len(results.get('messages', [])) else []
        emails = {
            msg['id']: service.users().messages().get(userId='me', id=msg['id']).execute()
            for msg in messages
        }
        messages = [emails[email] for email in emails if 'labelIds' in emails[email] and "UNREAD" in emails[email]['labelIds']]

        for msg in messages:
            body = html.unescape(msg['snippet']).lower()
            if any(keyword in body for keyword in LEAVE_MSG):
                internalDate = msg['internalDate']
                internal_date_s = int(internalDate) / 1000
                internal_date = datetime.utcfromtimestamp(internal_date_s)
                now = datetime.utcnow()
                ten_minutes_ago = now - timedelta(minutes=30)
                if ten_minutes_ago <= internal_date <= now:
                    emails_not_delivered[(f"{row[1]['First name']} {row[1]['Last name']} "
                                          f"{row[1]['Company name']} LinkedIn")] = row[1]['Email']
                    break

    num_emails_not_delivered = list(set(emails_not_delivered))
    logger.info(f"Total failed email deliveries: {len(num_emails_not_delivered)}")

    # draft mail
    logger.info(f"Creating Drafts")
    sent_emails = list(set(list(contacts_df['Email'])) - set(list(emails_not_delivered.values())))
    for email in sent_emails:
        if not (isinstance(email, float) and np.isnan(email)):
            sent_emails_df = contacts_df[contacts_df['Email'] == email]
            mail_body = MAIL_BODY.format(
                name=sent_emails_df.iloc[0]['First name'],
                company=sent_emails_df.iloc[0]['Company name'],
                position=sent_emails_df.iloc[0]['position'],
            )
            subject = SUBJECT.format(
                position=sent_emails_df.iloc[0]['position'],
            )

            draft_body = {
                'message': create_message(
                    'officialshashank5@gmail.com',
                    sent_emails_df.iloc[0]['Email'],
                    subject,
                    mail_body,
                    RESUME_PATH
                )
            }
            service.users().drafts().create(userId='officialshashank5@gmail.com', body=draft_body).execute()
    logger.info(f"Drafts created for sent emails")

    # draft schedule
    schedule_drafts_op(service)
    logger.info("Waiting for capturing the failed drafts")
    time.sleep(10)
    logger.info(f"Checking for any left drafts due to network error")
    schedule_drafts_op(service)
    logger.info(f"Scheduled Drafts")

    if len(emails_not_delivered):
        logger.info(f"Opening LinkedIn Profiles for unsent email profiles")
        for _ in range(5):
            try:
                windows = gw.getWindowsWithTitle('')
                chrome_windows = [w for w in windows if 'chrome' in w.title.lower()]
                search_in_chrome(emails_not_delivered, chrome_windows)
                break
            except:
                time.sleep(2)
                logger.info("Retrying opening profiles")

    logger.info("Job Completed Successfully")


if __name__ == '__main__':
    main()
