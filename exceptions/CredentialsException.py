from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail=""):
        # Call the base class constructor with the parameters it needs
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED)
        self.detail = "Could not validate credentials => " + detail
        self.errors = status.HTTP_401_UNAUTHORIZED
        self.headers = {"WWW-Authenticate": "Bearer"}
