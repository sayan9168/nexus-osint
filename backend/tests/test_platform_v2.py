from uuid import uuid4
from osint_core.auth import create_user,authenticate,issue_session,decode_session
from osint_core.audit import record,verify_chain
from osint_core.intelligence import fingerprint,merge_relationship

def test_auth_round_trip():
    username="test_"+uuid4().hex[:10]
    user=create_user(username,"strong-password-123")
    assert authenticate(username,"strong-password-123")["id"]==user["id"]
    assert authenticate(username,"wrong-password") is None
    assert decode_session(issue_session(user))["username"]==username

def test_entity_fingerprint_is_stable():
    assert fingerprint("domain","Example.COM.")==fingerprint("domain","example.com")

def test_relationship_merge_is_idempotent():
    case=str(uuid4())
    rid1=merge_relationship(case,"a","b","resolves-to",.8)["id"]
    rid2=merge_relationship(case,"a","b","resolves-to",.9)["id"]
    assert rid1==rid2

def test_audit_chain_verifies():
    record("test","pytest","platform",{"ok":True})
    assert verify_chain()["valid"] is True
