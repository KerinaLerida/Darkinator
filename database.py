import sqlite3
import datetime


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
                realname VARCHAR(100) NOT NULL,
                balance DOUBLE UNSIGNED
            )
        '''
        create_items_table_query = '''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                quantity INT UNSIGNED,
                price DOUBLE UNSIGNED NOT NULL
            )
        '''
        create_transactions_table_query = '''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATETIME NOT NULL,
                about VARCHAR(100) NOT NULL,

                id_user BIGINT NULL,

                credit_added DOUBLE UNSIGNED NULL,
                payment_assumed DOUBLE UNSIGNED NULL,

                old_balance DOUBLE UNSIGNED NULL,
                new_balance DOUBLE UNSIGNED NULL,

                item_name VARCHAR(100) NULL,

                quantity INT UNSIGNED NULL,
                old_quantity INT UNSIGNED NULL,
                quantity_purchased INT UNSIGNED NULL,

                price DOUBLE UNSIGNED NULL,
                old_price DOUBLE UNSIGNED NULL,
                change DOUBLE UNSIGNED NULL
            )
        '''

        with self.connection:
            self.connection.execute(create_users_table_query)
            self.connection.execute(create_items_table_query)
            self.connection.execute(create_transactions_table_query)

    # Transactions Table
    def get_users_with_positive_balance(self):
        select_query = '''
            SELECT *
            FROM users
            WHERE balance > 0;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            return cursor.fetchall()

    def get_items_with_positive_quantity(self):
        select_query = '''
            SELECT *
            FROM items
            WHERE quantity > 0;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            return cursor.fetchall()

    def has_transactions_after_or_on_september(self, year):
        september_date = f"{year}-09-01"
        select_query = '''
            SELECT EXISTS (
                SELECT 1 
                FROM transactions
                WHERE date >= ? LIMIT 1
            );
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (september_date,))
            result = cursor.fetchone()[0]
            return bool(result)

    def get_years_from_transactions(self):
        select_query = '''
            SELECT DISTINCT strftime('%Y', date) AS year
            FROM transactions;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            years = cursor.fetchall()
            return years

    def insert_buy(self, date, id_user, old_balance, new_balance, item_name, quantity, old_quantity, quantity_purchased,
                   price):
        payment_assumed = new_balance - old_balance
        insert_query = '''
            INSERT INTO transactions (date, about, id_user, old_balance, new_balance, item_name, quantity, old_quantity, quantity_purchased, price, payment_assumed) VALUES (?,"buy",?,?,?,?,?,?,?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (
            date, id_user, old_balance, new_balance, item_name, quantity, old_quantity, quantity_purchased, price,
            payment_assumed))

    def insert_balance(self, date, id_user, old_balance, new_balance):
        diff = new_balance - old_balance
        if diff > 0:
            credit_added, payment_assumed = diff, None
        elif diff < 0:
            credit_added, payment_assumed = None, diff
        insert_query = '''
            INSERT INTO transactions (date, about, id_user, old_balance, new_balance,credit_added,payment_assumed) VALUES (?,"balance",?,?,?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query,
                                    (date, id_user, old_balance, new_balance, credit_added, payment_assumed))

    def insert_item_price(self, date, item_name, price, old_price):
        if old_price == 0 or old_price is None:
            change = None
        else:
            change = (price - old_price) / old_price * 100
        insert_query = '''
            INSERT INTO transactions (date,about, item_name, price, old_price, change) VALUES (?,"price",?,?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (date, item_name, price, old_price, change))

    def insert_item_quantity(self, date, item_name, quantity, old_quantity):
        insert_query = '''
            INSERT INTO transactions (date,about, item_name, quantity, old_quantity) VALUES (?,"quantity",?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (date, item_name, quantity, old_quantity))

    def get_all_transactions(self):
        select_all_query = '''
            SELECT *
            FROM transactions ORDER BY date
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall()

    def get_transactions_since_last_update(self, derniere_update_date):
        # Sélectionner les transactions qui ont eu lieu depuis la dernière mise à jour
        select_transactions_query = '''
            SELECT *
            FROM transactions
            WHERE date > ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_transactions_query, (derniere_update_date,))
            return cursor.fetchall()

    def get_transactions_by_user(self, id_user):
        select_query = '''
            SELECT *
            FROM transactions
            WHERE id_user = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            return cursor.fetchall()

    def get_all_SOM_payments(self, date1, date2):
        select_query = '''
                    SELECT SUM(payment_assumed) AS Total_payments_assumed
                    FROM transactions
                    WHERE (about="buy" OR about="balance") AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_user_SOM_payments(self, id_user, date1, date2):
        select_query = '''
                    SELECT SUM(payment_assumed) AS Total_payments_assumed
                    FROM transactions
                    WHERE (about="buy" OR about="balance") AND id_user=? AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user, date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_all_SOM_credits(self, date1, date2):
        select_query = '''
                    SELECT SUM(credit_added) AS Total_credits_added
                    FROM transactions
                    WHERE about="balance" AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_user_SOM_credits(self, id_user, date1, date2):
        select_query = '''
                    SELECT SUM(credit_added) AS Total_credits_added
                    FROM transactions
                    WHERE about="balance" AND id_user=? AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user, date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_min_date(self):
        select_query = '''
                    SELECT MIN(date) AS First_date
                    FROM transactions
                '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_last_date(self):
        select_query = '''
                    SELECT MAX(date) AS Last_date
                    FROM transactions
                '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_dates(self):
        select_query = '''
                    SELECT date
                    FROM transactions
                '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            return cursor.fetchall()

    def get_users_about_buy_or_balance(self, date1, date2):
        select_query = '''
                    SELECT DISTINCT users.name
                    FROM transactions JOIN users ON transactions.id_user=users.id
                    WHERE (transactions.about="buy" OR transactions.about="balance") AND transactions.date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            return cursor.fetchall()

    def get_items_about_price_or_quantity(self, date1, date2):
        select_query = '''
                    SELECT DISTINCT item_name
                    FROM transactions
                    WHERE about!="balance" AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            return cursor.fetchall()

    def get_all_SOM_quantity_purchased(self, date1, date2):
        select_query = '''
                    SELECT SUM(quantity_purchased) AS Total_quantity_purchased
                    FROM transactions
                    WHERE about="buy" AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_item_SOM_quantity_purchased(self, item_name, date1, date2):
        select_query = '''
                    SELECT SUM(quantity_purchased) AS Total_quantity_purchased
                    FROM transactions
                    WHERE about="buy" AND item_name=? AND date BETWEEN ? AND ?
                '''
        with self.connection:
            cursor = self.connection.execute(select_query, (item_name, date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    def get_all_user_item_SOM_quantity_purchased_SOM_payments_assumed(self, date1, date2):
        select_query = '''
                SELECT users.id AS user_id, users.name AS user_name, 
                transactions.item_name AS item_name, 
                SUM(transactions.quantity_purchased) AS total_quantity_purchased, 
                SUM(transactions.payment_assumed) AS total_amount_spent 
                FROM transactions JOIN users 
                ON transactions.id_user = users.id 
                WHERE transactions.about = 'buy' AND transactions.date BETWEEN ? AND ?
                GROUP BY users.id, users.name, transactions.item_name 
                ORDER BY total_quantity_purchased DESC;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, ())
            return cursor.fetchall()

    def get_all_item_SOM_quantity_purchased_SOM_payments_assumed(self, date1, date2):
        select_query = '''
            SELECT transactions.item_name AS item_name,
            SUM(transactions.quantity_purchased) AS total_quantity_purchased,
            SUM(transactions.payment_assumed) AS total_amount_spent 
            FROM transactions 
            WHERE transactions.about = 'buy' AND transactions.date BETWEEN ? AND ?
            GROUP BY transactions.item_name 
            ORDER BY total_quantity_purchased DESC;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, ())
            return cursor.fetchall()

    def get_user_item_purchase_info(self, user_id, date1, date2):
        select_query = '''
                SELECT transactions.item_name AS item_name, 
                SUM(transactions.quantity_purchased) AS total_quantity_purchased, 
                SUM(transactions.payment_assumed) AS total_amount_spent 
                FROM transactions 
                JOIN users ON transactions.id_user = users.id 
                WHERE transactions.about = 'buy' 
                AND transactions.id_user = ? 
                AND transactions.date BETWEEN ? AND ?
                GROUP BY transactions.item_name;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (user_id, date1, date2))
            return cursor.fetchall()

    def get_all_item_purchase_info(self, date1, date2):
        select_query = '''
                SELECT transactions.item_name AS item_name, 
                SUM(transactions.quantity_purchased) AS total_quantity_purchased, 
                SUM(transactions.payment_assumed) AS total_amount_spent 
                FROM transactions 
                WHERE transactions.about = 'buy' 
                AND transactions.date BETWEEN ? AND ?
                GROUP BY transactions.item_name;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            return cursor.fetchall()

    def get_date_ba_ca_pa_for_user(self, user_id, date1, date2):
        select_query = '''
            SELECT date, ROUND(new_balance,2),credit_added, payment_assumed
            FROM transactions
            WHERE id_user = ? 
            AND about IN ('buy', 'balance')
            AND date BETWEEN ? AND ?
            GROUP BY date;
            '''
        with self.connection:
            cursor = self.connection.execute(select_query, (user_id, date1, date2))
            return cursor.fetchall()

    def get_date_ba_ca_pa_for_users(self, date1, date2):
        select_query = '''
            SELECT date,ROUND(new_balance,2), credit_added, payment_assumed
            FROM transactions
            WHERE about IN ('buy', 'balance')
            AND date BETWEEN ? AND ?
            GROUP BY date;
            '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            return cursor.fetchall()

    def get_date_price_change_quantity_for_item(self, item_name, date1, date2):
        select_query = '''
                    SELECT date, price, ROUND(change,2), quantity
                    FROM transactions
                    WHERE item_name = ? 
                    AND about IN ('price', 'quantity')
                    AND date BETWEEN ? AND ?
                    GROUP BY date;
                    '''
        with self.connection:
            cursor = self.connection.execute(select_query, (item_name, date1, date2))
            return cursor.fetchall()

    def get_balance_date_by_id(self, id_user, date1, date2):
        select_query = '''
                SELECT new_balance
                FROM transactions
                WHERE id_user = ?
                AND date BETWEEN ? AND ?
                ORDER BY date DESC
                LIMIT 1;
           '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user, date1, date2))
            result = cursor.fetchone()
            if result:
                return float(result[0])  # Renvoie la balance comme float
            else:
                return None

    # Users Table
    def insert_user(self, id_user, name, realname, balance):
        insert_query = '''
            INSERT INTO users (id, name,realname, balance) VALUES (?,?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (id_user, name, realname, balance))

    def update_balance_by_id(self, ajout, id_user):
        new_balance = max(0, round(self.get_balance_by_id(id_user) + ajout, 3))
        update_query = '''
            UPDATE users
            SET balance =  ?
            WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (new_balance, id_user))

    def get_user_by_id(self, id_user):
        select_query = '''
            SELECT id, name, realname, balance
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            return cursor.fetchone()  # renvoie tuple

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

    def get_user_realname_by_id(self, id_user):
        select_query = '''
            SELECT realname
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            result = cursor.fetchone()
            if result:
                return str(result[0])  # Renvoie la balance comme float
            else:
                return None  # Ou tout autre indication de l'absence de résultat

    def get_id_by_name(self, name):
        select_query = '''
            SELECT id
            FROM users
            WHERE name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name,))
            result = cursor.fetchone()
            if result:
                return int(result[0])
            else:
                return None

    def get_all_users(self):
        select_all_query = '''
            SELECT id, name, realname, balance
            FROM users ORDER BY balance DESC
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall()  # liste de tuples

    def get_balance_by_id(self, id_user):
        select_query = '''
            SELECT balance
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            result = cursor.fetchone()
            if result:
                return float(result[0])  # Renvoie la balance comme float
            else:
                return None  # Ou tout autre indication de l'absence de résultat

    def get_SOM_date_balance(self, date1, date2):
        select_query = '''
                SELECT SUM(new_balance) AS total_balance
                FROM (
                    SELECT id_user, MAX(date) AS max_date
                    FROM transactions
                    WHERE date BETWEEN ? AND ?
                    GROUP BY id_user
                ) AS latest_balances
                LEFT JOIN transactions ON transactions.id_user = latest_balances.id_user AND transactions.date = latest_balances.max_date
                UNION
                SELECT SUM(balance) AS total_balance
                FROM users
                WHERE id NOT IN (
                    SELECT id_user
                    FROM transactions
                    WHERE about = 'balance'
                    GROUP BY id_user
                );
            '''
        with self.connection:
            cursor = self.connection.execute(select_query, (date1, date2))
            cursor = cursor.fetchone()
            if cursor:
                return cursor[0]
            else:
                return 0

    # Items Table
    def insert_item(self, name_item, quantity_item, price_item):
        insert_query = '''
            INSERT INTO items (name,quantity,price) VALUES (?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (name_item, quantity_item, price_item))

    def update_quantity_by_name(self, new_quantity, name_item):
        update_query = '''
            UPDATE items
            SET quantity = ?
            WHERE name = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (new_quantity, name_item))

    def update_price_by_name(self, new_price, name_item):
        update_query = '''
            UPDATE items
            SET price = ?
            WHERE name = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (new_price, name_item))

    def update_realname_by_id(self, realname, id_user):
        update_query = '''
            UPDATE users
            SET realname = ?
            WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (realname, id_user))

    def update_name_by_id(self, name, id_user):
        update_query = '''
            UPDATE users
            SET name = ?
            WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (name, id_user))

    def get_item_by_name(self, name_item):
        select_query = '''
            SELECT name, quantity, price
            FROM items
            WHERE name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_item,))
            return cursor.fetchone()  # tuple

    def get_item_price(self, name_item):
        select_query = '''
            SELECT price
            FROM items
            WHERE name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_item,))
            result = cursor.fetchone()
            if result:
                return float(result[0])
            else:
                return None  # Ou tout autre indication de l'absence de résultat

    def get_item_quantity(self, name_item):
        select_query = '''
            SELECT quantity
            FROM items
            WHERE name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_item,))
            result = cursor.fetchone()
            if result:
                return int(result[0])
            else:
                return None  # Ou tout autre indication de l'absence de résultat

    def get_all_items(self):
        select_all_query = '''
            SELECT name, quantity, price
            FROM items ORDER BY name
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall()  # retourne liste de tuples

    def user_exist_by_id(self, id):
        select_query = "SELECT EXISTS (SELECT 1 FROM users WHERE id=?)"
        with self.connection:
            cursor = self.connection.execute(select_query, (id,))
            result = cursor.fetchone()
            return result[0] == 1  # 1 if exists, 0 if not exists

    def item_exist_by_name(self, name):
        select_query = "SELECT EXISTS (SELECT 1 FROM items WHERE name=?)"
        with self.connection:
            cursor = self.connection.execute(select_query, (name,))
            result = cursor.fetchone()
            return result[0] == 1  # 1 if exists, 0 if not exists

    def delete_user_by_id(self, id_user):
        delete_query = '''
        DELETE FROM users WHERE id=?
        '''
        with self.connection:
            cursor = self.connection.execute(delete_query, (id_user,))
            # return cursor.rowcount #nb de lignes affectées par la suppression

    def delete_item_by_name(self, item_name):
        delete_query = '''
        DELETE FROM items WHERE name=?
        '''
        with self.connection:
            cursor = self.connection.execute(delete_query, (item_name,))
            # return cursor.rowcount #nb de lignes affectées par la suppression

    def get_users_with_positive_balance(self):
        select_query = '''
            SELECT *
            FROM users
            WHERE balance > 0
            ORDER BY balance DESC;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            return cursor.fetchall()

    def get_items_with_positive_quantity(self):
        select_query = '''
            SELECT name, quantity
            FROM items
            WHERE quantity > 0
            ORDER BY quantity DESC;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            return cursor.fetchall()

    def get_top_payees(self):
        select_query = '''
            SELECT users.name, -SUM(payment_assumed) AS total_payment
            FROM transactions 
            JOIN users ON transactions.id_user = users.id
            WHERE about = 'buy' OR about = 'balance'
            GROUP BY id_user
            ORDER BY total_payment DESC
            LIMIT 10;
        '''
        with self.connection:
            cursor = self.connection.execute(select_query)
            return cursor.fetchall()

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

# Get item by name
item = database.get_item_by_name('Apple')
print(item)

# Get all users
all_users = database.get_all_users()
print(all_users)

# Get all items
all_items = database.get_all_items()
print(all_items)

# Don't forget to close the connection when you're done
database.close_connection()
"""

