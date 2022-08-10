import base64
import json
import os
from datetime import datetime
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail

THRESHOLD_NOTIFICATION_DAYS = 30

EMAIL_NOTIFICATION_TEMPLATE = """
    

"""

reminder_config = {
    "auto_policy": {
        "due_date": "07/18/2022",
        "renewal_date": None,
        "auto_pay": True,
        "description": "Car policy handled by Geico"
    },
    "home_insurance_3331_midtown": {
        "due_date": None,
        "renewal_date": "08/08/2022",
        "auto_pay": False,
        "description": "Condo policy handled by geico"
    },
    "home_insurance_9021_devon_crest_elk_grove": {
        "due_date": None,
        "renewal_date": "04/13/2023",
        "auto_pay": False,
        "description": "Landlord's insurance policy handled by geico"
    },
    "home_warranty_810_schoolhouse_rd": {
        "due_date": None,
        "renewal_date": "08/13/2022",
        "auto_pay": False,
        "description": "Home warranty for Schoolhouse rd house handled by Fidelity"
    },
    "hoa_3331_midtown_place_city_lights": {
        "due_date": None,
        "renewal_date": None,
        "auto_pay": False,
        "due_cadence": "monthly",
        "description": "City lights hoa payments. Payments need to be paid manually"
    },
    "9021_devon_crest_way_property_tax_due": {
        "due_date": "12/10/2022",
        "renewal_date": None,
        "auto_pay": False,
        "description": "Devon crest home property tax payment needs to be made for first installment"
    },
    "3331_midtown_place_property_tax_due": {
        "due_date": "12/10/2022",
        "renewal_date": None,
        "auto_pay": False,
        "description": "San Jose condo home property tax payment needs to be made for first installment"
    },
    "810_schoolhouse_rd_property_tax_due": {
        "due_date": "12/10/2022",
        "renewal_date": None,
        "auto_pay": False,
        "description": "San Jose schoolhouse rd home property tax payment needs to be made for first installment"
    }
}


def checker(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = event.get('data', None)
    msg = pubsub_message if pubsub_message else None
    if msg and msg.get('type'):
        # valid mesage
        process_checks()
    else:
        print("Error message - not doing anything here for: %s" % pubsub_message)


def process_checks():
    violation_keys = []
    c_datetime = datetime.today()
    for k, v in reminder_config.items():
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
    # prepar notification/dispatch
    # dispatch_notification(violation_keys)
    process_notification(violation_keys)


def process_notification(violations=None):
    to_mails = os.getenv('TO_EMAILS', None)
    API_KEY = os.getenv('SG_API_KEY', None)
    if to_mails is None or API_KEY is None:
        print(
            "Error dispatching notification. Required env vars are not populated. Current values are TO_EMAILs=%s and SG_API_KEY=%s" % (
                to_mails, API_KEY))
        exit(1)
    if violations is None:
        violations = []
    html_content = ''
    if len(violations) == 0:
        html_content = 'No upcoming violations for this week'
    else:
        content = [reminder_config.get(v) for v in violations]
        raw_content = "\n \n Please find the list violations below: \n \n"
        html_content = raw_content + json.dumps(content, indent=4, sort_keys=True)
    to_mails = to_mails.split(',')
    message = Mail(from_email='keshi8086@gmail.com', to_emails=to_mails,
                   subject='Nagger Reminder: %s violations found' % (len(violations)),
                   plain_text_content=html_content)
    try:
        sg = SendGridAPIClient(API_KEY)
        response = sg.send(message)
        print("Status code for email dispatch: %s" % (response.status_code))
    except SendGridException as e:
        print(e)


if __name__ == "__main__":
    checker({
        "data": {
            "type": "nagger"
        }
    }, None)
