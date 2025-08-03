import sqlite3
from typing import List

DB_PATH = 'db.sqlite3'  # adjust if your file lives elsewhere


def get_usernames_by_group(group_id: int) -> List[str]:
    
    query = """
        SELECT username
        FROM users_user
        WHERE group_id = ?;
    """

   

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = lambda cur, row: row[0]  # return strings, not tuples
        return conn.execute(query, (group_id,)).fetchall()


# Example usage
if __name__ == "__main__":
    g_id = 3
    print(get_usernames_by_group(g_id))  # ['alice', 'bob', ...]