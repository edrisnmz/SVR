from Main import Start
import schedule
import time
import datetime
Start()
TIMER = 0
print('A.I Run... Time to Wait')
def my_job():
    now = datetime.datetime.now()
    if now.minute in [0]:
        Start()       
        print(now)

schedule.every(1).minutes.do(my_job)

while True:
    schedule.run_pending()
    TIMER +=1
    print('>---->>>', TIMER)
    time.sleep(60)    
    

