from dns.resolver import dns

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from base64 import b64decode, b64encode


def verify_sig(public_key, signature, data):
    """ Verifies a signature """
    try:
        pk = serialization.load_pem_public_key(
            public_key,
            backend=default_backend()
        )

        pk.verify(b64decode(signature),
                  data,
                  padding.PKCS1v15(),
                  hashes.SHA256()
        )

        return True
    except:
        return False


def generate_sig(private_key, data):
    """ Generates a signature on the passed in data """
    pk = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
        )

    sig = pk.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return b64encode(sig)


def get_publickey(domain):
    """ Gets a publickey from a zone """
    try:
        segments = {}

        pembits = ''

        records = dns.resolver.query(domain, 'TXT') # Get all text records
        record_strings = []
        for text in records:
            record_strings.append(str(text))
            split_text = text.strings[0].split(',') # Separate the components
            index = -1
            indexData = None
            for kv in split_text:
                if kv.startswith('p='):
                    index = int(kv[2:])
                elif kv.startswith('d='):
                    indexData = kv[2:]
                elif kv.startswith('a=') and kv != 'a=RS256':
                    return None
                elif kv.startswith('t=') and kv != 't=x509':
                    return None

            if index != -1 and indexData != None:
                segments[index] = indexData

        # Concatenate all of the key segments
        for key in sorted(segments.iterkeys()):
            pembits = pembits + segments[key].strip('\n').strip('\\n').strip()

        return '-----BEGIN PUBLIC KEY-----\n' + pembits + '\n-----END PUBLIC KEY-----\n'

    except:
        return None
