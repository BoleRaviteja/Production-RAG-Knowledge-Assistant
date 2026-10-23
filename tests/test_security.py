from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_roundtrip():
    h = hash_password("correct horse")
    assert verify_password("correct horse", h)
    assert not verify_password("wrong", h)


def test_token_roundtrip_and_tamper():
    token = create_access_token("42")
    assert decode_access_token(token) == "42"
    assert decode_access_token(token + "x") is None
