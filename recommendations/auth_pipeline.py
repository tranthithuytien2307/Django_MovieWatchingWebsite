from .models import UserToken
import uuid
from datetime import datetime, timedelta

def save_tokens(strategy, details, response, user=None, *args, **kwargs):
    """
    Lưu access_token và refresh_token từ Google vào bảng UserToken
    """
    if user and response.get("access_token"):
        access_token = response.get("access_token")
        refresh_token = response.get("refresh_token")

        # Google trả về thời gian hết hạn access token (seconds)
        expires_in = response.get("expires_in", 3600)
        access_expires_at = datetime.now() + timedelta(seconds=expires_in)

        UserToken.objects.create(
            id=uuid.uuid4(),
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            # refresh_expires_at: Google không luôn trả, bạn có thể bỏ qua
        )
