from services.common import RedisCrud


class KeyWordCrud(RedisCrud):
    def create_keyword(self, keys: list):
        return self.add("keywords", keys)

    def get_all_keywords(self):
        return self.get(["keywords"])

    def delete_keywords(self, keys: list):
        return self.delete("keywords", keys)

    def append_related_user_tech(self, keyword: str, value: list):
        return self.add(keyword, value)

    def union_related_user_tech(self, keywords: list):
        return self.all(keywords)

    def get_related_user_tech(self, tech: str):
        return self.get([tech])

    def delete_related_user_tech(self, keyword: str, value: list):
        return self.delete(keyword, value)
