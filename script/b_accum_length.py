import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='mproject', db='work_prog')
curs = db.cursor()


def b_accum_length():
  tunnel_id_q = 'select distinct id from _tunnel;'
  blast_id_q_form = 'select id from _blast where tunnel_id="{t_id}"'
  b_info_q_form = 'select blasting_length from _blast_info where blast_id="{b_id}"'
  update_q_form = 'update _tunnel set b_accum_length={len} where id="{t_id}"'

  curs.execute(tunnel_id_q)
  res = curs.fetchall()
  tunnel_id_list = []
  for data in res:
    tunnel_id_list.append(data[0])

  for t_id in tunnel_id_list:
    b_id_q = blast_id_q_form.format(t_id=t_id)
    curs.execute(b_id_q)
    res = curs.fetchall()
    b_id_list = []
    for data in res:
      b_id_list.append(data[0])

    _len = 0
    for b_id in b_id_list:
      b_info_q = b_info_q_form.format(b_id=b_id)
      curs.execute(b_info_q)
      res = curs.fetchall()
      _len += res[0][0]

    update_q = update_q_form.format(len=_len, t_id=t_id)
    curs.execute(update_q)
  db.commit()


if __name__ == '__main__':
  b_accum_length()