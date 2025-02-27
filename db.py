import sqlite3
import threading

lock = threading.Lock()

class DB:

    def __init__(self, database):

        self.connection = sqlite3.connect(database, check_same_thread = False)
        self.cursor = self.connection.cursor()

        self.cursor.execute('PRAGMA foreign_keys = ON;')
			
    def get_dl(self, id):
        with self.connection:   
            result = self.cursor.execute("""SELECT dls.*, group_concat(categories.name) AS categories FROM dls
                                            JOIN dls_categories
                                            ON dls_categories.dl_id = dls.id
                                            JOIN categories
                                            ON categories.id = dls_categories.category_id WHERE dls.id = ?
                                            GROUP BY dls.id""", (id,)).fetchone()
            return result
            
    def get_dl_tickets(self, id):
        with self.connection:
            result = self.cursor.execute("""SELECT tickets.date, tickets.id, tickets.type, tickets.amount, district_departments.name as department_name
                                            FROM tickets 
                                            JOIN district_departments ON tickets.district_id = district_departments.id
                                            WHERE tickets.dl_id = ? ORDER BY DATETIME(tickets.date);""", (id,)).fetchall()
            return result
        
    def get_districts(self):
        with self.connection:   
            result = self.cursor.execute("""SELECT * FROM district_departments""").fetchall()
            return result
    
    def get_categroies(self):
        with self.connection:   
            result = self.cursor.execute("""SELECT * FROM categories""").fetchall()
            return result
        
    def get_dist_id(self, name):
        with self.connection:   
            result = self.cursor.execute("""SELECT id FROM district_departments WHERE name = ?""", (name,)).fetchone()
            return result
        
    def get_cat_id(self, name):
        with self.connection:   
            result = self.cursor.execute("""SELECT id FROM categories WHERE name = ?""", (name,)).fetchone()
            return result
        
    def get_last_dlid(self):
        with self.connection:   
            result = self.cursor.execute("""SELECT seq FROM sqlite_sequence WHERE `name` = 'dls'""").fetchone()
            return result
        

    def add_ticket(self, distcrict_id, dl_id, reason, date, amount):
        with self.connection:
            return self.cursor.execute("INSERT INTO tickets (district_id, dl_id, type, date, amount) VALUES (?, ?, ?, ?, ?)", (distcrict_id, dl_id, reason, date, amount,))
        
    def add_dl_cat_relation(self, dl_id, cat_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO dls_categories (dl_id, category_id) VALUES (?, ?)", (dl_id, cat_id,))
        
    def add_dl(self, issue_date, lastname, name, surname):
        with self.connection:
            return self.cursor.execute("INSERT INTO dls (issue_date, lastname, name, surname) VALUES (?, ?, ?, ?)", (issue_date, lastname, name, surname,))
        
    def get_tickets(self):
        with self.connection:   
            result = self.cursor.execute("""SELECT tickets.*, district_departments.name FROM tickets
                                        JOIN district_departments ON tickets.district_id = district_departments.id
                                        ORDER BY DATETIME(tickets.date) DESC;""").fetchall()
            return result
    
    def get_dist_summary(self, id):
        with self.connection:   
            result = self.cursor.execute("""SELECT SUM(amount), COUNT(*) AS total_amount FROM tickets WHERE district_id = ?;""", (id,)).fetchone()
            return result
    
    def delete_ticket(self, id):
        with self.connection:
            return self.cursor.execute("DELETE FROM tickets WHERE id = ?", (id,))
  