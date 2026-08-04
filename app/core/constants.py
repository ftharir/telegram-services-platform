from enum import Enum


class Language(str, Enum):
    """Supported languages in the bot."""
    FA = "fa"
    EN = "en"


DEFAULT_LANGUAGE = Language.FA
SUPPORTED_LANGUAGES = [Language.FA, Language.EN]