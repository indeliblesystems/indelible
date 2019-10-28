name="indelible_log"

import indelible_log.crypto
import json
import requests
from base64 import standard_b64decode, standard_b64encode

def profileFromJson(profileJson):
    """Load a profile from a JSON string."""
    res = json.loads(profileJson)
    res["master_key"] = standard_b64decode(res["master_key_base64"])
    del res["master_key_base64"]
    validateProfile(res)
    return res

def validateProfile(profile):
    """Raise an exception if the profile is missing required values."""
    missing = set(profile.keys()) - set(["customer_id", "apikey", "master_key", "endpoint_url"])
    if len(missing) > 0:
        raise Exception("profile is missing %s" % missing)

def validate_mode(mode):
    """Raise an exception if the given key/value mode is neither string, json, binary, nor raw."""
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
            encode = lambda x: standard_b64encode(encrypt(json.dumps(x, separators=(",",":")).encode())).decode(),
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
        """Provide an object for working with an Indelible Log.
        name: A name to distinguish this log from others in the account.  If
            encrypt=True is also used, this name will be automatically
            encrypted in all network communication.
        profile: The credentials, endpoint and encryption key for connecting
            to Indelible.
        key_mode: Set whether to treat log entry keys as strings (default),
            json-serialized objects (json), byte strings (binary), or raw.
            In all but raw, the keys will be encoded then,
            if encrypt=True is used, be encrypted with the log key in all
            network communication.  raw mode can be used to turn off encoding
            and encryption, preserving the byte strings at Indelible.
        value_mode: Set whether to treat log entry values as json-serialized
            objects (default, json), strings (string), byte strings (binary),
            or raw.  In all but raw, the values will be encoded then, if
            encrypt=True is used, be encrypted with the log entry key in all
            network communication.  raw mode can be used to turn off encoding
            and encryption, preserving the byte strings at Indelible.
        encrypt: Whether to perform automatic encryption/decryption, using a
            unique key for every log and entry key, derived from the profile's
            master key.
        name_mode: 'string' indicates the log name is given as a string and
            should be encrypted if encrypt=True is also set.  raw mode turns
            off encoding and encryption, preserving the byte string at
            Indelible.
        """

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
        """Create the log, or just return if it already exists as requested.
        After the first time this is done, the log exists, empty, at version 0.

        log_group: Customer-defined plaintext identifier that helps to determine
            which encryption key is needed to use the log.
        """
        req = { "authinfo": self.authinfo }
        req["logName"] = self.remote_name
        if log_group != None:
            req["logGroup"] = log_group
        response = requests.post(self.profile["endpoint_url"] + "/v1/log/create", json = req)
        handleError(response)

    def __iter__(self):
        """Iterate over the changes in the version of the log that was
        the latest version at the time iteration was started."""
        return self.version_diff(0, None).changes()

    def version_diff(self, from_version=0, to_version=None, wait_seconds=None):
        """Return a VersionDiff for the requested versions.  If to_version=None,
        the diff to the latest version will be returned.  If wait_seconds is 0-60,
        and there is presently no diff to report, the server will wait for
        a new version to be created, then diff that as soon as possible."""
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
        """Return the changes for a specific log version."""
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
        """Return a single page (up to 50 changes) of log changes.
        from_version: The version to start at (0 is the beginning).
        to_version: The version to end at (if None, use the latest version).
        wait_seconds: How long to wait (up to 60) for a new version to
            be created, if the from_version is the latest version when the
            request is made.
        order_results_by: 'command' or 'key', see pagination_options.
        limit: 0 to 50, the number of changes to include on the page.
        pagination_options: A map telling where to start the page.  Normally from
            nextPageOptions in a previous response.
            When orderResultsBy='command' is used:
                'skipToVersion': The version to start at.
                'skipToCommand': The offset of the command within the version to
                    start at.
            When orderResultsBy='key' is used:
                'skipToKey': The key to start the page at, in lexicographic order.
                'removeAlreadySeen': 'true' or 'false', Whether to start the
                    page with the addition for the 'skipToKey', if it exists.
                    Used when Remove/Add changes for a key are on different
                    pages, or when the caller never cares about removals.

        Returns a map with:
        fromVersion: The version the diff starts at, matching the requested
            version.
        toVersion: The version the diff applies to.  If unspecified in the
            request, this is the current version of the log.
        page: The changes to apply to fromVersion to make it have the same
            contents as toVersion. A list of maps, each containing:
                change: 'Add' or 'Remove', reflecting whether this value value
                    was added or removed.
                entry: a map containing the entry's 'key' and 'value', which
                    may have been decoded/decrypted depending on key_mode,
                    value_mode, or encrypt Log options.
                version: The version that introduced this value.
        nextPageOptions: Pagination options for subsequent diff requests, to
            see the next page of diffs in the same version.
        """
        req = { "authinfo": self.authinfo, "logName": self.remote_name }
        if from_version != None:
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
            req["paginationOptions"] = pagination_options.copy()
            if pagination_options.get("skipToKey") is not None:
                skipToKey = req["paginationOptions"]["skipToKey"]
                req["paginationOptions"]["skipToKey"] = \
                    self.key_transformer.encode(skipToKey)
        response = requests.post(self.profile["endpoint_url"] + "/v1/log/diff", \
                                 json = req)
        handleError(response)
        diff = response.json()
        for x in diff["page"]:
            x["entry"] = {
                "key": self.key_transformer.decode(x["entry"]["key"]),
                "value": self.value_transformer.decode(x["entry"]["value"])
            }
        if diff.get("nextPageOptions") is not None:
            toDecode = diff["nextPageOptions"].get("skipToKey")
            if toDecode is not None:
                diff["nextPageOptions"]["skipToKey"] = \
                    self.key_transformer.decode(toDecode)
        return diff

    def update(
            self,
            commands,
            update_source = None
    ):
        """
        commands: iterable of Cmd objects representing transaction commands
            that have to all succeed for the log to be updated.  See Cmd.
        update_source: a string identifying the person/system making this update.
        """
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
        """Require the log to be at the given version."""
        def __init__(self, version):
            self.type = "ExpectVersion"
            self.version = version
            self.key = self.value = None
    class Insert:
        """Insert a new value for for key.  Fail with UNEXPECTED_VALUE if there
        was already a different value for the key.  For idempotency, this
        command has no effect if the log already contains the given value for
        key."""
        def __init__(self, key, value):
            self.type = "Insert"
            self.key = key
            self.value = value
            self.version = None
    class Update:
        """Replace value for key.  Fail with NONEXISTENT_VALUE if there is
        not an existing value for key.  For idempotency, this command has no
        effect if the log already contains the given value for key."""
        def __init__(self, key, value):
            self.type = "Update"
            self.key = key
            self.value = value
            self.version = None
    class Upsert:
        """Update/Insert - sets the value for key.  For idempotency, this
        command has no effect if the log already contains the given value
        for key."""
        def __init__(self, key, value):
            self.type = "Upsert"
            self.key = key
            self.value = value
            self.version = None
    class Remove:
        """Remove the value for key.  Has no effect if the key is already
        removed or has another value."""
        def __init__(self, key, value):
            self.type = "Remove"
            self.key = key
            self.value = value
            self.version = None
