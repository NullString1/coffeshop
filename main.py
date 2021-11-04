import sqlite3

class db():
    def __init__(self, dbpath: str) -> None:
        self.dbcon = sqlite3.connect(dbpath)
        self.cursor = self.dbcon.cursor()
    
    def query(self, query: str) -> bool:
        self.cursor.execute(query)

    def selectFrom(self, table, col = "*", cond = None):
        if cond is not None:
            self.cursor.execute("SELECT ? FROM ?", (col, table))
        self.cursor.execute("SELECT ? FROM ? WHERE ?", (col, table, cond))
        