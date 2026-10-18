import re
from typing import Dict, Any

class LinkValidatorService:
    @staticmethod
    def sanitize_link(link: str) -> str:
        clean_link = link.split('?')[0].strip()
        return clean_link

    @classmethod
    def validate_telegram_post_link(cls, raw_input: str) -> Dict[str, Any]:
        if not raw_input:
            return {"is_valid": False, "error": "ورودی خالی است."}
            
        cleaned = cls.sanitize_link(raw_input)
        
        public_pattern = r"(https?://)?(www\.)?t\.me/([a-zA-Z0-9_]{5,})/(\d+)$"
        match_pub = re.match(public_pattern, cleaned)
        if match_pub:
            channel_username = match_pub.group(3)
            post_id = int(match_pub.group(4))
            return {
                "is_valid": True,
                "type": "public",
                "channel": channel_username,
                "post_id": post_id,
                "final_link": f"https://t.me/{channel_username}/{post_id}",
                "error": None
            }
            
        private_pattern = r"(https?://)?(www\.)?t\.me/c/(\d+)/(\d+)$"
        match_priv = re.match(private_pattern, cleaned)
        if match_priv:
            channel_id = match_priv.group(3)
            post_id = int(match_priv.group(4))
            return {
                "is_valid": True,
                "type": "private",
                "channel_id": channel_id,
                "post_id": post_id,
                "final_link": f"https://t.me/c/{channel_id}/{post_id}",
                "error": None
            }

        return {
            "is_valid": False,
            "error": "فرمت لینک یا پست تلگرام نامعتبر است."
        }
