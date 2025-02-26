import sqlite3
import threading

lock = threading.Lock()

class DB:

    def __init__(self, database):

        self.connection = sqlite3.connect(database, check_same_thread = False)
        self.cursor = self.connection.cursor()
			
    def get_dl(self, id):
        with self.connection:
            with lock:
                result = self.cursor.execute("""SELECT dls.*, group_concat(categories.name) AS categories FROM dls
                                                JOIN dls_categories
                                                ON dls_categories.dl_id = dls.id
                                                JOIN categories
                                                ON categories.id = dls_categories.category_id WHERE dls.id = ?
                                                GROUP BY dls.id""", (id,)).fetchone()
                return result
            
    def get_dl_tickets(self, id):
        with self.connection:
            with lock:
                result = self.cursor.execute("""SELECT tickets.date, tickets.id, tickets.type, tickets.amount, district_departments.name as department_name
                                                FROM tickets 
                                                JOIN district_departments ON tickets.district_id = district_departments.id
                                                WHERE tickets.dl_id = ? ORDER BY DATETIME(tickets.date);""", (id,)).fetchall()
                return result

    def set_status(self, uid, status):
        with self.connection:
            with lock:
                return self.cursor.execute("UPDATE `user` SET `status` = ? WHERE `uid` = ?", (status, uid))