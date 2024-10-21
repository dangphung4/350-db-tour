from dbtour import dbtour_app
import sqlite3

@dbtour_app.route("/")
def does_this_work():
    conn = sqlite3.connect("huge.db")
    cursor = conn.execute("select msg from message")
    msg = cursor.fetchall()
    return f"<HTML><BODY><H1>{msg[0][0]}</H1></BODY></HTML>"