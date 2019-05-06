import dataflow as flow
import os

my_email = ["brezovec@stanford.edu"]
email_file = 'C:/Users/User/projects/dataflow/scripts/email.txt'

try:
    with open(email_file, 'r') as f:
        user_email = f.read()
    if user_email == my_email[0]:
        emails = my_email
    else:
        emails = [my_email[0], user_email]
except:
    emails = my_email
    print('Cannot find email file.')

print('Emails: {}'.format(emails))
# Get latest log file
log_folder = 'C:/Users/User/Desktop/dataflow_logs/'
list_of_files = os.listdir(log_folder) # * means all if need specific format then *.csv
list_of_files_full = [os.path.join(log_folder, file) for file in list_of_files]
latest_file = max(list_of_files_full, key=os.path.getctime)

# Get error file with same name
error_folder = 'C:/Users/User/Desktop/dataflow_error/'
file = latest_file.split('/')[-1]
error_file = os.path.join(error_folder, file)
if os.stat(error_file).st_size != 0:
    with open(error_file, 'r') as f:
        error_info = f.read()
    for email in emails:
        flow.send_email(subject='Dataflow FAILED', message=error_info, recipient=email)
else:
    for email in emails:
        flow.send_email(subject='Dataflow SUCCESS', message=' ', recipient=email)
try:
    os.remove(email_file)
except:
    print('Could not remove email file.')