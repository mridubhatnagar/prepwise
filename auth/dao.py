import logging
import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError as SADatabaseError

from exceptions import DatabaseError
from infra.postgres import SessionLocal
from auth.models import User, AllowedUser, AccessAttempt

logger = logging.getLogger(__name__)


class IUserDAO(ABC):
    @abstractmethod
    def create(self, google_auth_id: str, email: str, name: str, avatar_url: str) -> User: ...

    @abstractmethod
    def update(self, user_id: str, name: str, avatar_url: str) -> User: ...

    @abstractmethod
    def get_by_auth_id(self, google_auth_id: str) -> User | None: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...


class UserDAO(IUserDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(self, google_auth_id: str, email: str, name: str, avatar_url: str) -> User:
        try:
            user = User(
                id=uuid.uuid4(),
                google_auth_id=google_auth_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info("Created user id=%s email=%s", user.id, email)
            return user
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error("UserDAO.create failed: %s", exc)
            raise DatabaseError("Failed to create user") from exc

    def update(self, user_id: str, name: str, avatar_url: str) -> User:
        try:
            user = self.db.get(User, uuid.UUID(user_id))
            if user is None:
                raise ValueError(f"User {user_id} not found")
            user.name = name
            user.avatar_url = avatar_url
            self.db.commit()
            self.db.refresh(user)
            return user
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error("UserDAO.update failed for user_id=%s: %s", user_id, exc)
            raise DatabaseError("Failed to update user") from exc

    def get_by_auth_id(self, google_auth_id: str) -> User | None:
        try:
            return self.db.query(User).filter(User.google_auth_id == google_auth_id).first()
        except (OperationalError, SADatabaseError) as exc:
            logger.error("UserDAO.get_by_auth_id failed: %s", exc)
            raise DatabaseError("Failed to fetch user") from exc

    def get_by_id(self, user_id: str) -> User | None:
        try:
            return self.db.get(User, uuid.UUID(user_id))
        except (OperationalError, SADatabaseError) as exc:
            logger.error("UserDAO.get_by_id failed for user_id=%s: %s", user_id, exc)
            raise DatabaseError("Failed to fetch user") from exc


class IAllowedUserDAO(ABC):
    @abstractmethod
    def is_allowed(self, email: str) -> AllowedUser | None: ...


class AllowedUserDAO(IAllowedUserDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def is_allowed(self, email: str) -> AllowedUser | None:
        try:
            return self.db.query(AllowedUser).filter(AllowedUser.email == email).first()
        except (OperationalError, SADatabaseError) as exc:
            logger.error("AllowedUserDAO.is_allowed failed for email=%s: %s", email, exc)
            raise DatabaseError("Failed to check allowed user") from exc


class IAccessAttemptDAO(ABC):
    @abstractmethod
    def create(self, email: str) -> None: ...


class AccessAttemptDAO(IAccessAttemptDAO):
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(self, email: str) -> None:
        try:
            attempt = AccessAttempt(id=uuid.uuid4(), email=email)
            self.db.add(attempt)
            self.db.commit()
            logger.warning("Unauthorised access attempt recorded for email=%s", email)
        except (OperationalError, IntegrityError, SADatabaseError) as exc:
            logger.error("AccessAttemptDAO.create failed for email=%s: %s", email, exc)
            raise DatabaseError("Failed to record access attempt") from exc
