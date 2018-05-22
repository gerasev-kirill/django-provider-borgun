import six


def to_bytes(data):
    if six.PY2:
        return data.encode('utf-8')
    return bytes(data, encoding='utf-8')
