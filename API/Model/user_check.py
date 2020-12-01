from imghdr import what
from pydantic import EmailStr
from fastapi  import UploadFile
from API.Model.exceptions import update_icon_size_exception, update_icon_format_exception

def email_size_validate(email: EmailStr):
    if len(email) > 100:
        raise ValueError("email length is greater than 100")
    if len(email) < 10:
        raise ValueError("email length is less than 10")
    return email

def username_char_set_validate(username: str):
    if not username.isalnum():
        raise ValueError("username must be a nonempty alphanumeric string")
    return username


def no_space_in_string_validate(stringVal: str):
    if any(map(lambda c: c.isspace(), stringVal)):
        raise ValueError("spaces not allowed in password")
    return stringVal

def icon_validate(new_icon: UploadFile):
    # ~ 2 MB is maximum size 
    max_size_icon = 2097152
    check_real_size = 0
    chunk_size = 1024
    chunk = new_icon.file.read(chunk_size)
    raw_icon = "".encode()
    while chunk:
        check_real_size += len(chunk)
        raw_icon += chunk
        if check_real_size > max_size_icon:
            raise update_icon_size_exception
        chunk = new_icon.file.read(chunk_size)
        
    if new_icon.content_type not in [
            "image/jpeg", "image/png", "image/bmp", "image/webp"]:
        raise update_icon_format_exception
    
    #raw_icon = new_icon.file.read()
    if what(new_icon.filename, h=raw_icon) not in [
            "jpeg", "png", "bmp", "webp"]:
        raise update_icon_format_exception

    return raw_icon