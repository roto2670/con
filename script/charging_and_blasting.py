import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='mproject', db='work_prog')
curs = db.cursor()


def insert_charging_and_blasting():
  charging_select = "select info.explosive_bulk, info.explosive_cartridge, " \
                    "info.detonator, info.drilling_depth, info.team_id, info.team_nos," \
                    " (select id from work_prog._work as wor where info.blast_id=" \
                    "wor.blast_id and wor.typ=113 limit 1) work_id, info.blast_id " \
                    "from work_prog._blast_info as info where info.blast_id in " \
                    "(select wor.blast_id from work_prog._work as wor where " \
                    "info.blast_id=wor.blast_id and wor.typ=113);"
  curs.execute(charging_select)
  charging_res = curs.fetchall()

  insert_charging = 'insert into _chargingactinfo(explosive_bulk, explosive_cartridge, ' \
                    'detonator, drilling_depth, team_id, team_nos, work_id, blast_id) '\
                    'values({explosive_bulk}, {explosive_cartridge}, {detonator}, ' \
                    '{drilling_depth}, {team_id}, {team_nos}, "{work_id}", "{blast_id}")'

  for charging in charging_res:
    charging_query = insert_charging.format(explosive_bulk=charging[0],
                                            explosive_cartridge=charging[1],
                                            detonator=charging[2],
                                            drilling_depth=charging[3],
                                            team_id=charging[4] if charging[4] else 0,
                                            team_nos=charging[5],
                                            work_id=charging[6],
                                            blast_id=charging[7])
    curs.execute(charging_query)

  select_q = "select info.blasting_time, info.start_point, " \
             "info.finish_point, info.blasting_length," \
             " (select id from work_prog._work as wor where info.blast_id=" \
             "wor.blast_id and wor.typ=114 limit 1) work_id, info.blast_id " \
             "from work_prog._blast_info as info where info.blast_id in " \
             "(select wor.blast_id from work_prog._work as wor where " \
             "info.blast_id=wor.blast_id and wor.typ=114);"
  curs.execute(select_q)
  blasting_res = curs.fetchall()

  insert_blasting = 'insert into _blastingactinfo(blasting_time, start_point, ' \
                    'finish_point, blasting_length, work_id, blast_id) '\
                    'values("{blasting_time}", {start_point}, {finish_point}, ' \
                    '{blasting_length}, "{work_id}", "{blast_id}")'

  for blasting in blasting_res:
    blasting_query = insert_blasting.format(blasting_time=blasting[0],
                                            start_point=blasting[1],
                                            finish_point=blasting[2],
                                            blasting_length=blasting[3],
                                            work_id=blasting[4],
                                            blast_id=blasting[5])
    curs.execute(blasting_query)
  db.commit()


if __name__ == '__main__':
  insert_charging_and_blasting()