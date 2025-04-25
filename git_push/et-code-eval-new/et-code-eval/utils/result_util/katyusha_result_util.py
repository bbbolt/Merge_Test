class KatyushaResultUtil:
    def __init__(self, result):
        self.result = result

    def get_is_success(self):
        return self.result.get('isSuccess')

    def get_status(self):
        return self.result.get('status')

    def get_value(self):
        return self.result.get('value')
