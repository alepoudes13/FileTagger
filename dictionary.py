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
