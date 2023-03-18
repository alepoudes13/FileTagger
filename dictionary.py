from database import DBConnector

class Dict:
    def __init__(self, db: DBConnector) -> None:
        self.tags = {}
        tags = db.getAllTags()
        for string in tags:
            cur_tags = string[0].split('|')
            for tag in cur_tags:
                if not tag.lower() in self.tags:
                    self.tags[tag.lower()] = 0
                self.tags[tag.lower()] += 1
    
    def getHints(self, word: str):
        hints = []
        if len(word) < 2:
            return hints
        word = word.lower()
        for tag in self.tags.items():
            if word == tag[0][:len(word)]:
                hints.append(tag)
        hints.sort(key = lambda x: x[1], reverse=True)
        return hints
    
    def addTag(self, tag):
        if not tag.lower() in self.tags:
            self.tags[tag.lower()] = 0
        self.tags[tag.lower()] += 1

    def deleteTags(self, tags):
        for tag in tags.split('|'):
            self.tags[tag] -= 1
            if self.tags[tag] == 0:
                self.tags.pop(tag)

    def rename(self, tag: str, newTag: str):
        if not tag in self.tags:
            return
        if not newTag in self.tags:
            self.tags[newTag] = 0
        self.tags[newTag] += self.tags[tag]
        self.tags.pop(tag)
        
    def getStat(self):
        stat = []
        for tag in self.tags.items():
            stat.append(tag)
        stat.sort(key = lambda x: x[1], reverse=True)
        return stat