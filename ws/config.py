import argparse

from google.api_core.exceptions import Conflict, NotFound, Forbidden
from google.cloud import storage

DIGI_CONFIG_MGR = None


class DigiConfig:

    def __init__(self, args):
        self.bucket = args.bucket
        self.site_owner = args.owner
        self.family_pic = args.picture
        self.site_name = args.site
        # check if bucket exists and if not create it.
        client = storage.Client()
        bucket = client.bucket(self.bucket)
        bucket.location = 'us'
        try:
            res = client.get_bucket(self.bucket)
        except NotFound as e:
            client.create_bucket(bucket)
            print("bucket %s created" % self.bucket)
        except Conflict:
            pass
        except Forbidden as e:
            print(
                "Bucket %s could not be created. This could be due to the fact that a bucket with this name exists in another account. Try changing the name of the bucket")
        except Exception as e:
            print("error in setting up dedicated bucket for site %s due to %s " % (self.site_name, e))

    def get_bucket(self):
        return self.bucket

    def get_owner(self):
        return self.site_owner

    def get_picture(self):
        return self.family_pic

    def get_site_name(self):
        return self.site_name


def get_config_mgr_with_args(args):
    global DIGI_CONFIG_MGR
    if not DIGI_CONFIG_MGR:
        DIGI_CONFIG_MGR = DigiConfig(args)
    return DIGI_CONFIG_MGR


def get_config_mgr():
    arg = argparse.ArgumentParser(description="Welcome to Digisafe - an information and data management hub for home.")
    arg.add_argument('--bucket', '-b', type=str, default='digisafe-nagger',
                     help="Name of the bucket to use for maintaining this ws's documents")
    arg.add_argument('--owner', '-o', type=str, help="Name of the owner of this ws")
    arg.add_argument('--site', '-s', type=str, default="Schoolhouse Road",
                     help="Name of the ws this infrastructure is limited to")
    arg.add_argument('--picture', '-p', type=str, default='family_office.jpg',
                     help="Path to the picture in case of custom branding")
    a = arg.parse_args()
    return get_config_mgr_with_args(a)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


if __name__ == "__main__":
    args = {
        "bucket": "new_bucket",
        "ws": "Schoolhouse Rd",
        "owner": None,
        "picture": "family_office.jpg"
    }
    ar = dotdict(args)
    d = DigiConfig(ar)
    print(d.get_bucket())
