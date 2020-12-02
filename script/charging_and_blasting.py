import pymysql
import time

db = pymysql.connect(host='127.0.0.1', user='root', password='mproject', db='work_prog')
curs = db.cursor()


def insert_charging_and_blasting():
  start_t = time.time()
  blast_all = "select * from _blast;"
  curs.execute(blast_all)
  blast_all_res = curs.fetchall()

  insert_charging = 'insert into _chargingactinfo(explosive_bulk, explosive_cartridge, ' \
                    'detonator, drilling_depth, team_id, team_nos, work_id, blast_id) '\
                    'values({explosive_bulk}, {explosive_cartridge}, {detonator}, ' \
                    '{drilling_depth}, {team_id}, {team_nos}, "{work_id}", "{blast_id}")'

  insert_blasting = 'insert into _blastingactinfo(blasting_time, start_point, ' \
                    'finish_point, blasting_length, work_id, blast_id) '\
                    'values("{blasting_time}", {start_point}, {finish_point}, ' \
                    '{blasting_length}, "{work_id}", "{blast_id}")'

  select_same_t_blast_list_form = 'select * from _blast where tunnel_id="{t_id}" order by blasting_time;'

  select_charging_form = 'select id from _work where blast_id="{b_id}" and typ=113;'

  select_blasting_form = 'select id from _work where blast_id="{b_id}" and typ=114;'

  select_b_info_form = 'select * from _blast_info where blast_id="{b_id}";'

  for blast in blast_all_res:
    t_id = blast[-1]
    same_t_blast_list_q = select_same_t_blast_list_form.format(t_id=t_id)
    curs.execute(same_t_blast_list_q)
    same_t_blast_list = curs.fetchall()
    same_t_blast_list = list(same_t_blast_list)

    select_b_info_q = select_b_info_form.format(b_id=blast[0])
    curs.execute(select_b_info_q)
    select_b_info_res = curs.fetchall()
    b_info = select_b_info_res[0]

    index = None
    for item in same_t_blast_list:
      if item[0] == blast[0]:
        index = same_t_blast_list.index(item)

    if index:
      pre_blast = same_t_blast_list[index - 1]
      select_charging_q = select_charging_form.format(b_id=pre_blast[0])
      curs.execute(select_charging_q)
      select_charging_res = curs.fetchall()

      select_blasting_q = select_blasting_form.format(b_id=pre_blast[0])
      curs.execute(select_blasting_q)
      select_blasting_res = curs.fetchall()
      if len(select_charging_res) == 1:
        cw_id = select_charging_res[0][0]
        charging_query = insert_charging.format(explosive_bulk=b_info[1],
                                                explosive_cartridge=b_info[2],
                                                detonator=b_info[3],
                                                drilling_depth=b_info[4],
                                                team_id=b_info[9] if b_info[9] else 0,
                                                team_nos=b_info[10],
                                                work_id=cw_id,
                                                blast_id=pre_blast[0])
        curs.execute(charging_query)

      if len(select_blasting_res) == 1:
        bw_id = select_blasting_res[0][0]
        blasting_query = insert_blasting.format(blasting_time=b_info[5],
                                                start_point=b_info[6],
                                                finish_point=b_info[7],
                                                blasting_length=b_info[8],
                                                work_id=bw_id,
                                                blast_id=pre_blast[0])
        curs.execute(blasting_query)
  db.commit()
  f_t = time.time()
  print("finish to data save. work_time : ", f_t - start_t)


if __name__ == '__main__':
  insert_charging_and_blasting()