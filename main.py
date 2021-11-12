import sqlite3
from datetime import date, datetime
from typing import Iterable

#Run to create db
#CREATE TABLE ProductType(ProductTypeID integer NOT NULL PRIMARY KEY, Description text NOT NULL)
#CREATE TABLE Product(ProductID integer NOT NULL PRIMARY KEY, Name text NOT NULL, Price real NOT NULL, ProductTypeID integer, FOREIGN KEY(ProductTypeID) REFERENCES ProductType(ProductTypeID))
#CREATE TABLE OrderItem(OrderItemID integer NOT NULL PRIMARY KEY, OrderID integer NOT NULL, ProductID integer NOT NULL, Quantity integer NOT NULL, FOREIGN KEY(OrderID) REFERENCES CustomerOrder(OrderID), FOREIGN KEY(ProductID) REFERENCES Product(ProductID))
#CREATE TABLE CustomerOrder(OrderID integer NOT NULL PRIMARY KEY, Date text NOT NULL, Time text NOT NULL, CustomerID integer NOT NULL, FOREIGN KEY(CustomerID) REFERENCES Customer(CustomerID))
#CREATE TABLE Customer(CustomerID integer NOT NULL PRIMARY KEY, FirstName text NOT NULL, LastName text NOT NULL, Street text NOT NULL, Town text NOT NULL, PostCode text NOT NULL, TelephoneNumber integer NOT NULL, Email text NOT NULL)

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
        if cond is None or cond == {}:
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
            return out
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

    def returnCustomer(self, col="*", **cols) -> list:
        if len(cols) == 0:
            return False
        cols = {k: v for k, v in cols.items() if v}
        return self.db.selectFrom("Customer", cols, col=col)

    def amendCustomer(self, match: dict, **change) -> bool:
        if len(match) == 0:
            return False
        return self.db.changeRecord("Customer", match, change)


class productController():
    def __init__(self, db: dbi) -> None:
        self.db = db

    def addProduct(self, name: str, price: float, ptypeid: int) -> bool:
        return self.db.insertInto("Product", (None, name, price, ptypeid))

    def deleteProduct(self, **cols) -> bool:
        if len(cols) == 0:
            return False
        return self.db.removeFrom("Product", cols)

    def returnProduct(self, **cols) -> list:
        return self.db.selectFrom("Product", cols)

    def amendProduct(self, match: dict, **change) -> bool:
        if len(match) == 0:
            return False
        return self.db.changeRecord("Product", match, change)

    def addProductType(self, description: str) -> bool:
        return self.db.insertInto("ProductType", (None, description))

    def deleteProductType(self, **cols) -> bool:
        if len(cols) == 0:
            return False
        return self.db.removeFrom("ProductType", cols)

    def returnProductType(self, **cols) -> list:
        return self.db.selectFrom("ProductType", cols)

    def amendProductType(self, match: dict, **change) -> bool:
        if len(match) == 0:
            return False
        return self.db.changeRecord("ProductType", match, change)


class orderController():
    def __init__(self, db: dbi) -> None:
        self.db = db
        #self.newOrder = self.addOrder

    def newOrder(self, date: str, time: str, customerId: int, products: list) -> bool:
        orderId = self.newCustomerOrder(date, time, customerId).lastrowid
        for product in products:
            quantity = product.pop("quantity")
            # print(product)
            productId = pc.returnProduct(**product)[0][0]
            self.newOrderItem(orderId, productId, quantity)

    def newCustomerOrder(self, date: str, time: str, customerId: int) -> sqlite3.Cursor:
        return self.db.insertInto("CustomerOrder", (None, date, time, customerId))

    def newOrderItem(self, orderId: int, productId: int, quantity: int) -> bool:
        return self.db.insertInto("OrderItem", (None, orderId, productId, quantity))

    def deleteOrder(self, **cols) -> bool:
        if len(cols) == 0:
            return False
        return self.db.removeFrom("OrderItem", cols)

    def returnOrder(self, **cols) -> list:
        if len(cols) == 0:
            return False
        return self.db.selectFrom("Orderitem", cols)

    def amendOrder(self, match: dict, **change) -> bool:
        if len(match) == 0:
            return False
        return self.db.changeRecord("OrderItem", match, change)

    def returnAllOrders(self) -> list:
        return db.query("SELECT Customer.firstname, CustomerOrder.time, Product.Name, OrderItem.quantity FROM Customer INNER JOIN CustomerOrder ON Customer.CustomerID=CustomerOrder.CustomerID INNER JOIN OrderItem ON CustomerOrder.OrderID=OrderItem.OrderID INNER JOIN Product ON Product.ProductID=OrderItem.ProductID").fetchall()

def newOrder():
    fname = input("Customer first name: ")
    lname = input("Customer last name: ")
    cid = input("Customer ID: ")
    customer = cc.returnCustomer(firstname=fname, lastname=lname, customerid=cid, col="Customer.CustomerID, Customer.FirstName, Customer.LastName")
    if len(customer) != 1:
        print(f"{customer}")
        print("Found multiple customers. Refine search")
        newOrder()
    cid = customer[0][0]
    now = datetime.now()
    dt = now.strftime("%Y/%m/%d")
    tm = now.strftime("%H:%M:%S")
    products = []
    while True:
        pname = input("Product name: ")
        if len(products) > 0 and len(pname) == 0:
            break
        quan = input("Product Quantity: ")
        if len(pname) != 0 and len(quan) != 0 and int(quan) != 0 and any(pname in p for p in pc.returnProduct()):
            products.append({"Name": pname, "quantity": quan})
    #print(dt, tm, cid, products)
    oc.newOrder(dt, tm, cid, products)

def newProduct():
    ptypes = pc.returnProductType()
    for i in ptypes:
        print(f"{i[0]} - {i[1]}")
    ptype = int(input("Product Type ID: "))
    while not any(ptype in pt for pt in ptypes):
        ptype = int(input("Product Type ID: "))
    pname = input("Product Name: ")
    while len(pname) == 0:
        pname = input("Product Name: ")
    price = input("Price: ")
    while len(price) == 0:
        price = input("Price: ")
    pc.addProduct(pname, price, ptype)


db = dbi("dbs2.sqlite3")
cc = customerController(db)
pc = productController(db)
oc = orderController(db)
