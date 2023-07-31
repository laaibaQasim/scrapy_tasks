class Article:
    def __init__(self, text):
        self.text = text

    def write(self, new_text):
        self.text = new_text

    def create_momento(self):
        return ArticleMomento(self.text)

    def restore(self, momento):
        self.text = momento.curr_text


class ArticleMomento:
    def __init__(self, text):
        self.curr_text = text

    def get_article(self):
        return self.curr_text


class ArticleHistory:
    def __init__(self):
        self.momentos = []

    def save(self, momento):
        self.momentos.append(momento)

    def undo(self):
        if len(self.momentos) > 0:
            self.momentos.pop()

    def get_history(self):
        return self.momentos


if __name__ == '__main__':
    history = ArticleHistory()

    article = Article("state 1")
    history.save(article.create_momento())

    article.write("state 2")
    history.save(article.create_momento())

    article.write("state 3")
    history.save(article.create_momento())

    history.undo()
    history.undo()

    article.write("state 4")
    history.save(article.create_momento())

    momentos = history.get_history()
    for i in range(len(momentos)):
        print("version: ", i+1, ": ", momentos[i].get_article())
