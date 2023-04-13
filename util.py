import re

_pattern = re.compile('^.*\\.([^\\.]+)$', re.IGNORECASE)
_endings = {
    'jpg',
    'jpeg',
    #'mp4',
    #'aae',
    #'mov',
    'png',
    'gif',
    'avi',
    'wav',
    'cr2'
}

def isImageFile(name: str):
    match = _pattern.match(name)
    if match:
        end = match.group(1).lower()
        return end in _endings
    else:
        return False
