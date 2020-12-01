import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='mproject', db='work_prog')
curs = db.cursor()


def time_fix_for_work_and_his():
  select1 = 'select distinct work_id from _work_history;'
  select2_form = 'select * from _work where id="{work_id}"'
  update_work_form = 'update _work set start_time="{start_time}", ' \
                     'end_time="{end_time}", accum_time={accum_time} ' \
                     'where id="{work_id}"'

  update_work_form_none_end = 'update _work set start_time="{start_time}", ' \
                              'end_time=null, accum_time={accum_time} ' \
                              'where id="{work_id}"'

  update_work_form_none_start = 'update _work set start_time=null, ' \
                                'end_time="null", accum_time={accum_time} ' \
                                'where id="{work_id}"'

  update_start_his_form = 'update _work_history set timestamp="{start_time}" ' \
                          'where state=1 and accum_time=0 and work_id="{work_id}" '

  update_finish_his_form = 'update _work_history set timestamp="{end_time}", accum_time={accum_time} ' \
                           'where state=2 and work_id="{work_id}" '
  curs.execute(select1)
  res = curs.fetchall()
  for data in res:
    work_id = data[0]
    select2_q = select2_form.format(work_id=work_id)
    curs.execute(select2_q)
    select2_res = curs.fetchall()
    if select2_res[0][10]:
      start_time = select2_res[0][10].replace(second=0)
    else:
      start_time = None
    if select2_res[0][11]:
      end_time = select2_res[0][11].replace(second=0)
    else:
      end_time = None
    if start_time and end_time:
      _accum_time = end_time-start_time
      accum_time = int(_accum_time.total_seconds())
    else:
      accum_time = 0

    if start_time and end_time:
      update_q = update_work_form.format(start_time=start_time,
                                         end_time=end_time,
                                         accum_time=accum_time,
                                         work_id=work_id)
    elif not end_time:
      update_q = update_work_form_none_end.format(start_time=start_time,
                                                  accum_time=accum_time,
                                                  work_id=work_id)
    else:
      update_q = update_work_form_none_start.format(accum_time=accum_time,
                                                    work_id=work_id)
    curs.execute(update_q)

    update_q_start_his = update_start_his_form.format(start_time=start_time,
                                                      work_id=work_id)
    update_q_finish_his = update_finish_his_form.format(end_time=end_time,
                                                        accum_time=accum_time,
                                                        work_id=work_id)


    curs.execute(update_q_start_his)
    curs.execute(update_q_finish_his)

  db.commit()


if __name__ == '__main__':
  time_fix_for_work_and_his()