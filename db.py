from typing import Dict, Tuple, List
import sqlite3

connection = sqlite3.connect("tasks.db")
cursor = connection.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ', '.join('?' * len(column_values.keys()))
    cursor.executemany(
        f"insert into {table}"
        f"({columns})"
        f"values ({placeholders})",
        values)
    connection.commit()


def fetchall(table: str, columns: List[str]) -> List[Dict]:
    columns_joined = ', '.join(columns)
    cursor.execute(f"select {columns_joined} from {table}")
    rows = cursor.fetchall()
    rezult = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        rezult.append(dict_row)
    return rezult


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    connection.commit()


def get_cursor():
    return cursor


def _init_db():
    with open("createdb.sql", "r") as f:
        sql = f.read()
        cursor.executescript(sql)
        connection.commit()


def check_db_exists():
    cursor.execute("select name from sqlite_master "
                   "where type='table' and name='task'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
