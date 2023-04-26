import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from loguru import logger

TOKEN_TTL = 86400  # 24 hours


def _get_expiration_date() -> datetime:
    return datetime.utcnow() + timedelta(seconds=TOKEN_TTL)


@dataclass(kw_only=True)
class Invitation:
    code: str
    is_used: bool = False
    expire_at: datetime = field(default_factory=_get_expiration_date)

    @property
    def is_expired(self) -> bool:
        now = datetime.utcnow()
        logger.debug(f"Invitation {self.code} expires at {self.expire_at} now is {now}")
        return now > self.expire_at


class InvitationNotFound(Exception):
    pass


class DuplicateInvitationCode(Exception):
    pass


class InvitationStorage:
    def __init__(self):
        self._storage = {}

    def get_all(self) -> list[Invitation]:
        return list(self._storage.values())

    def save(self, invitation: Invitation) -> None:
        logger.debug(f"Saving invitation {invitation!r}")
        if invitation.code in self._storage:
            raise DuplicateInvitationCode("Invitation code already exists")
        self._storage[invitation.code] = invitation

    def get_by_code(self, code: str) -> Invitation:
        try:
            return self._storage[code]
        except KeyError:
            raise InvitationNotFound("Invitation code does not exist") from None

    def delete_by_code(self, code: str) -> None:
        if code not in self._storage:
            raise InvitationNotFound("Invitation code does not exist")
        self._storage.pop(code)
        logger.debug(f"Deleted invitation {code!r}")


class Invite:
    # TODO: use a database instead of in-memory storage
    _storage = InvitationStorage()

    @classmethod
    def generate(cls) -> Invitation:
        code = secrets.token_hex(8)
        invitation = Invitation(code=code)
        cls._storage.save(invitation)
        logger.info(f"Generated invitation {invitation!r}")
        return invitation

    @classmethod
    def get(cls, code: str) -> Invitation:
        return cls._storage.get_by_code(code)

    @classmethod
    def delete(cls, code: str) -> None:
        logger.info(f"Deleting invitation {code!r}")
        cls._storage.delete_by_code(code)

    @classmethod
    def check(cls, code: str) -> bool:
        logger.info(cls._storage.get_all())
        try:
            invitation = cls._storage.get_by_code(code)
        except InvitationNotFound:
            logger.error(f"Invitation not found for code {code!r}", code)
            return False

        logger.info(f"Invitation found for code {code!r}: {invitation!r}")

        if invitation.is_used:
            logger.error(f"Invitation already used for code {code!r}: {invitation!r}")
            return False

        if invitation.is_expired:
            logger.error(f"Invitation expired for code {code!r}: {invitation!r}")
            return False
        return True

    @classmethod
    def use(cls, code: str, user_id: int) -> None:
        logger.info(f"Using invitation {code!r} for user {user_id}")
        invitation = cls._storage.get_by_code(code)
        invitation.is_used = True
        invitation.user_id = user_id
        cls._storage.save(invitation)

    @classmethod
    def clear_expired(cls) -> None:
        logger.info("Clearing expired invitations")
        for invitation in cls._storage.get_all():
            if invitation.is_expired:
                cls._storage.delete_by_code(invitation.code)
