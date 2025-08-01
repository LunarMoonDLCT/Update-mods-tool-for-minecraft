def sanitize_filename(name):
    import re
    return re.sub(r"[^\w\d\-_.]", "", name)

