import sqlite3

class SimpleSQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        create_users_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY NOT NULL,
                name VARCHAR(100) NOT NULL,
                points BIGINT UNSIGNED
            )
        '''
        with self.connection:
            self.connection.execute(create_users_table_query)

    # Users Table
    def insert_user(self, id_user):
        insert_query = '''
            INSERT INTO users (id,name,points) VALUES (?,"",0)
        '''
        with self.connection:
            self.connection.execute(insert_query, (id_user,))

    def update_points_by_id(self, ajout, id_user):
        update_query = '''
            UPDATE users
            SET points = points + ?
            WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (ajout, id_user))

    def get_user_by_id(self, id_user):
        select_query = '''
            SELECT id, name, points
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            return cursor.fetchone() #renvoie tuple

    def get_user_name_by_id(self, id_user):
        select_query = '''
            SELECT name
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            result = cursor.fetchone()
            if result:
                return str(result[0])
            else:
                return None  # Ou tout autre indication de l'absence de résultat

    def get_all_users(self):
        select_all_query = '''
            SELECT id, name, points
            FROM users ORDER BY points DESC
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall() #liste de tuples

    def get_points_by_id(self,id_user):
        select_query = '''
            SELECT points
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            result = cursor.fetchone()
            if result:
                return int(result[0])  # Renvoie la balance comme float
            else:
                return None  # Ou tout autre indication de l'absence de résultat

    # Items Table
    def insert_champion(self, name, title, gender,role, type,race, resource, typeautoattack,region,releaseyear, search_name):
        insert_query = '''
            INSERT INTO Champions (name, title, gender,role, type,race, 
            resource, typeautoattack,region,releaseyear, search_name) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (name, title, gender,role, type,race, resource, typeautoattack,region,releaseyear, search_name))

    def update_name_by_id(self,name,id_user):
        update_query = '''
            UPDATE users
            SET name = ?
            WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (name, id_user))

    def get_name_champ_by_search(self,search_name):
         select_query = '''
            SELECT name FROM Champions WHERE search_name = ?
            '''
         with self.connection:
            cursor = self.connection.execute(select_query, (search_name,))
            result =cursor.fetchone()
            if result:
                return str(result[0])
            else:
                return None

    def get_champ_title_by_search(self,name_champ):
        select_query=''' 
            SELECT title FROM Champions WHERE search_name=?;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_champ,))
            result = cursor.fetchone()
            if result:
                return str(result[0])  # Renvoie le résultat en tant que chaîne de caractères
            else:
                return None

    def get_champion_by_name(self, name_champ):
        select_query = '''
            SELECT name, title, gender,role, type,race, 
            resource, typeautoattack,region,releaseyear, search_name
            FROM Champions
            WHERE search_name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_champ,))
            return cursor.fetchone() #tuple

    def get_champ_guess_mode(self, name_champ):
        select_query = '''
            SELECT gender,role, type,race, 
            resource, typeautoattack,region,releaseyear
            FROM Champions
            WHERE search_name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_champ,))
            return cursor.fetchone() #tuple

    def get_all_champions(self): #acces bureau uniquement éviter les spam
        select_all_query = '''
            SELECT search_name
            FROM Champions ORDER BY search_name
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall() #retourne liste de tuples

    def get_champ_same_firstnletter(self,n, command_name, n_):
        select_all_query='''
            SELECT name FROM Champions
            WHERE SUBSTR(search_name, 1, ?) = SUBSTR(?, 1, ?)
            GROUP BY search_name;
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query, (n,command_name, n_))
            result = cursor.fetchall()
            if not result:  # Si result est vide (aucun enregistrement trouvé)
                return None
            return result  # Retourne la liste de tuples si des enregistrements ont été trouvés

    def get_champ_random(self):
        select_query=''' 
            SELECT search_name FROM Champions ORDER BY RANDOM() LIMIT 1;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            result = cursor.fetchone()
            if result:
                return str(result[0])  # Renvoie le résultat en tant que chaîne de caractères
            else:
                return None

    def user_exist_by_id(self,id):
        select_query="SELECT EXISTS (SELECT 1 FROM users WHERE id=?)"
        with self.connection:
            cursor = self.connection.execute(select_query, (id,))
            result = cursor.fetchone()
            return result[0] == 1 # 1 if exists, 0 if not exists

    def champ_exist_by_name(self,name):
        select_query="SELECT EXISTS (SELECT 1 FROM Champions WHERE search_name=?)"
        with self.connection:
            cursor = self.connection.execute(select_query, (name,))
            result = cursor.fetchone()
            return result[0] == 1 # 1 if exists, 0 if not exists

    def delete_user_by_id(self,id_user):
        delete_query = '''
        DELETE FROM users WHERE id=?
        '''
        with self.connection:
            cursor = self.connection.execute(delete_query, (id_user,))
            #return cursor.rowcount #nb de lignes affectées par la suppression

    def delete_champ_by_name(self,search_name):
        delete_query = '''
        DELETE FROM Champions WHERE search_name=?
        '''
        with self.connection:
            cursor = self.connection.execute(delete_query, (search_name,))
            #return cursor.rowcount #nb de lignes affectées par la suppression

    def close_connection(self):
        self.connection.close()
"""
# Example usage
database = SimpleSQLiteDatabase('my_database.db')

# Insert a new user
database.insert_user('John Doe', 1000)

# Insert a new item
database.insert_item('Apple', 5, 100)

# Update user balance by name
database.update_balance_by_name('John Doe', 1200)

# Get user by name
user = database.get_user_by_name('John Doe')
print(user)

# Don't forget to close the connection when you're done
database.close_connection()
"""
