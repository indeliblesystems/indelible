name="indelible_log"

import indelible_log.crypto
import json
import requests
from base64 import standard_b64decode, standard_b64encode

def profileFromJson(profileJson):
    res = json.loads(profileJson)
    res["master_key"] = standard_b64decode(res["master_key_base64"])
    del res["master_key_base64"]
    validateProfile(res)
    return res

def validateProfile(profile):
    missing = set(profile.keys()) - set(["customer_id", "apikey", "master_key", "endpoint_url"])
    if len(missing) > 0:
        raise Exception("profile is missing %s" % missing)

def validate_mode(mode):
    if mode not in ["string", "json", "binary", "raw"]:
        raise Exception("mode must be string/json/binary/raw")

class ValueTransformer:

    def __init__(self, encode, decode):
        self.encode = encode
        self.decode = decode

def value_transformer(mode, key):
    if mode == "raw":
        if key != None:
            raise Exception("cannot encrypt/decrypt in 'raw' mode")
        return ValueTransformer(
            encode = lambda x: x,
            decode = lambda x: x)
    if key != None:
        encrypt = lambda m: indelible_log.crypto.encrypt(key, m)
        decrypt = lambda m: indelible_log.crypto.decrypt(key, m)
    else:
        encrypt = lambda m: m
        decrypt = lambda m: m
    if mode == "string":
        return ValueTransformer(
            encode = lambda x: standard_b64encode(encrypt(x.encode())).decode(),
            decode = lambda x: decrypt(standard_b64decode(x)).decode())
    elif mode == "binary":
        return ValueTransformer(
            encode = lambda x: standard_b64encode(encrypt(x)).decode(),
            decode = lambda x: decrypt(standard_b64decode(x)))
    elif mode == "json":
        return ValueTransformer(
            encode = lambda x: standard_b64encode(encrypt(json.dumps(x).encode())).decode(),
            decode = lambda x: json.loads(decrypt(standard_b64decode(x))))
    else:
        raise Exception("unimplemented value_transformer mode '%s'" % mode)

class Log:

    def __init__(
            self,
            name,
            profile,
            key_mode = "string",
            value_mode = "json",
            encrypt = True,
            name_mode = "string"):
        validate_mode(key_mode)
        validate_mode(value_mode)
        self.orig_name = name
        self.profile = profile
        self.key_mode = key_mode
        self.value_mode = value_mode
        self.encrypt = encrypt
        self.authinfo = {
            "customer_id": profile["customer_id"],
            "apikey": profile["apikey"]
        }
        self.encoded_name = encode_name(name, name_mode)
        if encrypt:
            self.encrypted_name = encrypt_name(self.encoded_name, profile)
            self.remote_name = standard_b64encode(self.encrypted_name).decode()
            key = indelible_log.crypto.derive_key(profile["master_key"], self.encoded_name)
        else:
            key = None
            if name_mode != "raw":
                self.remote_name = self.encoded_name.decode()
            else:
                self.remote_name = name
        self.key_transformer = value_transformer(key_mode, key)
        self.value_transformer = value_transformer(value_mode, key)

    def create(self, log_group = None):
        req = { "authinfo": self.authinfo }
        req["logName"] = self.remote_name
        if log_group != None:
            req["logGroup"] = log_group
        response = requests.post(self.profile["endpoint_url"] + "/v1/log/create", json = req)
        handleError(response)

    def __iter__(self):
        return self.version_diff(0, None).changes()

    def version_diff(self, from_version=0, to_version=None, wait_seconds=None):
        diff = self.diff_page(
            from_version,
            to_version,
            wait_seconds = wait_seconds
        )
        return VersionDiff(
            self,
            diff["fromVersion"],
            diff["toVersion"],
            diff["page"],
            diff["nextPageOptions"]
        )

    def version(self, version):
        return self.version_diff(0, version).changes()

    def diff_page(
            self,
            from_version,
            to_version = None,
            wait_seconds = None,
            order_results_by = None,
            limit = None,
            pagination_options = None
    ):
        req = { "authinfo": self.authinfo, "logName": self.remote_name }
        req["fromVersion"] = from_version
        if to_version != None:
            req["toVersion"] = to_version
        if wait_seconds != None:
            req["waitSeconds"] = wait_seconds
        if order_results_by != None:
            req["orderResultsBy"] = order_results_by
        if limit != None:
            req["limit"] = limit
        if pagination_options != None:
            req["paginationOptions"] = pagination_options
        response = requests.post(self.profile["endpoint_url"] + "/v1/log/diff", json = req)
        handleError(response)
        diff = response.json()
        for x in diff["page"]:
            x["entry"] = {
                "key": self.key_transformer.decode(x["entry"]["key"]),
                "value": self.value_transformer.decode(x["entry"]["value"])
            }
        return diff

    def update(
            self,
            commands,
            update_source = None
    ):
        req = { "authinfo": self.authinfo, "logName": self.remote_name }
        if update_source != None:
            req["updateSource"] = update_source
        try:
            iter = iter(commands)
        except:
            iter = list(commands)
        def gen():
            yield(str.encode(json.dumps(req)))
            for x in iter:
                transformed = x.__dict__.copy()
                if x.key != None:
                    transformed["key"] = self.key_transformer.encode(x.key)
                if x.value != None:
                    transformed["value"] = self.value_transformer.encode(x.value)
                yield(str.encode(json.dumps(transformed)))
        response = requests.post(self.profile["endpoint_url"] + "/v1/log/update", data = gen())
        handleError(response)

def encode_name(name, name_mode):
    if name_mode == "raw":
        return name#.encode()
    elif name_mode == "stringlist":
        nul = bytearray(1)
        nul[0] = 0
        version = bytearray(1)
        version[0] = 1
        encoded = version
        for x in name:
            encoded = encoded + x.encode() + nul
        return bytes(encoded)
    elif name_mode == "string":
        return name.encode()
    else:
        raise Exception("unimplemented name_mode '%s'" % name_mode)

def encrypt_name(encoded_name, profile):
    return indelible_log.crypto.encrypt(profile["master_key"], encoded_name)

def handleError(response):
    if response.status_code == 200:
        return
    try:
        toRaise = ApiErrorException(response.json())
    except:
        response.raise_for_status()
    raise(toRaise)

class ApiErrorException(BaseException):
    def __init__(self, response):
        self.__dict__ = response

class VersionDiff:
    def __init__(self, log, from_version, to_version, page, next_page_options):
        self.log = log
        self.from_version = from_version
        self.to_version = to_version
        self.page = page
        self.next_page_options = next_page_options

    def __str__(self):
        return str(self.to_version)

    def changes(self):
        while True:
            for x in self.page:
                yield(x)
            if self.next_page_options == None:
                return
            diff = self.log.diff_page(
                self.from_version,
                self.to_version,
                pagination_options = self.next_page_options
            )
            self.next_page_options = diff["nextPageOptions"]
            self.page = diff["page"]

class Cmd:
    class ExpectVersion:
        def __init__(self, version):
            self.type = "ExpectVersion"
            self.version = version
            self.key = self.value = None
    class Insert:
        def __init__(self, key, value):
            self.type = "Insert"
            self.key = key
            self.value = value
            self.version = None
    class Update:
        def __init__(self, key, value):
            self.type = "Update"
            self.key = key
            self.value = value
            self.version = None
    class Upsert:
        def __init__(self, key, value):
            self.type = "Upsert"
            self.key = key
            self.value = value
            self.version = None
    class Remove:
        def __init__(self, key, value):
            self.type = "Remove"
            self.key = key
            self.value = value
            self.version = None
