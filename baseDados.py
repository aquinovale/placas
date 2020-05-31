import psycopg2
con = psycopg2.connect(host='localhost', database='placas', port=5436,
user='raspberry', password='00198500')

cur = con.cursor()

def existePlaca(placa):
    cur.execute("SELECT count(*) FROM carros WHERE placa = '" + placa + "';")
    result = cur.fetchall()
    for row in result:
        return int(row[0]) > 0

def closeConnection():
    con.close()

