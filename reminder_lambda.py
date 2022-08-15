import base64
import json
import os
from datetime import datetime
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail

THRESHOLD_NOTIFICATION_DAYS = 30
reminder_config_dict = {}


def checker(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = event.get('data', None)
    msg = pubsub_message if pubsub_message else None
    if msg and type(msg) == str:
        msg = json.loads(base64.b64decode(msg)).get('data')
    print(msg)
    if msg and msg.get('type'):
        # valid message
        process_checks()
    else:
        print("Error message - not doing anything here for: %s" % pubsub_message)


def process_checks():
    reminder_config = os.getenv('REMINDER_CONFIG')
    global reminder_config_dict
    if not reminder_config:
        print("no REMINDER_CONFIG env var is provided")
        exit(1)
    else:
        reminder_config_dict = json.loads(reminder_config)
    violation_keys = []
    c_datetime = datetime.today()

    for k, v in reminder_config_dict.items():
        due_date = v.get('due_date')
        renewal_date = v.get('renewal_date')
        due_diff = (c_datetime - datetime.strptime(due_date, '%m/%d/%Y')).days if due_date else -1
        renewal_diff = (c_datetime - datetime.strptime(renewal_date, '%m/%d/%Y')).days if renewal_date else -1
        if due_diff == -1 and renewal_diff == -1:
            violation_keys.append(k)
        elif due_diff >= 30 or renewal_diff >= 30:
            violation_keys.append(k)
        else:
            continue
    process_notification(violation_keys)


def process_notification(violations=None):
    to_mails = os.getenv('TO_EMAILS', None)
    API_KEY = os.getenv('SG_API_KEY', None)
    if to_mails is None or API_KEY is None:
        print(
            "Error dispatching notification. Required env vars are not populated. Current values are TO_EMAILs=%s and "
            "SG_API_KEY=%s" % (
                to_mails, API_KEY))
        exit(1)
    if violations is None:
        violations = []
    html_content = ''
    if len(violations) == 0:
        html_content = 'No upcoming violations for this week'
    else:
        content = [reminder_config_dict.get(v) for v in violations]
        raw_content = "\n \n Please find the list violations below: \n \n"
        html_content = raw_content + json.dumps(content, indent=4, sort_keys=True)
    to_mails = to_mails.split(',')
    message = Mail(from_email='keshi8086@gmail.com', to_emails=to_mails,
                   subject='Nagger Reminder: %s violations found' % (len(violations)),
                   plain_text_content=html_content)
    try:
        sg = SendGridAPIClient(API_KEY)
        response = sg.send(message)
        print("Status code for email dispatch: %s" % response.status_code)
    except SendGridException as e:
        print(e)


if __name__ == "__main__":
    checker({
        "data": {
            "type": "nagger"
        }
    }, None)
