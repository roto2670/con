import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='mproject', db='work_prog')
curs = db.cursor()

def work_data_update():
  state_time = "update work_prog_bk._work set start_time=(SELECT timestamp FROM " \
               "work_prog_bk._work_history where state=1 and accum_time=0 and " \
               "work_prog_bk._work_history.work_id = work_prog_bk._work.id " \
               "order by timestamp desc limit 1)"

  end_time = "update work_prog_bk._work set end_time=(select work_prog_bk._work_history.timestamp from " \
             "work_prog_bk._work_history where work_prog_bk._work_history.state=2 and " \
             "work_prog_bk._work_history.work_id = work_prog_bk._work.id limit 1)" \
             " where work_prog_bk._work.state = 2"
  curs.execute(state_time)
  curs.execute(end_time)

  update_hisory = 'update work_prog._work_history as his set timestamp=(select timestamp ' \
                  'from work_prog_bk._work_history wo_his where his.id=wo_his.id)' \
                  'where his.created_time < "2020-12-01 12:00:00"'
  curs.execute(update_hisory)

  up_start_time = 'update work_prog._work as his set start_time=(select start_time ' \
                  'from work_prog_bk._work wo_his where his.id=wo_his.id) ' \
                  'where his.created_time < "2020-12-01 12:00:00"'
  curs.execute(up_start_time)

  up_end_time = 'update work_prog._work as his set end_time=(select end_time ' \
                'from work_prog_bk._work wo_his where his.id=wo_his.id) ' \
                'where his.last_updated_time < "2020-12-01 12:00:00"'
  curs.execute(up_end_time)

  slect_work = 'select id, start_time, end_time from work_prog_bk._work;'
  curs.execute(slect_work)
  res = curs.fetchall()
  for data in res:
    if data[2]:
      _id = data[0]
      accum = data[2] - data[1]
      accum = int(accum.total_seconds())
      up_accum = 'update work_prog._work as his set accum_time={accum} where id="{id}" and last_updated_time < "2020-12-01 12:00:00"'.format(accum=accum, id=_id)
      curs.execute(up_accum)
      up_accum_2 = 'update work_prog._work_history as his set accum_time={accum} where work_id="{id}" and state=2 and created_time < "2020-12-01 12:00:00"'.format(accum=accum, id=_id)
      curs.execute(up_accum_2)

  db.commit()


if __name__ == '__main__':
  work_data_update()