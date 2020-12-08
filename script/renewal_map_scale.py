import pymysql

db = pymysql.connect(host='127.0.0.1', user='mproject', password='mproject', db='work_prog')
curs = db.cursor()

BASEPOINT_SCALE = {
    "C1ATHE": ["C1ATHE", -8.9210, 5.4167],
    "C1BTHE": ["C1BTHE", -8.9210, 5.2171],
    "C1CTHE": ["C1CTHE", -8.9210, 4.9000],
    "C1DTHE": ["C1DTHE", -8.9210, 4.4768],
    "C2ATHE": ["C1DTHE", -8.9868, 4.7379],
    "C2BTHE": ["C1DTHE", -8.9649, 3.9071],
    "C2CTHE": ["C1DTHE", -8.9868, 2.8662],
    "C2DTHE": ["C1DTHE", -8.9868, 1.6090],
    "C3ATHE": ["C1DTHE", -9.0228, 0.3614],
    "C3BTHE": ["C1DTHE", -9.0228, -1.5073],
    "C3CTHE": ["C1DTHE", -9.0008, -3.5866],
    "C3DTHE": ["C1DTHE", -9.0448, -5.8019],
}

LEN_SCALE = 0.0696


#TODO: rollback code delete after complete
def test_rollback():
  basepoint_rollback = 'update work_prog._basepoint bp set ' \
                       'x_loc=(select x_loc from work_prog_bk._basepoint bp2 ' \
                       'where bp2.id=bp.id), ' \
                       'y_loc=(select y_loc from work_prog_bk._basepoint bp2 ' \
                       'where bp2.id=bp.id);'
  curs.execute(basepoint_rollback)

  tunnel_rollback = 'update work_prog._tunnel t set ' \
                    'left_x_loc=(select left_x_loc from work_prog_bk._tunnel t2 ' \
                    'where t.id=t2.id), ' \
                    'right_x_loc=(select right_x_loc from work_prog_bk._tunnel t2 ' \
                    'where t.id=t2.id), ' \
                    'y_loc=(select y_loc from work_prog_bk._tunnel t2 ' \
                    'where t.id=t2.id), ' \
                    'width=(select width from work_prog_bk._tunnel t2 ' \
                    'where t.id=t2.id);'
  curs.execute(tunnel_rollback)

  blast_rollback = 'update work_prog._blast b set ' \
                    'left_x_loc=(select left_x_loc from work_prog_bk._blast b2 ' \
                    'where b.id=b2.id), ' \
                    'right_x_loc=(select right_x_loc from work_prog_bk._blast b2 ' \
                    'where b.id=b2.id), ' \
                    'y_loc=(select y_loc from work_prog_bk._blast b2 ' \
                    'where b.id=b2.id), ' \
                    'width=(select width from work_prog_bk._blast b2 ' \
                    'where b.id=b2.id);'
  curs.execute(blast_rollback)

  db.commit()


def renewal_map_scale():
  update_base_height = 'update work_prog._basepoint set height=15;'
  curs.execute(update_base_height)

  update_tunnel_height = 'update work_prog._tunnel set height=15;'
  curs.execute(update_tunnel_height)

  update_blast_height = 'update work_prog._blast set height=15;'
  curs.execute(update_blast_height)

  base_list_q = 'select * from work_prog._basepoint;'
  curs.execute(base_list_q)
  base_list = list(curs.fetchall())
  for b_p in base_list:
    name = b_p[1]
    if name in BASEPOINT_SCALE:
      x_loc = b_p[2] + BASEPOINT_SCALE[name][1]
      y_loc = b_p[3] + BASEPOINT_SCALE[name][2]
      update_base_loc = 'update work_prog._basepoint set x_loc={x_loc}, y_loc={y_loc} where name="{name}"'.format(x_loc=x_loc, y_loc=y_loc, name=name)
      curs.execute(update_base_loc)

      select_tunnel_list = 'select * from _tunnel where basepoint_id="{b_id}";'.format(b_id=b_p[0])
      curs.execute(select_tunnel_list)
      tunnel_list = list(curs.fetchall())
      for tunnel in tunnel_list:
        t_id = tunnel[0]
        length = tunnel[6]
        direction = tunnel[5]
        left_x_loc = tunnel[10]
        right_x_loc = tunnel[11]
        y_loc = tunnel[12]
        width = length * LEN_SCALE
        if direction == 1:
          t_r_x_loc = right_x_loc + BASEPOINT_SCALE[name][1]
          t_l_x_loc = t_r_x_loc - width
        elif direction == 0:
          t_l_x_loc = left_x_loc + BASEPOINT_SCALE[name][1]
          t_r_x_loc = t_l_x_loc + width
        t_y_loc = y_loc + BASEPOINT_SCALE[name][2]
        udpate_tunnel_loc = 'update work_prog._tunnel set left_x_loc={t_l_x_loc},' \
                            ' right_x_loc={t_r_x_loc}, y_loc={t_y_loc}, width={width}' \
                            ' where id="{t_id}"'.format(t_l_x_loc=t_l_x_loc,
                                                        t_r_x_loc=t_r_x_loc,
                                                        t_y_loc=t_y_loc,
                                                        width=width,
                                                        t_id=t_id)
        curs.execute(udpate_tunnel_loc)

        if direction == 1:
          select_blast_list = 'select * from _blast where tunnel_id="{t_id}" order by right_x_loc desc;'.format(t_id=t_id)
        elif direction == 0:
          select_blast_list = 'select * from _blast where tunnel_id="{t_id}" order by left_x_loc;'.format(t_id=t_id)
        curs.execute(select_blast_list)
        blast_list = list(curs.fetchall())

        prev_x_loc = 0
        for blast in blast_list:
          b_id = blast[0]
          b_y_loc = blast[3] + BASEPOINT_SCALE[name][2]
          b_left_x_loc = blast[1]
          b_right_x_loc = blast[2]
          select_b_info = 'select blasting_length from _blast_info where blast_id="{b_id}"'.format(b_id=b_id)
          curs.execute(select_b_info)
          b_info_length = list(curs.fetchall())[0][0]
          b_width = b_info_length * LEN_SCALE

          if direction == 1:  # West side direction
            if prev_x_loc == 0:
              b_r_x_loc = b_right_x_loc + BASEPOINT_SCALE[name][1]
            else:
              b_r_x_loc = prev_x_loc
            b_l_x_loc = b_r_x_loc - b_width
          elif direction == 0:  # East side direction
            if prev_x_loc == 0:
              b_l_x_loc = b_left_x_loc + BASEPOINT_SCALE[name][1]
            else:
              b_l_x_loc = prev_x_loc
            b_r_x_loc = b_l_x_loc + b_width

          udpate_blast_loc = 'update work_prog._blast set left_x_loc={b_l_x_loc},' \
                              ' right_x_loc={b_r_x_loc}, y_loc={b_y_loc}, width={b_width}' \
                              ' where id="{b_id}"'.format(b_l_x_loc=b_l_x_loc,
                                                          b_r_x_loc=b_r_x_loc,
                                                          b_y_loc=b_y_loc,
                                                          b_width=b_width,
                                                          b_id=b_id)
          curs.execute(udpate_blast_loc)
          if direction == 1:
            prev_x_loc = b_l_x_loc
          elif direction == 0:
            prev_x_loc = b_r_x_loc

  db.commit()


if __name__ == '__main__':
  renewal_map_scale()
  # test_rollback()