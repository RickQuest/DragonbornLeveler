# core/exceptions.py

class ApplicationError(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message="An application error occurred"):
        super().__init__(message)

class LogicError(ApplicationError):
    """Base exception for all errors related to DragonbornLeveler."""
    def __init__(self, message="A logic error occurred"):
        super().__init__(message)

class FavoriteNotFoundException(LogicError):
    """Exception raised when a favorite is not found in the favorites menu."""
    def __init__(self, favorite_name=None):
        message = f"Favorite '{favorite_name}' not found in the favorites menu." if favorite_name else "Favorite not found in the favorites menu."
        super().__init__(message)

class FavoriteEquipStateNotFoundException(LogicError):
    """Exception raised when a favorite equip state (l, r, lr) is not found in the favorites menu."""
    def __init__(self, message = "Favorite equip state (l, r, lr) not found."):
        super().__init__(message)

class FavoriteTextNotFoundException(LogicError):
    """Exception raised when favorite text is not found indicating a problem with the OCR or the screenshot region."""
    def __init__(self, message="Favorite text not found. There may be an issue with OCR or screenshot region."):
        super().__init__(message)
