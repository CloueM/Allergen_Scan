import sqlite3

conn = sqlite3.connect('allergen_scan.sqlite')

c = conn.cursor()

# Drop the first table
c.execute('DROP TABLE IF EXISTS allergen_alert;')

# Drop the second table
c.execute('DROP TABLE IF EXISTS ingredient_suggestion;')

conn.commit()
conn.close()
