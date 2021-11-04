import sqlite3
from typing import Iterable


class dbi():
    def __init__(self, dbpath: str) -> None:
        self.dbcon = sqlite3.connect(dbpath)
        self.cursor = self.dbcon.cursor()

    def commit(self) -> bool:
        self.dbcon.commit()
        return True

    def query(self, query: str, params=None) -> sqlite3.Cursor:
        if params is None:
            return self.cursor.execute(query)
        return self.cursor.execute(query, params)

    def selectFrom(self, table: str, cond: dict = None, col="*") -> list:
        if cond is None:
            return self.query(f"SELECT {col} FROM {table}").fetchall()
        match = " AND ".join(
            list(map(lambda a, b: f"{a} = {b.__repr__()}", cond.keys(), cond.values())))
        return self.query(f"SELECT {col} FROM {table} WHERE {match}").fetchall()

    def insertInto(self, table: str, values: Iterable) -> bool:
        try:
            out = self.query(
                f"INSERT INTO {table} VALUES({('?,' * len(values))[:-1]})", values)
            self.commit()
            return out
        except Exception as e:
            print(e)
            return False

    def removeFrom(self, table: str, values: dict, check: bool = True) -> bool:
        try:
            match = " AND ".join(
                list(map(lambda a, b: f"{a} = {b.__repr__()}", values.keys(), values.values())))
            print(match)
            if check:
                count = self.query(
                    f"SELECT COUNT(*) FROM {table} WHERE {match}").fetchone()
                print(count)
                if count[0] > 1:
                    return False
            self.query(f"DELETE FROM {table} WHERE {match}")
            self.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def newTable(self, table: str, cols: list) -> bool:
        try:
            self.query(f"CREATE TABLE {table}({', '.join(cols)})")
            self.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def dropTable(self, table: str) -> bool:
        try:
            self.query(f"DROP TABLE {table}")
            self.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def changeRecord(self, table: str, match: dict, change: dict) -> bool:
        try:
            match = " AND ".join(
                list(map(lambda a, b: f"{a} = {b.__repr__()}", match.keys(), match.values())))
            change = " AND ".join(
                list(map(lambda a, b: f"{a} = {b.__repr__()}", change.keys(), change.values())))
            count = self.query(
                f"SELECT COUNT(*) FROM {table} WHERE {match}").fetchone()
            if count[0] > 1:
                return False
            out = self.query(f"UPDATE {table} SET {change} WHERE {match}")
            self.commit()
            return False
        except Exception as e:
            print(e)
            return False

    def clearTable(self, table: str) -> bool:
        try:
            self.query(f"DELETE FROM {table}")
            self.commit()
            return True
        except Exception as e:
            print(e)
            return False


class customerController():
    def __init__(self, db: dbi) -> None:
        self.db = db

    def addCustomer(self, fname: str, lname: str, street: str, town: str, pcode: str, teln: int, email: str) -> bool:
        return self.db.insertInto("Customer", (None, fname, lname, street, town, pcode, teln, email))

    def deleteCustomer(self, **cols) -> bool:
        if len(cols) == 0:
            return False
        return self.db.removeFrom("Customer", cols)

    def returnCustomer(self, **cols) -> bool:
        if len(cols) == 0:
            return False
        return self.db.selectFrom("Customer", cols)

    def amendCustomer(self, match: dict, **change) -> bool:
        if len(change) == 0:
            return False
        return self.db.changeRecord("Customer", match, change)


db = dbi("dbs2.sqlite3")
cc = customerController(db)
