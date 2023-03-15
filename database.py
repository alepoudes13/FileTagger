import sqlite3

class DBConnector:
    def __init__(self, db_path) -> None:
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()
        self.activeTable = None

    def close(self):
        self.c.close()
        self.conn.close()

    def __del__(self):
        self.deleteEmptyTable()
        self.c.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()
    
    def deleteEmptyTable(self):
        if self.activeTable == None:
            return
        row = self.c.execute(f'SELECT * FROM {self.activeTable}').fetchone()
        if row == None:
            self.c.execute(f'DROP TABLE {self.activeTable}')
        self.conn.commit()

    def createTable(self, dir_path):
        self.deleteEmptyTable()
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

    def deleteName(self, name):
        try:
            self.c.execute(f'DELETE FROM {self.activeTable} WHERE name = "{name}"')
        except:
            pass

    def getAllTags(self):
        tags = self.c.execute(f'SELECT tags FROM {self.activeTable}').fetchall()
        return tags
    
    def rename(self, tag: str, newTag: str):
        if tag == '':
            return
        tags = self.c.execute(f'SELECT * FROM {self.activeTable}').fetchall()
        for item in tags:
            if tag in item[1].split('|'):
                string = '|' + item[1] + '|'
                new_tags = string.replace('|' + tag + '|', '|' + newTag + '|')
                self.c.execute(f'UPDATE {self.activeTable} SET tags = (?) WHERE name = (?)', [new_tags[1:-1], item[0]])