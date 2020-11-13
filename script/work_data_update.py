import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='mproject', db='work_prog')
curs = db.cursor()


def work_data_update():
  state_time = "update _work set start_time=(SELECT timestamp FROM " \
               "work_prog._work_history where state=1 and accum_time=0 and " \
               "_work_history.work_id = _work.id order by timestamp desc limit 1)"

  end_time = "update _work set end_time=(select _work_history.timestamp from " \
             "_work_history where _work_history.state=2 and " \
             "_work_history.work_id = _work.id limit 1) where _work.state = 2"
  curs.execute(state_time)
  curs.execute(end_time)
  db.commit()


if __name__ == '__main__':
  work_data_update()