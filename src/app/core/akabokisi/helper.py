from datetime import datetime

def current_year() -> int:
    """
    Returns the current year
    """
    year = datetime.now().year
    return year
