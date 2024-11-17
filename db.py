import sqlite3

def create_db():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    
    # Create the stocks table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        ticker TEXT PRIMARY KEY
    )''')
    
    conn.commit()
    conn.close()

def add_stock(ticker):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    
    # Insert stock info
    cursor.execute('''
    INSERT OR REPLACE INTO stocks (ticker)
    VALUES (?)''', (ticker,))
    
    conn.commit()
    conn.close()

def remove_stock(ticker):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    
    # Remove stock info
    cursor.execute('DELETE FROM stocks WHERE ticker = ?', (ticker,))
    
    conn.commit()
    conn.close()

def get_all_stocks():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT ticker FROM stocks')
    stocks = cursor.fetchall()
    
    conn.close()
    return stocks
