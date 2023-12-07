import sqlite3

conn = sqlite3.connect('allergen_scan.sqlite')

c = conn.cursor()

# Create the 'allergen_alert' table
c.execute('''
    CREATE TABLE allergen_alert
    (id INTEGER PRIMARY KEY ASC,
     user_id INTEGER NOT NULL,
     user_name VARCHAR(250) NOT NULL,
     barcode INTEGER NOT NULL,
     product_name VARCHAR(250) NOT NULL,
     allergen VARCHAR(250) NOT NULL,
     symptom VARCHAR(250) NOT NULL,
     date_created VARCHAR(100) NOT NULL,
     trace_id VARCHAR(36)) 
''')

# Create the 'ingredient_suggestion' table
c.execute('''
    CREATE TABLE ingredient_suggestion
    (id INTEGER PRIMARY KEY ASC,
     user_id INTEGER NOT NULL,
     user_name VARCHAR(250) NOT NULL,
     barcode INTEGER NOT NULL,
     product_name VARCHAR(250) NOT NULL,
     suggested_ingredient VARCHAR(250) NOT NULL,
     suggestion_details VARCHAR(250) NOT NULL,
     date_created VARCHAR(100) NOT NULL,
     trace_id VARCHAR(36)) 
''')

conn.commit()
conn.close()
