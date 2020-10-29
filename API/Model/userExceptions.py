from fastapi import HTTPException, status

not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

register_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Could not register the user"
)

update_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to update"
)

update_icon_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to update icon. Formats allowed: jpeg, png, bmp, webp"
)

unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
)

not_authenticated_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authenticated"
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

profile_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Login to see private profile"
)
