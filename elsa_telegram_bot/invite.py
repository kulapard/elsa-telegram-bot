import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from loguru import logger

TOKEN_TTL = 86400  # 24 hours


def _get_code() -> str:
    return secrets.token_hex(16)


def _get_expiration_date() -> datetime:
    return datetime.utcnow() + timedelta(seconds=TOKEN_TTL)


@dataclass(kw_only=True)
class Invitation:
    code: str = field(default_factory=_get_code)
    is_used: bool = False
    expire_at: datetime = field(default_factory=_get_expiration_date)
    user_id: int = None

    @property
    def is_expired(self) -> bool:
        now = datetime.utcnow()
        logger.debug(f"Invitation {self.code} expires at {self.expire_at} now is {now}")
        return now > self.expire_at

    def use(self) -> None:
        self.is_used = True


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
    _GENERATE_MAX_TRIES = 3

    @classmethod
    def _try_to_generate_and_save(cls) -> Invitation | None:
        invitation = Invitation()
        try:
            cls._storage.save(invitation)
        except DuplicateInvitationCode:
            return None
        return invitation

    @classmethod
    def generate(cls) -> Invitation:
        invitation = None
        try_count = 1
        while invitation is None and try_count <= cls._GENERATE_MAX_TRIES:
            logger.info(
                f"Trying to generate invitation, attempt {try_count}/{cls._GENERATE_MAX_TRIES}"
            )
            invitation = cls._try_to_generate_and_save()
            try_count += 1

        if invitation is None:
            raise RuntimeError("Failed to generate invitation code")

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
