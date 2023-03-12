import sqlite3

class DBConnector:
    def __init__(self, db_path) -> None:
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()
        self.activeTable = None

    def __del__(self):
        self.c.close()
        self.conn.close()

    def createTable(self, dir_path):
        self.activeTable = f'[{dir_path}]'
        self.c.execute(f" CREATE TABLE IF NOT EXISTS {self.activeTable} (name text PRIMARY KEY, tags text); ")
        self.conn.commit()

    def getTags(self, name):
        tags = self.c.execute(f'SELECT tags FROM {self.activeTable} WHERE name = "{name}"').fetchone()
        if tags == None:
            return ''
        return tags[0].lower()

    def setTag(self, name, tag):
        if tag == '':
            return
        tags = self.c.execute(f'SELECT tags FROM {self.activeTable} WHERE name = "{name}"').fetchone()
        if tags == None:
            self.c.execute(f'INSERT INTO {self.activeTable}(name, tags) VALUES (?,?)', (name, tag))
        elif not tag in tags[0].split('|'):
            self.c.execute(f'UPDATE {self.activeTable} SET tags = (?) WHERE name = (?)', [tags[0] + '|' + tag, name])
        self.conn.commit()

    def deleteName(self, name):
        try:
            self.c.execute(f'DELETE FROM {self.activeTable} WHERE name = "{name}"')
            self.conn.commit()
        except:
            pass

    def getAllTags(self):
        tags = self.c.execute(f'SELECT tags FROM {self.activeTable}').fetchall()
        return tags