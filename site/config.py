class Config:

    def __init__(self, bucket='digisafe-nagger', owner=None):
        self.bucket = bucket
        self.site_owner = owner

    def get_bucket(self):
        return self.bucket

    def get_owner(self):
        return self.site_owner
