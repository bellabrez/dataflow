from ftplib import FTP

#domain name or server ip:

ftp = FTP('123.server.ip')
ftp.login(user='user', passwd = 'flyeye')

ftp.cwd('/whyfix/')

def grabFile():

    filename = 'example.txt'

    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)

    ftp.quit()
    localfile.close()


from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=10)
def timed_job():
    print('This job is run every 10 seconds.')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def scheduled_job():
    print('This job is run every weekday at 10am.')

sched.configure(options_from_ini_file)
sched.start()


https://www.geeksforgeeks.org/writing-windows-batch-script/
https://stackoverflow.com/questions/4249542/run-a-task-every-x-minutes-with-windows-task-scheduler
https://datatofish.com/batch-python-script/