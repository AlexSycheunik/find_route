import psycopg2

way_config = []

try:
    connections = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1111",
        database="router_db"
    )
    connections.autocommit = True

    with connections.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM way_config"""
        )
        for temp in cursor.fetchall():
            way_config.append({
                'way_id': temp[1],
                'truck_ban': temp[2],
                'weight_limit': temp[3],
                'way_height': temp[4],
                'way_width': temp[5]
            })

except Exception as _ex:
    print(_ex)
finally:
    if connections:
        connections.close()
        print('closed connection')
