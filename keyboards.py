from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# =========================================================
# LANGUAGE KEYBOARD
# =========================================================

def language_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇪🇹 አማርኛ",
                    callback_data="lang_am"
                ),
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="lang_en"
                ),
            ]
        ]
    )


# =========================================================
# PAYMENT FOR — AMHARIC
# =========================================================

def payment_for_keyboard_am():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 ለራሴ እከፍላለሁ",
                    callback_data="pay_self"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 ለሌላ ሰው እከፍላለሁ",
                    callback_data="pay_other"
                )
            ]
        ]
    )


# =========================================================
# PAYMENT FOR — ENGLISH
# =========================================================

def payment_for_keyboard_en():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Pay for myself",
                    callback_data="pay_self"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Pay for another person",
                    callback_data="pay_other"
                )
            ]
        ]
    )


# =========================================================
# PAYMENT METHOD — AMHARIC
# =========================================================

def payment_method_keyboard_am():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏦 CBE",
                    callback_data="payment_cbe"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 Telebirr",
                    callback_data="payment_telebirr"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏦 ሌላ ባንክ → CBE",
                    callback_data="payment_other_bank"
                )
            ]
        ]
    )


# =========================================================
# PAYMENT METHOD — ENGLISH
# =========================================================

def payment_method_keyboard_en():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏦 CBE",
                    callback_data="payment_cbe"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 Telebirr",
                    callback_data="payment_telebirr"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏦 Other Bank → CBE",
                    callback_data="payment_other_bank"
                )
            ]
        ]
    )


# =========================================================
# ADMIN PAYMENT ACTIONS
# =========================================================

def admin_payment_keyboard(payment_id: int):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ APPROVE",
                    callback_data=f"approve_{payment_id}"
                ),
                InlineKeyboardButton(
                    text="❌ REJECT",
                    callback_data=f"reject_{payment_id}"
                )
            ]
        ]
    )