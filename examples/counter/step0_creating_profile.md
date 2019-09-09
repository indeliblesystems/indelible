Create `indelibleprofile.json` with your Indelible Developer Preview credentials.  For example:

```json
{
    "endpoint_url": "https://log.ndlbl.net:8443",
    "customer_id": "customer-id",
    "apikey": "api-key",
    "master_key_base64": "v7RBLmFz5oB+IWOtGBEyfgejHvyYZwMTu+x0bbzZ+/4="
}
```

You can generate a new random key by:

```
python -c 'import base64, os; print(base64.standard_b64encode(os.urandom(32)).decode())'
9wY+Oi33I870wopguIhuW4Ewo9HTVi8XGq+69JkA1ok=
```


