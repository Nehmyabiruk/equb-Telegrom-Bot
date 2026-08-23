import re


# =========================================================
# FULL NAME VALIDATION
# =========================================================

def validate_full_name(name: str) -> bool:

    name = name.strip()

    # Must contain at least two words
    parts = name.split()

    if len(parts) < 2:
        return False

    # Minimum and maximum length
    if len(name) < 5 or len(name) > 100:
        return False

    # Allow:
    # English letters
    # Amharic characters
    # Spaces
    # Hyphen
    # Apostrophe

    pattern = r"^[A-Za-z\u1200-\u137F\s'-]+$"

    if not re.fullmatch(pattern, name):
        return False

    return True


# =========================================================
# ETHIOPIAN PHONE VALIDATION
# =========================================================

def validate_phone(phone: str) -> bool:

    phone = phone.strip()

    # Remove spaces and hyphens
    normalized = phone.replace(" ", "").replace("-", "")

    # Local format:
    #
    # 09XXXXXXXX
    # 07XXXXXXXX
    #
    # International:
    #
    # +2519XXXXXXXX
    # +2517XXXXXXXX

    local_pattern = r"^(09|07)[0-9]{8}$"

    international_pattern = r"^\+251(9|7)[0-9]{8}$"

    if re.fullmatch(local_pattern, normalized):
        return True

    if re.fullmatch(
        international_pattern,
        normalized
    ):
        return True

    return False


# =========================================================
# CBE TRANSACTION REFERENCE
# =========================================================
#
# Format:
#
# FT + 2 digit year
#    + 3 digit Julian day
#    + 5 alphanumeric characters
#
# Example:
#
# FT26123ABCDE
#
# Pattern:
#
# ^FT[0-9]{2}[0-9]{3}[A-Z0-9]{5}$
#
# =========================================================

def validate_cbe_reference(
    reference: str
) -> bool:

    reference = reference.strip().upper()

    pattern = r"^FT[0-9]{2}[0-9]{3}[A-Z0-9]{5}$"

    return bool(
        re.fullmatch(
            pattern,
            reference
        )
    )


# =========================================================
# TELEBIRR TRANSACTION NUMBER
# =========================================================
#
# 10 to 12 uppercase alphanumeric characters
#
# Example:
#
# AB123456789
#
# =========================================================

def validate_telebirr_reference(
    reference: str
) -> bool:

    reference = reference.strip().upper()

    pattern = r"^[A-Z0-9]{10,12}$"

    return bool(
        re.fullmatch(
            pattern,
            reference
        )
    )