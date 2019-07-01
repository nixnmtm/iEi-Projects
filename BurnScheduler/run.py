class Scheduli(object):
    def __init__(self, app, local=False):
        self.app = app
        self.app.add_url_rule('/mustangTools/discover', 'discover', self.discover, methods=['GET', 'POST'])
        self.app.add_url_rule('/mustangTools/mustangBurn', 'mustangBurn', self.mustangBurn, methods=['POST'])