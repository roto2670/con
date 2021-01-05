import base64
import csv
import os.path
from datetime import datetime, timezone, timedelta
import tempfile
import signal
import sys

from authlib.jose import jwt
from dateutil.relativedelta import relativedelta
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
from firebase_admin import messaging
from firebase_admin import storage
import json
import pytz
import qrcode
import requests
import shutil
import time


THE_KEY = 'CopeWithCOVID-19'
NUM_TESTS = 20

ACCESS_VALID_FOR = 24 * 100  # hours by default
LOCATIONS = set([0, 1, 100, 1000])

cred = credentials.Certificate(os.path.expanduser("~/.google/serviceAccountKey.json"))
firebase_admin.initialize_app(cred, {
    'storageBucket': 'skec-fujairah-3a656.appspot.com',
    'databaseURL': 'https://skec-fujairah-3a656.firebaseio.com'
})
fs = firestore.client()
bucket = storage.bucket()

work_statuses = {
    'ON DUTY': 1,
    'QUARANTINE': 2,
    'ISOLATION': 3,
    'HOSPITALIZED': 4,
    'HOSPITALIZED - ICU': 5,
    'TERMINATION': 6,
    'RESIGNED': 7,
    'DEMOBILIZATION': 8,
    'VACATION': 9,
    'BUSINESS TRIP': 10,
    'OTHERS': 11
}

# Update users in batch. No side effects if failed.
# Compare with the previous file (in Firebase Storage), and only update what's changed.
def update_users_and_stats(user_filename=None, test_run=False, send_warnings=False, force_update=False, should_update_stats=False, tz=pytz.timezone('Asia/Dubai')):
    success = True
    if not user_filename:
        raise Exception("No user file is given.")
    user_blob_path = 'stats/users.csv'
    users, _ = load_users(user_blob_path=user_blob_path)

    # Statistics
    base_stats = {
             u'confirmed': 1541, # count in user reports
             #u'deaths': 0, # count in user reports
             #u'recovered': 0, # count in user reports
             u'active_positives': 0, # count in users
             u'close_contacts': 0, # count in users
             u'quarantined': 0, # count in users
             u'isolated': 0, # count in users
             u'hospitalized': 0, # count in users
             #u'avg_new_cases': 0, # average from stats
             #u'avg_new_deaths': 0, # average from stats
             u'headcount': 0, # count in users (status > -1)
             u'ts': firestore.SERVER_TIMESTAMP
         }

    dbman = {'batch': fs.batch(), 'count': 0}
    total_records = 0
    valid_records = 0
    skipped_user_records = 0
    skipped_test_records = 0
    dup_checks = set()
    hr_cols = [
        'Role_1',
        'Registration_1',
        'Name_1',
        'Nationality_1',
        'Dob_1',
        'gender_1',
        'contact_no_1',
        'company_id_1',
        'join_date_1',
        'area_1',
        'company_1',
        'sub_tier_1',
        'department_1',
        'job_category_1',
        'job_category_2',
        'location_1',
        'room_no_1',
        'work_statu_1',
        'Quarantine_isolation',
        'covid_current_status_1',
        'access_id_1',
        'require_sa_1',
        'enable_ac_1',
    ]

    access_db_ref = db.reference('/access')
    with open_csv(user_filename) as usersfile:
        _ = [usersfile.readline() for i in range(6)]  # the first unused 6 lines
        reader = csv.DictReader(usersfile)
        for row in reader:
            total_records += 1
            uid = row['company_id_1'].strip().upper()
            fullname = row['Name_1'].strip().upper()

            # Check skipping conditions
            if not uid:
                continue
            if 'Registration_1' in row and row['Registration_1'].strip().upper() != 'YES':
                continue
            if uid in dup_checks:
                print(f"DUPLICATE ID!: {uid}")
                continue

            # Proceed with this only if 1) a new user, 2) user data has changed
            should_update = uid not in users or diff_dicts(users[uid], row, cols=hr_cols)

            try:
                if not row['Dob_1'] or row['Dob_1'].strip() == '#N/A' or row['Dob_1'].strip() == '#REF!':
                    dob = datetime(1, 1, 1)
                else:
                    dob = datetime.strptime(row['Dob_1'].strip().replace('/', '-'), '%d-%b-%y')
                    if dob.year >= 2020: # Adjust the birth year
                        dob = dob.replace(year=dob.year-100)
                dob = dob.replace(tzinfo=timezone.utc)
                gender = row['gender_1'].strip().upper()
                nationality = row['Nationality_1'].strip().upper()
                employer = row['company_1'].strip().upper()
                camp = row['location_1'].strip().upper()
                room = row['room_no_1'].strip().upper()
                phone_number = row['contact_no_1'].strip()
                department = row['department_1'].strip().upper()
                pv_area = row['area_1'].strip().upper()
                job_cat1 = row['job_category_1'].strip().upper()
                job_cat2 = row['job_category_2'].strip().upper()
                role = parse_role(row['Role_1'].strip())
                work_status = work_statuses.get(row['work_statu_1'].strip().upper(), 1)
                if uid in users:
                    prev_work_status = work_statuses.get(users[uid]['work_statu_1'].strip().upper(), 1)
                else:
                    prev_work_status = None  # new user
                quarantine_reason = row['Quarantine_isolation'].strip().upper()
                positive = row['covid_current_status_1'].strip().upper() == 'POSITIVE'
                access_id = row.get('access_id_1', '')
                require_sa = row.get('require_sa_1', '').strip().upper() == 'YES'
                enable_ac = row.get('enable_ac_1', '').strip().upper() == 'YES'
                if should_update or force_update:
                    doc = fs.collection(u'users').document(uid)
                    data = {
                        u'fullname': fullname,
                        u'dob': dob,
                        u'gender': gender,
                        u'nationality': nationality,
                        u'employer': employer,
                        u'camp': camp,
                        u'room': room,
                        u'phone_number': phone_number,
                        u'department': department,
                        u'pv_area': pv_area,
                        u'job_cat1': job_cat1,
                        u'job_cat2': job_cat2,
                        u'role': role,
                        u'status': work_status,
                        u'access_id': access_id,
                        u'require_sa': require_sa,
                        u'enable_ac': enable_ac,
                        u'ts': firestore.SERVER_TIMESTAMP
                    }

                    if uid not in users:
                        # New user
                        data[u'clinic_status'] = 1
                        data[u'op_status'] = 1
                        data[u'test_referred'] = False
                    elif work_status >= 2 and work_status <= 8:
                        # if quarantine, isolation, etc., clear clinic_status and op_status
                        data[u'clinic_status'] = 1
                        data[u'op_status'] = 1

                    if not test_run:
                        if work_status == 6 or work_status == 7:
                            # Terminated
                            delete_from_db(dbman, doc)
                            print(f"Deleting {fullname}:{uid}")
                            try:
                                auth.delete_user(uid)
                            except:
                                pass # it doesn't matter if it fails
                        else:
                            set_to_db(dbman, doc, data, merge=uid in users)
                    if uid not in users:
                        print(f"New User {fullname}:{uid}")
                    elif not force_update:
                        print(f"Updating {fullname}:{uid}")

                    if not test_run and access_id and work_status != prev_work_status:
                        # Update access
                        if work_status >= 2 and work_status <=8 and (require_sa or enable_ac):
                            # quarantine, isolation, hospitalized, terminated, demobilized, etc.
                            # Block the user
                            access_db_ref.set({access_id: "0"})
                        elif work_status == 1:
                            # Allow the user again
                            access_db_ref.set({access_id: "1"})
                else:
                    skipped_user_records += 1

                # Count the total confirmed
                prev_tr = False
                for i in range(1, NUM_TESTS):
                    cur_tr = 'POSITIVE' in row.get(f"C-19_MassTest_Result {i}", '').strip().upper()
                    # Count the number of FIRST Positives
                    increment(not prev_tr and cur_tr, base_stats, 'confirmed')
                    #increment(cur_tr, base_stats, 'confirmed')
                    prev_tr = cur_tr

                valid_records += 1
                increment(True, base_stats, 'headcount')
                increment(work_status == 2, base_stats, 'quarantined')
                increment(work_status == 3, base_stats, 'isolated')
                increment(work_status >= 4 and work_status <= 5, base_stats, 'hospitalized')
                increment(positive, base_stats, 'active_positives')
                increment(quarantine_reason == 'CLOSE CONTACT', base_stats, 'close_contacts')
                dup_checks.add(uid)
            except Exception as e:
                print(f"Skipping due to Errors: {fullname} ({uid}), error={e}")
                success = False

    if should_update_stats:
        stats_doc = None
        stats = None
        today = datetime.now(tz=tz)
        query = fs.collection(u'covid19_stats').order_by(u'ts', direction=firestore.Query.DESCENDING).limit(1)
        for doc in query.stream():
            stats = doc.to_dict()
            stats_doc = doc.reference
            if 'deaths' in stats and stats['deaths']:
                base_stats[u'recovered'] = base_stats['confirmed'] - base_stats['active_positives'] - stats['deaths']
        if not test_run:
            if not stats_doc or stats['ts'].astimezone(tz).day != today.day:
                stats_doc = fs.collection(u'covid19_stats').document()
                print("Using new Stats Document")
                set_to_db(dbman, stats_doc, base_stats)
            else:
                print("Updating the existing Document")
                set_to_db(dbman, stats_doc, base_stats, merge=True)
    print(f"Stats: {base_stats}")

    if valid_records > 0 and not test_run:
        print(f"Skipped {skipped_user_records} users, {skipped_test_records} tests.")
        if dbman['count'] > 0:
            dbman['batch'].commit()
            print("Flushing the remaining to DB...")
        print(f"Total committed to DB: {valid_records}/{total_records}")
        # Back up the data file for the future comparison
        data_file = bucket.blob(user_blob_path)
        data_file.upload_from_filename(user_filename)
        print("Successfully saved the data file to the storage.")
    else:
        print(f"Test Run. {valid_records}/{total_records}")

    return success



# Helper to load all users from the previous MasterFile
# If user_filename is given, it's used first
def load_users(user_blob_path=None, user_filename=None, encoding='utf-8'):
    users = {}
    if user_blob_path and not user_filename:
        users_blob = bucket.get_blob(user_blob_path)
    else:
        users_blob = None
    if users_blob:
        # Loading the last database
        last_filename = tempfile.mktemp()
        with open(last_filename, 'wb') as usersfile:
            users_blob.download_to_filename(last_filename)
        print(f"Downloaded users to {last_filename}")
        user_filename = last_filename

    if not user_filename:
        raise Exception("No user files given")

    with open_csv(user_filename) as usersfile:
        _ = [usersfile.readline() for i in range(6)]  # the first unused 6 lines
        reader = csv.DictReader(usersfile)
        for row in reader:
            uid = row['company_id_1'].strip().upper()
            if uid:
                users[uid] = row
    return users, user_filename


# Helper to open the csv file with a proper encoding
def open_csv(filename):
    try:
        with open(filename, newline='\r\n') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pass
        return open(filename, newline='\r\n')
    except UnicodeDecodeError:
        print(f"{filename}: trying windows-1252")
        return open(filename, newline='\r\n', encoding='windows-1252')


# Helper to write to DB in batch
def set_to_db(dbman, doc, data, merge=False):
    dbman['batch'].set(doc, data, merge=merge)
    dbman['count'] += 1
    count = dbman['count']
    if count > 100:
        print(f"Committing {count} writes...")
        dbman['batch'].commit()
        dbman['batch'] = fs.batch()
        dbman['count'] = 0


# Helper to delete from DB in batch
def delete_from_db(dbman, doc):
    dbman['batch'].delete(doc)
    dbman['count'] += 1
    count = dbman['count']
    if count > 100:
        print(f"Committing {count} writes...")
        dbman['batch'].commit()
        dbman['batch'] = fs.batch()
        dbman['count'] = 0


# Helper to parse the given test_date if non-empty string.
def parse_test_date(test_date):
    if test_date:
        try:
            parsed = datetime.strptime(test_date, '%d-%b-%y')
            if parsed.year >= 2020: # Adjust the birth year
                parsed = parsed.replace(year=test_date.year-100)
            return parsed
        except Exception as e:
            print(e)
            return None
    return None


# Helper to parse the given test_date if non-empty string.
def parse_retest(row, test_number):
    try:
        test_date = parse_test_date(row[f'T.Date\n(Re-T-{test_number})'])
        result_date = parse_test_date(row[f'T.Result\n(Re-T-{test_number})'])
        result = parse_test_result(row[f'Result\n(Re-T-{test_number})'])
        return test_date, result_date, result
    except KeyError:
        return None, None, 0


# Helper to parse the given test_date if non-empty string.
def parse_test_result(test_result):
    if test_result:
        return 1 if test_result.upper() == 'POSITIVE' else -1
    return 0


# Helper to increment the value in the dictionary if the given condition is True
def increment(cond, m, k):
    if cond:
        m[k] += 1


# Helper to parse the given role text and return the corresponding role number.
def parse_role(role):
    role = role.upper()
    if role == 'ADMIN':
        return 1
    elif role == 'CLINIC':
        return 2
    else:
        return 0


# Helper to load the country-wide stats from the COVID tracker (Oxford).
def get_country_stats(date):
    try:
        print(f"Calling the country stats API: {date}")
        response = requests.get('https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/actions/are/' +
                                date.strftime("%Y-%m-%d"))
        country_stats = response.json()
        total_cases = country_stats['stringencyData']['confirmed']
        total_deaths = country_stats['stringencyData']['deaths']
        stringency_index = country_stats['stringencyData']['stringency']
        print(f"{total_cases}, {total_deaths}, {stringency_index}")
        return total_cases, total_deaths, stringency_index
    except Exception as e:
        print(f"Something wrong with the country stats API: {country_stats}")
        print(e)
        # Data not available. Copy from the past?
    return None, None, None


# Helper to check and return True if the two dictionaires are different.
# If cols is given, it will only check the given column names.
def diff_dicts(a, b, cols=None):
    keys = cols if cols else b.keys()
    for kb in keys:
        if kb not in a and kb not in b:
            continue
        elif kb not in a and kb in b or a[kb] != b[kb]:
            # if there's any new columns or the value has been changed.
            return True
    return False


# Terminate a user with the given emirates ID.
def terminate_user(emirates_id):
    pass


# Delete all terminated/inactive users
def cleanup_users():
    dbman = {
        'count': 0,
        'batch': fs.batch()
    }
    count = 0
    query = fs.collection(u'users')
    for doc in query.stream():
        #if doc.id.startswith('999-') or doc.id.startswith('784-0000-0000000') or doc.id.startswith('AR-'):
        #    continue  # Skip test users
        if doc.id.startswith('784-') and not doc.id.startswith('784-0000-00000'):
            delete_from_db(dbman, doc.reference)
            count += 1

    if count > 0:
        if dbman['count'] > 0:
            dbman['batch'].commit()
        print(f"Deleted {count} users.")
    else:
        print("No users to delete.")


# Delete all messages for the given user.
def cleanup_messages(user_id, dbman=None):
    if not dbman:
        dbman = {
            'count': 0,
            'batch': fs.batch()
        }
    count = 0
    query = fs.collection(u'messages').where(u'from', '==', user_id)
    for doc in query.stream():
        delete_from_db(dbman, doc.reference)
        count += 1
    if count > 0:
        if dbman['count'] > 0:
            dbman['batch'].commit()
        print(f"Deleted {count} messages for {user_id}")
    else:
        print(f"No messagse to delete for {user_id}")


# Helper to delete all test results
def delete_all_test_results():
    dbman = {
        'count': 0,
        'batch': fs.batch()
    }
    count = 0
    query = fs.collection(u'test_results')
    for doc in query.stream():
        delete_from_db(dbman, doc.reference)
        count += 1
    if count > 0:
        if dbman['count'] > 0:
            dbman['batch'].commit()
        print(f"Deleted {count} test results")
    else:
        print("No test results to delete")


# Helper to delete old self-assessments that are no-risk
# NOTE: This is an EXPENSIVE function. Try to run this once every weekend!
def delete_old_self_assessments(days=14):
    dbman = {
        'count': 0,
        'batch': fs.batch()
    }
    count = 0
    today = datetime.now()
    while_ago = (today - timedelta(days=days))
    query = fs.collection(u'self_reports').where(u'ts', '<=', while_ago)
    for doc in query.stream():
        delete_from_db(dbman, doc.reference)
        count += 1
    if count > 0:
        if dbman['count'] > 0:
            dbman['batch'].commit()
        print(f"Deleted {count} self-assessments that are older than {days} days.")
    else:
        print("No self-assessments to delete")


# This will delete all messages that are OLD.
def delete_old_messages(days=30):
    dbman = {
        'count': 0,
        'batch': fs.batch()
    }
    count = 0
    today = datetime.now()
    while_ago = (today - timedelta(days=days))
    query = fs.collection(u'messages').where(u'ts', '<=', while_ago)
    for doc in query.stream():
        delete_from_db(dbman, doc.reference)
        count += 1
    if count > 0:
        if dbman['count'] > 0:
            dbman['batch'].commit()
        print(f"Deleted {count} messages that are older than {days} days.")
    else:
        print("No messages to delete")


# Send notifications to all users for self-assessment reminders.
def send_self_assessment_reminders(tz=pytz.timezone('Asia/Dubai')):
    users = set()
    for user in auth.list_users().iterate_all():
        users.add(user.uid)
    today = datetime.now(tz=tz).replace(hour=0, minute=0, second=0, microsecond=0)
    # All self-assessments
    query = fs.collection(u'self_reports').where(u'ts', '>', today.astimezone(pytz.utc))
    for doc in query.stream():
        user = doc.get(u'reporter')
        if user.id in users:
            users.remove(user.id)

    successes= 0
    # Now we have those who have not submitted self-assessments
    for user_id in users:
        doc = fs.collection(u'users').document(user_id).get()
        if doc.exists:
            name = doc.get('fullname')
            try:
                f_token = doc.get('f_token')
                if f_token:
                    title = "Self-Assessment OVERDUE"
                    message = "Submit your Self-Assessment NOW!"
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=message
                        ),
                        data={
                            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                            'id': 'self-assessment',
                            'status': 'self-assessment',
                            'title': title,
                            'body': message
                        },
                        android=messaging.AndroidConfig(
                            priority='high',
                            notification=messaging.AndroidNotification(
                                title=title,
                                body=message,
                                priority='max',
                                visibility='public'
                            )
                        ),
                        token=f_token
                    )
                    messaging.send(message)
                    print(f'Successfully sent self-assessment reminder to {name}({user_id})')
                    successes += 1
                else:
                    print(f'No token exists for {name}({user_id})')
            except Exception as e:
                print(f'Error while sending the reminder to {name}({user_id}): {e}')
    total = len(users)
    print(f"Sent reminders to {successes}/{total}.")


# Send notifications to all users for app update
def send_app_update_reminders(tz=pytz.timezone('Asia/Dubai')):
    users = set()
    for user in auth.list_users().iterate_all():
        users.add(user.uid)

    successes= 0
    # Now we have those who have not submitted self-assessments
    #query = fs.collection(u'users').where(u'deviceId', 'not-in', ['android', 'ios'])
    query = fs.collection(u'users').where(u'version', '<', '34')
    docs = [doc for doc in query.stream()]
    for doc in docs:
        if doc.exists and doc.id in users:
            user_id = doc.id
            name = doc.get('fullname')
            try:
                f_token = doc.get('f_token')
                if f_token:
                    title = "Please update WINVID"
                    message = "You are using an old version. Please update NOW."
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=message
                        ),
                        data={
                            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                            'id': 'app-update',
                            'status': 'app-update',
                            'title': title,
                            'body': message
                        },
                        android=messaging.AndroidConfig(
                            priority='high',
                            notification=messaging.AndroidNotification(
                                title=title,
                                body=message,
                                priority='max',
                                visibility='public'
                            )
                        ),
                        token=f_token
                    )
                    messaging.send(message)
                    print(f'Successfully sent app update reminder to {name}({user_id})')
                    successes += 1
                else:
                    print(f'No token exists for {name}({user_id})')
            except Exception as e:
                print(f'Error while sending the reminder to {name}({user_id}): {e}')
    total = len(users)
    print(f"Sent reminders to {successes}/{total}.")


def send_notification(user_id, title='Just a test message from Winvid', message='Please ignore this. Just a test.', status='message'):
    user = fs.collection(u'users').document(user_id).get()
    if status == 'message':
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message
            ),
            data={
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                'id': 'PDknZbcEotcCFIvckbAM',
                'status': status,
                'channel_id': 'winvid',
                'title' : title,
                'body': message
            },
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    title=title,
                    body=message,
                    priority='max',
                    visibility='public'
                )
            ),
            token=user.get('f_token')
        )
    else:
        message = messaging.Message(
            data={
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                'id': 'PDknZbcEotcCFIvckbAM',
                'status': status,
                'channel_id': 'winvid',
            },
            token=user.get('f_token')
        )

    response = messaging.send(message)
    print('Successfully sent a message to the user:', response)


def refresh_kiosk(kiosk_id=None):
    kiosk_tokens = []
    if not kiosk_id:
        kiosk_query = fs.collection(u'kiosks')
        for kiosk in kiosk_query.stream():
            try:
                kiosk_tokens.append(kiosk.get(u'f_token'))
            except:
                pass
    else:
        kiosk = fs.collection(u'kiosks').document(kiosk_id).get()
        kiosk_tokens.append(kiosk.get(u'f_token'))

    for token in kiosk_tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Refreshing Kiosk",
                    body="We're updating the Kiosk. Please wait."
                ),
                token=token
            )
            response = messaging.send(message)
            print('Successfully sent a message to the Kiosk:', response)
        except Exception as e:
            print('Error while refreshing the Kiosk:', e)


# Upload the profile photo of the user ID
def upload_profile(uid, filename):
    with open(filename, 'rb') as f:
        files = {'file': f.read()}
        r = requests.post(f"https://skec-fujairah.loc8.dev:10443/api/upload/image?id={uid}", files=files, verify=True)
        #r = requests.post(f"http://203.233.111.6:5000/api/profile?user_id={uid}&file_name={filename}", files=files)
        print(f"Status == {r.status_code}")
        if r.ok:
            print(f"File uploaded! {r.text}")
        else:
            print(f"Error uploading file! {r.text}")
        print(f"{r.request.headers}")


# Mark all users who have not installed the app and who have not done self-assessment
def mark_users_with_no_app_no_assessment(tz=pytz.timezone('Asia/Dubai')):
    # Download the users file from Stroage
    # Query firestore to remove the users
    user_blob_path = 'stats/users.csv'
    users, _ = load_users(user_blob_path=user_blob_path)
    inst_counter = 0
    # All installations
    for user in auth.list_users().iterate_all():
        if user.uid in users:
            users[user.uid]['app_installed'] = 'Yes'
            inst_counter += 1

    sa_counter = 0
    today = datetime.now(tz=tz)
    yesterday = (today - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
    # All self-assessments
    query = fs.collection(u'self_reports').where(u'ts', '>', yesterday.astimezone(pytz.utc))
    for doc in query.stream():
        user = doc.get(u'reporter')
        if user.id in users:
            users[user.id]['self_assessment'] = 'Yes'
            sa_counter += 1
        else:
            print(f"User not in the list: {user.id}")
    print(f"# of self-assessments for today: {sa_counter}")
    print(f"# of registered users as of today: {inst_counter}")

    csv_filename = tempfile.mktemp()
    with open(csv_filename, 'w', newline='') as csvfile:
        fields = [
            'company_id_1',
            'Name_1',
            'contact_no_1',
            'area_1',
            'company_1',
            'sub_tier_1',
            'department_1',
            'job_category_1',
            'job_category_2',
            'location_1',
            'app_installed',
            'self_assessment',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')

        writer.writeheader()
        for uid, user in users.items():
            writer.writerow(user)
    print(f"Finished: {csv_filename}")
    return csv_filename


# Update the stats that are not MasterFile-based
# Note: try to run this every midnight
def update_stats(tz=pytz.timezone('Asia/Dubai')):
    today = datetime.now(tz=tz)
    yesterday = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    stats_doc = None
    stats = None
    query = fs.collection(u'covid19_stats').order_by(u'ts', direction=firestore.Query.DESCENDING).limit(1)
    for doc in query.stream():
        stats = doc.to_dict()
        stats_doc = doc.reference

    if stats['ts'].astimezone(tz).day != today.day:
        # Needs a new record for today
        stats_doc = fs.collection(u'covid19_stats').document()
        stats['selfassessments'] = 0  # Reset
        print("Using new Stats Document")
    if 'selfassessments' not in stats:
        stats['selfassessments'] = 0  # Init
        print("Updating the existing Stats Document")

    # Count close-contacts and symptomatics
    #stats['close_contacts'] = 0
    #stats['symptomatics'] = 0
    #query = fs.collection(u'users').where(u'clinic_status', '>=', 2).where(u'clinic_status', '<=', 3)
    #for doc in query.stream():
    #    status = doc.get(u'clinic_status')
    #    if status == 2:
            #stats['close_contacts'] += 1
    #        pass
    #    elif status == 3:
            #stats['symptomatics'] += 1
    #        pass
    #    else:
    #        print(f"Unexpected status! {status}")

    # Country-wide stats update
    country_total_cases, country_total_deaths, stringency_index = get_country_stats(yesterday)
    if country_total_cases:
        stats['country_total_cases'] = country_total_cases
        stats['country_total_deaths'] = country_total_deaths
        stats['stringency_index'] = stringency_index
    else:
        print("Country stats not available.")

    stats['ts'] = today.astimezone(pytz.utc)
    stats_doc.set(stats, merge=True)
    print(f"Successfully updated stats for yesterday: {yesterday}, {stats}")


# Generate last month's observation reports and their corresponding resolutions in csv file
def generate_observation_reports(today=None, tz=pytz.timezone('Asia/Dubai')):
    reports = {}
    reporters = {} # reporters cache
    resolvers = {} # resolvers cache
    if not today:
        today = datetime.now(tz=tz)
    start_at = (today - relativedelta(months=2)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_at = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # All self-assessments
    query = fs.collection(u'compliance_reports').where(u'ts', '>', start_at.astimezone(pytz.utc)).where(u'ts', '<', end_at.astimezone(pytz.utc)).order_by(u'ts', direction=firestore.Query.ASCENDING)
    counter = 0
    for doc in query.stream():
        data = doc.to_dict()
        if 'reporter' not in data:
            continue # too old data

        if data['category'] == 0:
            category = "Indoor/Outdoor Gathering"
        elif data['category'] == 1:
            category = "PPE"
        elif data['category'] == 2:
            category = "Disinfection"
        elif data['category'] == 3:
            category = "Sanitizer"
        elif data['category'] == 4:
            category = "House Keeping"
        elif data['category'] == 5:
            category = "Other"
        else:
            category = "Unknown"

        location_type = data.get('location')
        if location_type == 0:
            location = "Camp"
        elif location_type == 1:
            location = "Work Site"
        elif location_type == 2:
            location = "Transportation"
        elif location_type == 3:
            location = "Other"
        else:
            location = "Unknown"

        resolution_type = data.get('resolution_type', 1)
        if resolution_type == 1:
            resolution = "Open"
        elif resolution_type == 2:
            resolution = "Closed"
        elif resolution_type == 3:
            resolution = "Postponed"
        elif resolution_type == 4:
            resolution = "Declined"
        else:
            resolution = "N/A"

        resolver_ref = data.get('resolver')
        resolver = {}
        if resolver_ref:
            if resolver_ref.id in resolvers:
                resolver = resolvers[resolver_ref.id]
            else:
                resolver_doc = resolver_ref.get()
                if resolver_doc.exists:
                    resolver = {
                        'Responder-1': resolver_doc.get('employer'),
                        'Responder-2': resolver_doc.get('fullname'),
                    }

        reporter_company_id = data['reporter'].id
        if reporter_company_id in reporters:
            reporter = reporters[reporter_company_id]
        else:
            reporter_doc = data['reporter'].get()
            if reporter_doc.exists:
                reporter_data = reporter_doc.to_dict()
                reporter = {
                    'Reporter-1': reporter_data.get('employer', 'N/A'),
                    'Reporter-2': reporter_company_id,
                    'Reporter-3': reporter_data.get('fullname'),
                    'Reporter-4': reporter_data.get('phone_number', 'N/A')
                }
                reporters[reporter_company_id] = reporter
            else:
                reporter = {}
        counter += 1
        reports[doc.id] = {
            'No-1': counter,
            'Description-1': category,
            'Description-2': location,
            'Description-3': data['message'],
            'Remarks-1': data.get('resolution_note', ''),
            'Date & Time-1': data['ts'].astimezone(tz),
            'Issue closed-1': 'resolution_ts' in data and data['resolution_ts'].astimezone(tz) or ''
        }
        reports[doc.id].update(reporter)
        reports[doc.id].update(resolver)

    csv_filename = tempfile.mktemp()
    with open(csv_filename, 'w', newline='') as csvfile:
        csvfile.writelines([
            'No.,Date & Time,Reporter (User) ,Reporter (User) ,Reporter (User) ,Reporter (User) ,Category,Location,Description,Responder (PIC) ,Responder (PIC) ,Issue closed (Date & Time),Remarks\n',
            ',,Company,Company ID,Name,Mobile Number,,,,Company,Name,,\n'
        ])
        fields = [
            'No-1',
            'Date & Time-1',
            'Reporter-1',
            'Reporter-2',
            'Reporter-3',
            'Reporter-4',
            'Description-1',
            'Description-2',
            'Description-3',
            'Responder-1',
            'Responder-2',
            'Issue closed-1',
            'Remarks-1',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')

        writer.writeheader()
        sorting_key = lambda x: x[1]['No-1']
        for _, report in sorted(reports.items(), key=sorting_key):
            writer.writerow(report)
    print(f"Finished: {csv_filename}")
    return csv_filename


# Generate last month's clinic reports and their corresponding resolutions in csv file
def generate_clinic_reports(today=None, tz=pytz.timezone('Asia/Dubai')):
    cc_reports = {} # close contacts
    ss_reports = {} # suspected symptoms
    reporters = {} # reporters cache
    resolvers = {} # resolvers cache
    if not today:
        today = datetime.now(tz=tz)
    start_at = (today - relativedelta(months=2)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_at = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # All self-assessments
    query = fs.collection(u'clinic_history').where(u'ts', '>', start_at.astimezone(pytz.utc)).where(u'ts', '<', end_at.astimezone(pytz.utc)).order_by(u'ts', direction=firestore.Query.ASCENDING)
    cc_counter = 0
    ss_counter = 0
    all_data = []
    for doc in query.stream():
        data = doc.to_dict()
        all_data.append((doc.id, data))
    for doc_id, data in all_data:
        action_type = data['action']
        if action_type > 4 or action_type < 3:
            continue # Skip OP actions

        resolver_ref = data.get('staff')
        resolver = {}
        if resolver_ref:
            if resolver_ref.id in resolvers:
                resolver = resolvers[resolver_ref.id]
            else:
                resolver_doc = resolver_ref.get()
                if resolver_doc.exists:
                    resolver = {
                        'Responder-1': resolver_doc.get('employer'),
                        'Responder-2': resolver_doc.get('fullname'),
                    }

        reporter_company_id = data['user'].id
        if reporter_company_id in reporters:
            reporter = reporters[reporter_company_id]
        else:
            reporter_doc = data['user'].get()
            if reporter_doc.exists:
                try:
                    phone_number = reporter_doc.get('phone_number')
                except:
                    phone_number = ''
                reporter = {
                    'Reporter-1': reporter_doc.get('employer'),
                    'Reporter-2': reporter_company_id,
                    'Reporter-3': reporter_doc.get('fullname'),
                    'Reporter-4': phone_number
                }
                reporters[reporter_company_id] = reporter
            else:
                reporter = {}

        reports = None
        counter = 0
        item = ''
        sa = data['sa']
        if not sa or sa['score'] < 10:
            print(f"Warning! No self-assessment found for {doc_id}")
            continue # Skip no-risk cases
        elif sa['score'] == 10:
            # Close contacts
            reports = cc_reports
            cc_counter += 1
            counter = cc_counter
            item = 'Close Contact'
        else:
            # Suspected symptoms
            reports = ss_reports
            ss_counter += 1
            counter = ss_counter
            item = 'Suspected Symptom'

        reports[doc_id] = {
            'No-1': counter,
            'Item-1': item,
            'Remarks-1': '',
            'Date & Time-1': sa['ts'].astimezone(tz),
            'Action taken-1': action_type == 4 and data['ts'].astimezone(tz) or '',
            'Action taken-2': action_type == 3 and data['ts'].astimezone(tz) or ''
        }
        reports[doc_id].update(reporter)
        reports[doc_id].update(resolver)

    csv_filename = tempfile.mktemp()
    with open(csv_filename, 'w', newline='') as csvfile:
        csvfile.writelines([
            'No.,Item,Date & Time,Reporter (User) ,Reporter (User) ,Reporter (User) ,Reporter (User) ,Responder (Clinic) ,Responder (Clinic) ,Action taken,Action taken,Remarks\n',
            ',,,Company,Company ID,Name,Mobile Number,Company,Name,Released (Date & Time),Referred Test (Date & Time),\n'
        ])
        fields = [
            'No-1',
            'Item-1',
            'Date & Time-1',
            'Reporter-1',
            'Reporter-2',
            'Reporter-3',
            'Reporter-4',
            'Responder-1',
            'Responder-2',
            'Action taken-1',
            'Action taken-2',
            'Remarks-1',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')

        writer.writeheader()
        sorting_key = lambda x: x[1]['No-1']
        counter = 1
        for _, report in sorted(cc_reports.items(), key=sorting_key) + sorted(ss_reports.items(), key=sorting_key):
            report['No-1'] = counter
            writer.writerow(report)
            counter += 1
    print(f"Finished: {csv_filename}")
    return csv_filename


# Genererate QR code for authenticating the given Kiosk
def generate_kiosk_qr_code(kiosk_id, output_path):
    header = {
        'alg': 'HS256'
    }
    payload = {
        'iss': 'SOS',
        'sub': 'KIOSK',
        'id': kiosk_id,
    }
    key = THE_KEY
    s = jwt.encode(header, payload, key)
    print(f"JWT: {s}")

    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=20,
        border=4,
    )
    qr.add_data(s)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"Auth QR code written to {output_path}")


# Gerenate QR codes return the output file path in ZIP
# If userlist is given, it will create QR codes for the users in the userlist.
# Otherwise, it creates QR codes for all users in the lastest Master File.
def generate_qr_codes(userlist=None, enable_quick=True):
    users = None
    if userlist:
        users = userlist
    else:
        user_blob_path = 'stats/users.csv'
        users_dict, _ = load_users(user_blob_path=user_blob_path)
        users = [k for k, v in users_dict.items() if 'Registration_1' in v and v['Registration_1'].strip().upper() == 'YES']

    header = {
        'alg': 'HS256'
    }
    exp = int(time.time() * 2)  # almost none-expiring
    key = THE_KEY
    folder = tempfile.mkdtemp()
    print(f"Temporarily generating QR codes in {folder}. QuickMode={enable_quick}.")
    count = 0
    for user_id in users:
        if enable_quick:
            s = "!!" + base64.b64encode(user_id.encode('ascii')).decode('ascii')
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_Q,
                box_size=10,
                border=4,
            )
        else:
            payload = {
                'iss': 'SOS',
                'sub': 'SIGNIN',
                'exp': exp,
                'id': user_id,
            }
            s = jwt.encode(header, payload, key)
            qr = qrcode.QRCode(
                version=8,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=7,
                border=4,
            )
        qr.add_data(s)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        output_path = os.path.join(folder, user_id + '.png')
        img.save(output_path)
        count += 1
    # Zip the folder
    result_path = tempfile.mktemp()
    shutil.make_archive(result_path, 'zip', folder)
    try:
        shutil.rmtree(folder, ignore_errors=True)
    except:
        pass
    print(f"{count} QR codes created at {result_path}.zip")
    return result_path


# Enable or disable access control permissions based on self-assessment submissions (or non-submissions).
# User will lose access if
#   1. not submit their self-assessment AND their temperature measurement for 24 hours (can change)
#   2. found to have close contact and/or suspected symptoms
#   3. in quarantine or in isolation
#
# This function will block the program and not return until sig-kill'ed
def run_access_controller():
    base_url = 'https://172.16.5.9:5556'
    enable_url = base_url + '/users/access/enabled'
    disabl_url = base_url + '/users/access/disabled'
    extend_url = base_url + '/users/access/extend'

    def get_user_info(uid):
        url = f"{base_url}/users/{uid}/server/ALL"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()
        if not results:
            return None
        return results

    def update_access(uid, servers, access):
        params = {
            'user_id': uid,
            'server_list': servers
        }
        if access:
            params['extend_hour'] = ACCESS_VALID_FOR
            response = requests.post(enable_url, json=params, timeout=10)
        else:
            response = requests.post(disabl_url, json=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        if not results
            raise Exception("Request failed")
        for result in results:
            if not result['result']:
                raise Exception("Request failed")

    def extend_access(uid, servers, hours):
        params = {
            'user_id': uid,
            'extend_hour': hours,
            'server_list': servers
        }
        response = requests.post(extend_url, json=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        if not results
            raise Exception("Request failed")
        for result in results:
            if not result['result']:
                raise Exception("Request failed")

    def listner(event):
        if event.data:
            access_data = {}
            sa_data = {}
            if event.path.startswith('/sa'):
                sa_data = event.data
            elif event.path.startswith('/access'):
                access_data = event.data
            elif event.path == '/':
                # Initial fetch (ie. the system might have been shutdown for some time)
                sa_data = event.data.get('sa', {})
                access_data = event.data.get('access', {})

            # NOTE: uid refers to the ID used in the Access Control System (Biostar)
            for uid, access in access_data.items():
                try:
                    user_info = get_user_info(uid)
                    if user_info:
                        servers = [ui['server_name'] for ui in user_info]
                        enable = str(access) == '1'
                        update_access(uid, servers, enable)
                        print(f"Updated access for the user {uid} to {enable}")
                    else:
                        print(f"User {uid} does not exist. Ignoring the enable/disable request.")
                    # Delete the data
                    db.reference(f"/access/{uid}").delete()
                except:
                    print(f"Error processing access for the user {uid}")

            for uid, hours in sa_data.items():
                try:
                    user_info = get_user_info(uid)
                    if user_info:
                        servers = [ui['server_name'] for ui in user_info]
                        try:
                            hours = int(hours)
                            if hours <= 0 or hours > ACCESS_VALID_FOR:
                                hours = ACCESS_VALID_FOR
                        except:
                            hours = ACCESS_VALID_FOR
                        extend_access(uid, servers, hours)
                    else:
                        print(f"User {uid} does not exist. Ignoring the SA request.")
                    # Delete the data
                    db.reference(f"/sa/{uid}").delete()
                except:
                    print(f"Error processing access extension for the user {uid}")


    ref = db.reference()
    reg = ref.listen(listner)
    print("Successfully started access controller.")
    signal.sigwait([signal.SIGTERM, signal.SIGINT, signal.SIGKILL])
    reg.close()
    print("Successfully terminated access controller.")


# Set the user's location based on the Biostar access events
# location=0 for N/A (unknown)
# location=1 for outside
# location=100 for in-camps
# location=1000 for in-tunnels
def set_user_location(access_id, location):
    if location not in LOCATIONS:
        raise Exception("Invalid location value")

    query = fs.collection(u'users').where(u'access_id', '==', access_id)
    user_id = None
    for doc in query.stream():
        user_id = doc.id
        break

    if user_id:
        doc = fs.collection(u'users').document(user_id)
        doc.update({
            'location': location
        })
        print(f"Location updated for {user_id}: {location}")
        return True
    else:
        print(f"Location update failed: {user_id} does not exist.")
        return False


# Helper to run the given function and log any stdout/stderr to the given log file path.
def log_and_run(log_filepath, func, *args, **kwargs):
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    try:
        with open(log_filepath, 'w') as logfile:
            sys.stdout = logfile
            sys.stderr = sys.stdout
            return func(*args, **kwargs)
    finally:
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr


if __name__ == '__main__':
    # role: 0 for normal users, 1 for admins, 2 for medical staff
    #send_reminders(quarantined=True)
    #send_notification('784-0000-0000000-2', status='message')
    #send_notification('999-0000-0000000-1', status='sa-done')
    #refresh_kiosk('EaQxYstHsTXOZrt62jfq')
    #refresh_kiosk()  # Refresh all kiosks
    #update_users_and_stats('users300.csv')
    #update_users_and_stats('users-test.csv')
    #upload_profile('999-0000-0000000-3', 'guy2.jpg')
    #update_roles('roles.csv')
    #update_users_and_stats(user_filename='users_20200929.csv', test_run=False, send_warnings=False)
    #update_users_and_stats(user_filename='users_20201013.csv', test_run=True, should_update_stats=True, send_warnings=False)
    #delete_all_test_results()
    #delete_old_self_assessments()
    #delete_old_messages()
    #cleanup_users()
    #update_stats()
    #mark_users_with_no_app_no_assessment()
    #send_self_assessment_reminders()
    #send_app_update_reminders()
    #generate_observation_reports()
    #generate_clinic_reports()
    #generate_clinic_reports(today=datetime.now() + relativedelta(months=1))
    #generate_kiosk_qr_code("hbuCPrHfRhpKu49enJlG", 'admin_test_2.png') # Demo Tablet
    #generate_qr_codes(userlist=['K-120'], enable_quick=True)
    #generate_qr_codes()
    #log_and_run("test.log", generate_qr_codes, userlist=['999-0000-0000000-1', '784-0000-0000000-2'])
    #log_and_run("test.log", mark_users_with_no_app_no_assessment)
    #run_access_controller()
    pass

