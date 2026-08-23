# =========================================================
# ETHIO CAR EQUB BOT
# =========================================================

import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, ADMIN_ID

from database import get_db

from models import User, Payment

from states import RegistrationStates

from keyboards import (
    language_keyboard,
    payment_for_keyboard_am,
    payment_for_keyboard_en,
    payment_method_keyboard_am,
    payment_method_keyboard_en,
    admin_payment_keyboard,
)

from validation import (
    validate_full_name,
    validate_phone,
    validate_cbe_reference,
    validate_telebirr_reference,
)
from config import (
    BOT_TOKEN,
    ADMIN_ID,
    CBE_ACCOUNT_NAME,
    CBE_ACCOUNT_NUMBER,
    TELEBIRR_ACCOUNT_NAME,
    TELEBIRR_PHONE,
    EQUB_AMOUNT
)


# =========================================================
# BOT
# =========================================================

bot = Bot(
    token=BOT_TOKEN
)

dp = Dispatcher()


# =========================================================
# HELPER
# =========================================================

def get_language(data):
    return data.get("language", "am")


# =========================================================
# /START
# =========================================================

@dp.message(CommandStart())
async def start_command(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "🚗✨ <b>ETHIO CAR EQUB</b> ✨🚗\n\n"
        "ወደ ETHIO CAR EQUB እንኳን በደህና መጡ።\n\n"
        "የቋንቋ ምርጫዎን ይምረጡ።",
        parse_mode="HTML",
        reply_markup=language_keyboard()
    )

    await state.set_state(
        RegistrationStates.language
    )


# =========================================================
# LANGUAGE — AMHARIC
# =========================================================

@dp.callback_query(
    RegistrationStates.language,
    F.data == "lang_am"
)
async def select_amharic(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        language="am"
    )

    await callback.answer()

    await callback.message.edit_text(
        "🚗✨ <b>ETHIO CAR EQUB</b> ✨🚗\n\n"
        "ወደ ETHIO CAR EQUB እንኳን "
        "በደህና መጡ።\n\n"
        "ክፍያውን ለራስዎ ነው ወይስ "
        "ለሌላ ሰው የሚከፍሉት?",
        parse_mode="HTML",
        reply_markup=payment_for_keyboard_am()
    )

    await state.set_state(
        RegistrationStates.payment_for
    )


# =========================================================
# LANGUAGE — ENGLISH
# =========================================================

@dp.callback_query(
    RegistrationStates.language,
    F.data == "lang_en"
)
async def select_english(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        language="en"
    )

    await callback.answer()

    await callback.message.edit_text(
        "🚗✨ <b>ETHIO CAR EQUB</b> ✨🚗\n\n"
        "Welcome to ETHIO CAR EQUB.\n\n"
        "Are you making the payment for "
        "yourself or another person?",
        parse_mode="HTML",
        reply_markup=payment_for_keyboard_en()
    )

    await state.set_state(
        RegistrationStates.payment_for
    )


# =========================================================
# PAYMENT FOR — SELF
# =========================================================

@dp.callback_query(
    RegistrationStates.payment_for,
    F.data == "pay_self"
)
async def payment_for_self(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        payment_for="self"
    )

    data = await state.get_data()

    language = get_language(data)

    await callback.answer()

    if language == "am":

        await callback.message.edit_text(
            "👤 <b>ሙሉ ስምዎን ያስገቡ።</b>\n\n"
            "ለምሳሌ፦ አበበ ከበደ\n\n"
            "⚠️ እባክዎ እውነተኛ ሙሉ ስም "
            "ያስገቡ።",
            parse_mode="HTML"
        )

    else:

        await callback.message.edit_text(
            "👤 <b>Enter your full name.</b>\n\n"
            "Example: Abebe Kebede\n\n"
            "⚠️ Please enter your real full name.",
            parse_mode="HTML"
        )

    await state.set_state(
        RegistrationStates.full_name
    )


# =========================================================
# PAYMENT FOR — OTHER
# =========================================================

@dp.callback_query(
    RegistrationStates.payment_for,
    F.data == "pay_other"
)
async def payment_for_other(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        payment_for="other"
    )

    data = await state.get_data()

    language = get_language(data)

    await callback.answer()

    if language == "am":

        await callback.message.edit_text(
            "👤 <b>የሚመዘገበውን ሰው ሙሉ ስም "
            "ያስገቡ።</b>\n\n"
            "ለምሳሌ፦ አበበ ከበደ\n\n"
            "⚠️ እውነተኛ ሙሉ ስም ያስገቡ።",
            parse_mode="HTML"
        )

    else:

        await callback.message.edit_text(
            "👤 <b>Enter the full name of the "
            "person being registered.</b>\n\n"
            "Example: Abebe Kebede\n\n"
            "⚠️ Please enter the real full name.",
            parse_mode="HTML"
        )

    await state.set_state(
        RegistrationStates.full_name
    )


# =========================================================
# FULL NAME
# =========================================================

@dp.message(
    RegistrationStates.full_name,
    F.text
)
async def receive_full_name(
    message: Message,
    state: FSMContext
):

    full_name = message.text.strip()

    data = await state.get_data()

    language = get_language(data)

    if not validate_full_name(full_name):

        if language == "am":

            await message.answer(
                "❌ የገባው ስም ትክክል አይደለም።\n\n"
                "እባክዎ እውነተኛ ሙሉ ስምዎን "
                "ያስገቡ።\n\n"
                "ለምሳሌ፦ አበበ ከበደ"
            )

        else:

            await message.answer(
                "❌ Invalid name.\n\n"
                "Please enter your real full name."
            )

        return

    await state.update_data(
        full_name=full_name
    )

    if language == "am":

        await message.answer(
            "📱 <b>ስልክ ቁጥርዎን ያስገቡ።</b>\n\n"
            "ለምሳሌ፦\n"
            "0912345678\n"
            "+251912345678\n"
            "0712345678\n\n"
            "Ethio telecom ወይም Safaricom "
            "ስልክ ቁጥር መጠቀም ይችላሉ።",
            parse_mode="HTML"
        )

    else:

        await message.answer(
            "📱 <b>Enter your phone number.</b>\n\n"
            "Examples:\n"
            "0912345678\n"
            "+251912345678\n"
            "0712345678\n\n"
            "Ethio telecom or Safaricom numbers "
            "are accepted.",
            parse_mode="HTML"
        )

    await state.set_state(
        RegistrationStates.phone
    )


# =========================================================
# PHONE
# =========================================================

@dp.message(
    RegistrationStates.phone,
    F.text
)
async def receive_phone(
    message: Message,
    state: FSMContext
):

    phone = message.text.strip()

    data = await state.get_data()

    language = get_language(data)

    if not validate_phone(phone):

        if language == "am":

            await message.answer(
                "❌ የስልክ ቁጥሩ ትክክል አይደለም።\n\n"
                "እባክዎ ትክክለኛ የኢትዮጵያ "
                "ስልክ ቁጥር ያስገቡ።\n\n"
                "ለምሳሌ፦\n"
                "0912345678\n"
                "+251912345678\n"
                "0712345678"
            )

        else:

            await message.answer(
                "❌ Invalid Ethiopian phone number.\n\n"
                "Examples:\n"
                "0912345678\n"
                "+251912345678\n"
                "0712345678"
            )

        return

    await state.update_data(
        phone=phone
    )

    if language == "am":

        await message.answer(
            "💳 <b>የክፍያ ዘዴዎን ይምረጡ።</b>",
            parse_mode="HTML",
            reply_markup=payment_method_keyboard_am()
        )

    else:

        await message.answer(
            "💳 <b>Select your payment method.</b>",
            parse_mode="HTML",
            reply_markup=payment_method_keyboard_en()
        )

    await state.set_state(
        RegistrationStates.payment_method
    )


# =========================================================
# PAYMENT METHOD — CBE
# =========================================================

@dp.callback_query(
    RegistrationStates.payment_method,
    F.data == "payment_cbe"
)
async def select_cbe(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        payment_method="cbe"
    )

    await callback.answer()

    language = get_language(
        await state.get_data()
    )

    if language == "am":

        await callback.message.answer(
            "🏦 <b>CBE BANK</b>\n\n"

            "👤 <b>የሂሳብ ባለቤት</b>\n"
            f"{CBE_ACCOUNT_NAME}\n\n"

            "💳 <b>የሂሳብ ቁጥር</b>\n"
            f"<code>{CBE_ACCOUNT_NUMBER}</code>\n\n"

            "💰 <b>የሚከፈለው መጠን</b>\n"
            f"<b>{EQUB_AMOUNT} ETB</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "⚠️ እባክዎ ክፍያውን ወደላይ "
            "የተጠቀሰው የCBE ሂሳብ ይፈጽሙ።\n\n"

            "ከክፍያው በኋላ የክፍያ ደረሰኝዎን "
            "ይላኩ።",

            parse_mode="HTML"
        )

    else:

        await callback.message.answer(
            "🏦 <b>CBE BANK</b>\n\n"

            "👤 <b>Account Owner</b>\n"
            f"{CBE_ACCOUNT_NAME}\n\n"

            "💳 <b>Account Number</b>\n"
            f"<code>{CBE_ACCOUNT_NUMBER}</code>\n\n"

            "💰 <b>Payment Amount</b>\n"
            f"<b>{EQUB_AMOUNT} ETB</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "Please make the payment to the "
            "CBE account shown above.\n\n"

            "After completing the payment, "
            "send your payment receipt.",

            parse_mode="HTML"
        )

    await request_receipt(
        callback.message,
        "cbe"
    )

    await state.set_state(
        RegistrationStates.receipt
    )


# =========================================================
# PAYMENT METHOD — TELEBIRR
# =========================================================

@dp.callback_query(
    RegistrationStates.payment_method,
    F.data == "payment_telebirr"
)
async def select_telebirr(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        payment_method="telebirr"
    )

    await callback.answer()

    language = get_language(
        await state.get_data()
    )

    if language == "am":

        await callback.message.answer(
            "📱 <b>TELEBIRR</b>\n\n"

            "👤 <b>የሂሳብ ባለቤት</b>\n"
            f"{TELEBIRR_ACCOUNT_NAME}\n\n"

            "📱 <b>የTelebirr ቁጥር</b>\n"
            f"<code>{TELEBIRR_PHONE}</code>\n\n"

            "💰 <b>የሚከፈለው መጠን</b>\n"
            f"<b>{EQUB_AMOUNT} ETB</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "⚠️ እባክዎ ክፍያውን ወደላይ "
            "የተጠቀሰው የTelebirr ቁጥር ይፈጽሙ።\n\n"

            "ከክፍያው በኋላ የክፍያ ደረሰኝዎን "
            "ይላኩ።",

            parse_mode="HTML"
        )

    else:

        await callback.message.answer(
            "📱 <b>TELEBIRR</b>\n\n"

            "👤 <b>Account Owner</b>\n"
            f"{TELEBIRR_ACCOUNT_NAME}\n\n"

            "📱 <b>Telebirr Number</b>\n"
            f"<code>{TELEBIRR_PHONE}</code>\n\n"

            "💰 <b>Payment Amount</b>\n"
            f"<b>{EQUB_AMOUNT} ETB</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "Please make the payment to the "
            "Telebirr number shown above.\n\n"

            "After completing the payment, "
            "send your payment receipt.",

            parse_mode="HTML"
        )

    await request_receipt(
        callback.message,
        "telebirr"
    )

    await state.set_state(
        RegistrationStates.receipt
    )


# =========================================================
# PAYMENT METHOD — OTHER BANK → CBE
# =========================================================

@dp.callback_query(
    RegistrationStates.payment_method,
    F.data == "payment_other_bank"
)
async def select_other_bank(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        payment_method="other_bank"
    )

    await callback.answer()

    language = get_language(
        await state.get_data()
    )

    if language == "am":

        await callback.message.answer(
            "🏦 <b>ሌላ ባንክ → CBE</b>\n\n"

            "👤 <b>የCBE ሂሳብ ባለቤት</b>\n"
            f"{CBE_ACCOUNT_NAME}\n\n"

            "💳 <b>የCBE ሂሳብ ቁጥር</b>\n"
            f"<code>{CBE_ACCOUNT_NUMBER}</code>\n\n"

            "💰 <b>የሚከፈለው መጠን</b>\n"
            f"<b>{EQUB_AMOUNT} ETB</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "ከሌላ ባንክ ወደዚህ CBE ሂሳብ "
            "ክፍያውን ይፈጽሙ።\n\n"

            "ከክፍያው በኋላ የክፍያ ደረሰኝዎን "
            "ይላኩ።",

            parse_mode="HTML"
        )

    else:

        await callback.message.answer(
            "🏦 <b>OTHER BANK → CBE</b>\n\n"

            "👤 <b>CBE Account Owner</b>\n"
            f"{CBE_ACCOUNT_NAME}\n\n"

            "💳 <b>CBE Account Number</b>\n"
            f"<code>{CBE_ACCOUNT_NUMBER}</code>\n\n"

            "💰 <b>Payment Amount</b>\n"
            f"<b>{EQUB_AMOUNT} ETB</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "Make the payment from your other bank "
            "account to the CBE account above.\n\n"

            "After completing the payment, "
            "send your payment receipt.",

            parse_mode="HTML"
        )

    await request_receipt(
        callback.message,
        "other_bank"
    )

    await state.set_state(
        RegistrationStates.receipt
    )


# =========================================================
# REQUEST RECEIPT
# =========================================================

async def request_receipt(
    message: Message,
    payment_method: str
):

    if payment_method == "cbe":

        await message.answer(
            "🧾 <b>የCBE ክፍያ ደረሰኝዎን ይላኩ።</b>\n\n"
            "ትክክለኛውን የባንክ ደረሰኝ "
            "JPG፣ PNG ወይም PDF መልክ ይላኩ።\n\n"
            "⚠️ Screenshot ወይም የተቀየረ "
            "ምስል አይላኩ።",
            parse_mode="HTML"
        )

    elif payment_method == "telebirr":

        await message.answer(
            "🧾 <b>የTelebirr ክፍያ ደረሰኝዎን "
            "ይላኩ።</b>\n\n"
            "ትክክለኛውን የTelebirr ደረሰኝ "
            "JPG፣ PNG ወይም PDF መልክ ይላኩ።\n\n"
            "⚠️ Screenshot ወይም የተቀየረ "
            "ምስል አይላኩ።",
            parse_mode="HTML"
        )

    else:

        await message.answer(
            "🧾 <b>የክፍያ ደረሰኝዎን ይላኩ።</b>\n\n"
            "JPG፣ PNG ወይም PDF መልክ ይሆናል።\n\n"
            "⚠️ ትክክለኛ የክፍያ ደረሰኝ "
            "ብቻ ይላኩ።",
            parse_mode="HTML"
        )


# =========================================================
# RECEIPT PHOTO
# =========================================================

@dp.message(
    RegistrationStates.receipt,
    F.photo
)
async def receive_receipt_photo(
    message: Message,
    state: FSMContext
):

    photo = message.photo[-1]

    await process_receipt(
        message=message,
        state=state,
        file_id=photo.file_id,
        receipt_type="photo"
    )


# =========================================================
# RECEIPT DOCUMENT
# =========================================================

@dp.message(
    RegistrationStates.receipt,
    F.document
)
async def receive_receipt_document(
    message: Message,
    state: FSMContext
):

    document = message.document

    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png"
    ]

    if document.mime_type not in allowed_types:

        await message.answer(
            "❌ እባክዎ JPG፣ PNG ወይም PDF "
            "የክፍያ ደረሰኝ ይላኩ።"
        )

        return

    await process_receipt(
        message=message,
        state=state,
        file_id=document.file_id,
        receipt_type=document.mime_type
    )


# =========================================================
# PROCESS RECEIPT
# =========================================================

async def process_receipt(
    message: Message,
    state: FSMContext,
    file_id: str,
    receipt_type: str
):

    await state.update_data(
        receipt_file_id=file_id,
        receipt_file_type=receipt_type
    )

    data = await state.get_data()

    language = get_language(data)

    payment_method = data.get(
        "payment_method"
    )

    if payment_method in [
        "cbe",
        "other_bank"
    ]:

        if language == "am":

            await message.answer(
                "🔢 <b>የግብይት መለያ ቁጥርዎን "
                "ያስገቡ።</b>\n\n"
                "የCBE የግብይት መለያ ቁጥር "
                "በFT መጀመር አለበት።\n\n"
                "ለምሳሌ፦ "
                "<code>FT26123ABCDE</code>\n\n"
                "በደረሰኙ ላይ እንደተጻፈው "
                "በትክክል ያስገቡ።",
                parse_mode="HTML"
            )

        else:

            await message.answer(
                "🔢 <b>Enter your Transaction "
                "Reference Number.</b>\n\n"
                "For CBE, the reference must start "
                "with FT.\n\n"
                "Example: "
                "<code>FT26123ABCDE</code>",
                parse_mode="HTML"
            )

    else:

        if language == "am":

            await message.answer(
                "🔢 <b>የTelebirr የግብይት ቁጥርዎን "
                "ያስገቡ።</b>\n\n"
                "10–12 ፊደላት ወይም ቁጥሮች "
                "መሆን አለበት።\n\n"
                "በደረሰኙ ላይ እንደተጻፈው "
                "በትክክል ያስገቡ።",
                parse_mode="HTML"
            )

        else:

            await message.answer(
                "🔢 <b>Enter your Telebirr "
                "Transaction Number.</b>\n\n"
                "It must contain 10–12 "
                "letters or numbers.",
                parse_mode="HTML"
            )

    await state.set_state(
        RegistrationStates.transaction_reference
    )


# =========================================================
# TRANSACTION REFERENCE
# =========================================================

@dp.message(
    RegistrationStates.transaction_reference,
    F.text
)
async def receive_transaction_reference(
    message: Message,
    state: FSMContext
):

    reference = message.text.strip().upper()

    data = await state.get_data()

    language = get_language(data)

    payment_method = data.get(
        "payment_method"
    )

    # =====================================================
    # CBE VALIDATION
    # =====================================================

    if payment_method in [
        "cbe",
        "other_bank"
    ]:

        if not validate_cbe_reference(
            reference
        ):

            if language == "am":

                await message.answer(
                    "❌ ያስገቡት የክፍያ ቁጥር "
                    "ትክክል አይደለም።\n\n"
                    "የCBE የግብይት ቁጥር "
                    "በFT መጀመር አለበት።\n\n"
                    "እባክዎ ደረሰኝዎን ይመልከቱና "
                    "እንደገና ይላኩ።"
                )

            else:

                await message.answer(
                    "❌ Invalid CBE transaction reference.\n\n"
                    "Please check your receipt and "
                    "enter it again."
                )

            return

    # =====================================================
    # TELEBIRR VALIDATION
    # =====================================================

    elif payment_method == "telebirr":

        if not validate_telebirr_reference(
            reference
        ):

            if language == "am":

                await message.answer(
                    "❌ ያስገቡት የTelebirr "
                    "የግብይት ቁጥር ትክክል አይደለም።\n\n"
                    "10–12 ፊደላት ወይም ቁጥሮች "
                    "መሆን አለበት።\n\n"
                    "እባክዎ ደረሰኝዎን ይመልከቱና "
                    "እንደገና ይላኩ።"
                )

            else:

                await message.answer(
                    "❌ Invalid Telebirr transaction number.\n\n"
                    "Please check your receipt and "
                    "enter it again."
                )

            return

    else:

        await message.answer(
            "❌ Invalid payment method."
        )

        return

    # =====================================================
    # DATABASE
    # =====================================================

    db = get_db()

    try:

        # -------------------------------------------------
        # DUPLICATE TRANSACTION CHECK
        # -------------------------------------------------

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.transaction_reference ==
                reference
            )
            .first()
        )

        if existing_payment:

            if language == "am":

                await message.answer(
                    "❌ ይህ የግብይት መለያ ቁጥር "
                    "ከዚህ በፊት ተልኳል።\n\n"
                    "እባክዎ የክፍያ መረጃዎን "
                    "ይመልከቱ።"
                )

            else:

                await message.answer(
                    "❌ This transaction reference "
                    "has already been submitted."
                )

            return

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.telegram_id ==
                message.from_user.id
            )
            .first()
        )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        if not user:

            user = User(

                telegram_id=message.from_user.id,

                telegram_username=(
                    message.from_user.username
                    if message.from_user.username
                    else None
                ),

                language=language,

                participant_name=data[
                    "full_name"
                ],

                phone=data[
                    "phone"
                ]
            )

            db.add(user)

            db.flush()

        else:
            # A User represents the Telegram account. Participant details belong
            # to an individual payment because one Telegram account can register
            # several people. Do not overwrite the original account profile here.
            user.language = language

            user.telegram_username = (
                message.from_user.username
                if message.from_user.username
                else None
            )

        # -------------------------------------------------
        # RECEIPT
        # -------------------------------------------------

        receipt_file_id = data.get(
            "receipt_file_id"
        )

        receipt_file_type = data.get(
            "receipt_file_type"
        )

        if not receipt_file_id:

            await message.answer(
                "❌ ደረሰኙ አልተገኘም።\n\n"
                "እባክዎ /start በመጫን "
                "እንደገና ይጀምሩ።"
            )

            return

        # -------------------------------------------------
        # CREATE PAYMENT
        # -------------------------------------------------

        payment = Payment(

            user_id=user.id,

            payment_method=payment_method,

            receipt_path=receipt_file_id,

            transaction_reference=reference,

            payment_for=data.get("payment_for"),

            participant_name=data.get("full_name") or user.participant_name,

            # Snapshot these at submission, not approval. Otherwise a later
            # registration from the same Telegram account can overwrite the
            # phone number shown for an earlier participant.
            participant_phone=data.get("phone") or user.phone,

            status="PENDING"
        )

        db.add(payment)

        db.commit()

        db.refresh(payment)

        payment_id = payment.id

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    # =====================================================
    # USER WAITING MESSAGE
    # =====================================================

    if language == "am":

        await message.answer(
            "⏳ <b>እባክዎ ትንሽ ይጠብቁ።</b>\n\n"

            "የክፍያ መረጃዎንና ደረሰኝዎን "
            "በትክክል ልከዋል።\n\n"

            "👨‍💼 አስተዳዳሪው የCBE ወይም "
            "የTelebirr የግብይት መረጃን "
            "በመመርመር ክፍያዎን ያረጋግጣል።\n\n"

            "ማረጋገጫው ከተጠናቀቀ በኋላ "
            "የማረጋገጫ መልዕክት ይደርስዎታል።",
            parse_mode="HTML"
        )

    else:

        await message.answer(
            "⏳ <b>Please wait a moment.</b>\n\n"

            "Your payment information and receipt "
            "have been submitted successfully.\n\n"

            "An administrator will manually verify "
            "the payment.\n\n"

            "You will receive a confirmation message "
            "after verification.",
            parse_mode="HTML"
        )

    # =====================================================
    # ADMIN MESSAGE
    # =====================================================

    admin_text = (

        "🚗✨ <b>ETHIO CAR EQUB</b> ✨🚗\n\n"

        "🔔 <b>NEW PAYMENT SUBMISSION</b>\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🆔 <b>Payment ID:</b> #{payment_id}\n\n"

        f"👤 <b>Name:</b>\n"
        f"{data['full_name']}\n\n"

        f"📱 <b>Phone:</b>\n"
        f"{data['phone']}\n\n"

        f"💳 <b>Payment Method:</b>\n"
        f"{payment_method.upper()}\n\n"

        f"🔢 <b>Transaction Reference:</b>\n"
        f"<code>{reference}</code>\n\n"

        f"👥 <b>Payment For:</b>\n"
        f"{data.get('payment_for', 'N/A')}\n\n"

        "⏳ <b>Status:</b> PENDING\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "⚠️ <b>ADMIN ACTION REQUIRED</b>\n\n"

        "Check the actual transaction in the "
        "authorized CBE/Telebirr system.\n\n"

        "Do NOT approve based only on the receipt."
    )

    # =====================================================
    # SEND TO ADMIN
    # =====================================================

    admin_bot = Bot(
        token=BOT_TOKEN
    )

    try:

        await admin_bot.send_message(
            ADMIN_ID,
            admin_text,
            parse_mode="HTML",
            reply_markup=admin_payment_keyboard(
                payment_id
            )
        )

        # -------------------------------------------------
        # SEND RECEIPT
        # -------------------------------------------------

        if receipt_file_type == "photo":

            await admin_bot.send_photo(
                ADMIN_ID,
                photo=receipt_file_id,
                caption=(
                    "🧾 <b>Payment Receipt</b>\n\n"
                    f"Payment ID: #{payment_id}"
                ),
                parse_mode="HTML"
            )

        else:

            await admin_bot.send_document(
                ADMIN_ID,
                document=receipt_file_id,
                caption=(
                    "🧾 <b>Payment Receipt</b>\n\n"
                    f"Payment ID: #{payment_id}"
                ),
                parse_mode="HTML"
            )

    finally:

        await admin_bot.session.close()

    # =====================================================
    # WAITING FOR ADMIN
    # =====================================================

    await state.set_state(
        RegistrationStates.waiting_for_admin
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    print(
        "🚗 ETHIO CAR EQUB BOT IS RUNNING..."
    )

    await dp.start_polling(
        bot
    )


# =========================================================
# RUN
# =========================================================
# =========================================================
# ADMIN APPROVE PAYMENT
# =========================================================

# =========================================================
# MASK PHONE NUMBER
# =========================================================

def mask_phone(phone: str) -> str:

    phone = str(phone).strip()

    if len(phone) <= 6:
        return phone

    return phone[:4] + "****" + phone[-2:]


@dp.callback_query(
    F.data.startswith("approve_")
)
async def approve_payment(
    callback: CallbackQuery
):

    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Unauthorized action.",
            show_alert=True
        )

        return

    # -----------------------------------------------------
    # GET PAYMENT ID
    # -----------------------------------------------------

    try:

        payment_id = int(
            callback.data.split("_")[1]
        )

    except (ValueError, IndexError):

        await callback.answer(
            "❌ Invalid payment ID.",
            show_alert=True
        )

        return

    db = get_db()

    try:

        # -------------------------------------------------
        # FIND PAYMENT
        # -------------------------------------------------

        payment = db.query(Payment).filter(
            Payment.id == payment_id
        ).first()

        # -------------------------------------------------
        # ENSURE PARTICIPANT SNAPSHOT
        # -------------------------------------------------
        # Fetch the user now so we can snapshot their name into the
        # payment record. This prevents later user profile changes from
        # altering the historical payment entry shown on the dashboard.
        user_for_snapshot = db.query(User).filter(
            User.id == payment.user_id
        ).first() if payment else None

        if not payment:

            await callback.answer(
                "❌ Payment not found.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # PREVENT DOUBLE APPROVAL
        # -------------------------------------------------

        if payment.status == "APPROVED":

            await callback.answer(
                "⚠️ This payment is already approved.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # PREVENT APPROVING REJECTED PAYMENT
        # -------------------------------------------------

        if payment.status == "REJECTED":

            await callback.answer(
                "⚠️ This payment was already rejected.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # APPROVE PAYMENT
        # -------------------------------------------------

        payment.status = "APPROVED"
        payment.verified_at = datetime.utcnow()

        # Snapshot participant name if not already set (covers older rows
        # created before migrations or cases where it was left NULL).
        if not payment.participant_name and user_for_snapshot:
            payment.participant_name = user_for_snapshot.participant_name

        # Snapshot participant phone if not already set so each payment keeps
        # the phone number the user had at approval time.
        if not getattr(payment, 'participant_phone', None) and user_for_snapshot:
            payment.participant_phone = user_for_snapshot.phone

        db.flush()

        approved_count = db.query(Payment).filter(
            Payment.status == "APPROVED"
        ).count()

        payment.participant_number = approved_count

        db.commit()

        # -------------------------------------------------
        # GET USER
        # -------------------------------------------------

        user = db.query(User).filter(
            User.id == payment.user_id
        ).first()

        if not user:

            await callback.answer(
                "⚠️ Payment approved, but user was not found.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # GENERATE PARTICIPANT NUMBER
        # -------------------------------------------------

        participant_number = payment.participant_number

        # -------------------------------------------------
        # USER CONFIRMATION
        # -------------------------------------------------

        confirmation_message = (
            "🚗✨ <b>ETHIO CAR EQUB</b> ✨🚗\n\n"

            "🎉 <b>የተሳታፊ ምዝገባዎ ተረጋግጧል!</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "✅ የክፍያ መረጃዎ በአስተዳዳሪ "
            "ተረጋግጧል።\n\n"

            f"🎟️ <b>የተሳታፊ ቁጥር</b>\n"
            f"#{participant_number:03d}\n\n"

            f"👤 <b>ስም</b>\n"
            f"{payment.participant_name or user.participant_name}\n\n"

            f"📱 <b>ስልክ</b>\n"
            f"{mask_phone(payment.participant_phone or user.phone)}\n\n"

            "💳 <b>የክፍያ ሁኔታ</b>\n"
            "✅ ተረጋግጧል\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "✅ በETHIO CAR EQUB በትክክል "
            "ተመዝግበዋል።\n\n"

            "📢 የተሳታፊዎች ዝርዝር በTelegram "
            "ቻናላችን ላይ ይገኛል።\n\n"

            "🍀 <b>መልካም እድል!</b>"
        )

        # -------------------------------------------------
        # SEND USER CONFIRMATION
        # -------------------------------------------------

        bot = Bot(token=BOT_TOKEN)

        try:

            await bot.send_message(
                user.telegram_id,
                confirmation_message,
                parse_mode="HTML"
            )

        finally:

            await bot.session.close()

        # -------------------------------------------------
        # UPDATE ADMIN MESSAGE
        # -------------------------------------------------

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

        await callback.message.answer(
            "✅ Payment approved successfully.\n"
            f"Participant number: #{participant_number:03d}"
        )

        await callback.answer(
            "✅ Payment approved.",
            show_alert=True
        )

    except Exception as e:

        db.rollback()

        print(
            f"APPROVE ERROR: {e}"
        )

        await callback.answer(
            "❌ An error occurred while approving.",
            show_alert=True
        )

    finally:

        db.close()


# =========================================================
# ADMIN REJECT PAYMENT
# =========================================================

@dp.callback_query(
    F.data.startswith("reject_")
)
async def reject_payment(
    callback: CallbackQuery
):

    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "❌ Unauthorized action.",
            show_alert=True
        )

        return

    # -----------------------------------------------------
    # GET PAYMENT ID
    # -----------------------------------------------------

    try:

        payment_id = int(
            callback.data.split("_")[1]
        )

    except (ValueError, IndexError):

        await callback.answer(
            "❌ Invalid payment ID.",
            show_alert=True
        )

        return

    db = get_db()

    try:

        # -------------------------------------------------
        # FIND PAYMENT
        # -------------------------------------------------

        payment = db.query(Payment).filter(
            Payment.id == payment_id
        ).first()

        if not payment:

            await callback.answer(
                "❌ Payment not found.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # PREVENT DOUBLE REJECTION
        # -------------------------------------------------

        if payment.status == "REJECTED":

            await callback.answer(
                "⚠️ This payment is already rejected.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # PREVENT REJECTING APPROVED PAYMENT
        # -------------------------------------------------

        if payment.status == "APPROVED":

            await callback.answer(
                "⚠️ This payment is already approved.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # REJECT PAYMENT
        # -------------------------------------------------

        payment.status = "REJECTED"
        payment.verified_at = datetime.utcnow()

        payment.rejection_reason = (
            "Payment was rejected by administrator."
        )

        db.commit()

        # -------------------------------------------------
        # GET USER
        # -------------------------------------------------

        user = db.query(User).filter(
            User.id == payment.user_id
        ).first()

        if not user:

            await callback.answer(
                "⚠️ Payment rejected, but user was not found.",
                show_alert=True
            )

            return

        # -------------------------------------------------
        # USER REJECTION MESSAGE
        # -------------------------------------------------

        rejection_message = (
            "🚗✨ <b>ETHIO CAR EQUB</b> ✨🚗\n\n"

            "❌ <b>የክፍያ ማረጋገጫ አልተሳካም</b>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "ያስገቡት የክፍያ መረጃ "
            "በአስተዳዳሪ ማረጋገጫ አልፏል።\n\n"

            "እባክዎ የክፍያዎን ደረሰኝ እና "
            "የግብይት ቁጥር በትክክል ያረጋግጡ።\n\n"

            "🔄 ከዚያ እንደገና ይላኩ።\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "🙏 እናመሰግናለን።"
        )

        # -------------------------------------------------
        # SEND REJECTION TO USER
        # -------------------------------------------------

        bot = Bot(token=BOT_TOKEN)

        try:

            await bot.send_message(
                user.telegram_id,
                rejection_message,
                parse_mode="HTML"
            )

        finally:

            await bot.session.close()

        # -------------------------------------------------
        # UPDATE ADMIN MESSAGE
        # -------------------------------------------------

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

        await callback.message.answer(
            "❌ Payment rejected."
        )

        await callback.answer(
            "❌ Payment rejected.",
            show_alert=True
        )

    except Exception as e:

        db.rollback()

        print(
            f"REJECT ERROR: {e}"
        )

        await callback.answer(
            "❌ An error occurred while rejecting.",
            show_alert=True
        )

    finally:

        db.close()
        
        
if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "🛑 ETHIO CAR EQUB BOT STOPPED."
        )
        
