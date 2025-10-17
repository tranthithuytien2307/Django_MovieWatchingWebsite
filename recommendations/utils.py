import requests
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken

def call_internal_api(request, method, url, data=None, params=None):
    """
    Gọi API nội bộ Django, tự động thêm JWT access_token vào header
    """
    # Lấy access_token từ session
    access_token = request.session.get('jwt_access_token')
    expires_at = request.session.get('jwt_expires_at', 0)

    # Nếu token hết hạn → tạo mới từ refresh_token
    if datetime.now().timestamp() > expires_at:
        refresh_token = request.session.get('jwt_refresh_token')
        if refresh_token:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            # cập nhật lại session
            request.session['jwt_access_token'] = access_token
            request.session['jwt_expires_at'] = (datetime.now() + timedelta(minutes=15)).timestamp()
        else:
            raise Exception("No valid JWT tokens in session")

    headers = {"Authorization": f"Bearer {access_token}"}

    if method.lower() == "get":
        return requests.get(url, headers=headers, params=params)
    elif method.lower() == "post":
        return requests.post(url, headers=headers, data=data, json=data)
    else:
        raise Exception(f"Unsupported method: {method}")
