@router.callback_query(F.data == "check_channel_join")
async def check_channel_join_callback(
    callback: CallbackQuery,
    db_user: User,
) -> None:
    """بررسی مجدد عضویت کاربر هنگام کلیک روی دکمه تایید عضویت."""
    lang = db_user.language_code or "fa"
    from app.core.config import settings
    channel_id = getattr(settings, "required_channel_id", None)

    if not channel_id:
        await callback.answer(text=get_text("join_verified", lang), show_alert=True)
        if callback.message:
            await callback.message.delete()
        return

    try:
        member = await callback.bot.get_chat_member(chat_id=channel_id, user_id=callback.from_user.id)
        from aiogram.enums import ChatMemberStatus
        if member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
            await callback.answer(text=get_text("join_verified", lang), show_alert=True)
            if callback.message:
                await callback.message.delete()
                await callback.message.answer(
                    text=get_text("welcome", lang, name=db_user.first_name),
                    reply_markup=get_main_menu_keyboard(lang),
                )
        else:
            await callback.answer(text=get_text("not_joined_yet", lang), show_alert=True)
    except Exception as e:
        await callback.answer(text="خطا در اعتبارسنجی / Validation Error", show_alert=True)