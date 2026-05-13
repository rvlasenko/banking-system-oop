from uuid import uuid4

from .enums import ClientStatus
from ..exceptions.invalid_operation import InvalidOperationError


class Client:
    def __init__(
        self,
        full_name: str,
        age: int,
        pin_code: str,
        client_id: str | None = None,
        contacts: dict | None = None,
        status: ClientStatus = ClientStatus.ACTIVE,
    ):
        self.full_name = self._validate_full_name(full_name)
        self.age = self._validate_age(age)
        self.pin_code = self._validate_pin_code(pin_code)
        self.client_id = self._validate_client_id(client_id)
        self.contacts = self._validate_contacts(contacts)
        self.status = self._validate_status(status)

        self.account_ids: list[str] = []
        self.failed_login_attempts = 0
        self.is_suspicious = False

    def _validate_full_name(self, full_name: str) -> str:
        if not isinstance(full_name, str):
            raise InvalidOperationError("Full name must be a string")

        clean_full_name = full_name.strip()

        if not clean_full_name:
            raise InvalidOperationError("Full name cannot be empty")

        return clean_full_name

    def _validate_age(self, age: int) -> int:
        if not isinstance(age, int):
            raise InvalidOperationError("Age must be an integer")

        if age < 18:
            raise InvalidOperationError("Client must be at least 18 years old")

        return age

    def _validate_pin_code(self, pin_code: str) -> str:
        if not isinstance(pin_code, str):
            raise InvalidOperationError("PIN must be a string")

        clean_code = pin_code.strip()

        if not clean_code:
            raise InvalidOperationError("PIN cannot be empty")

        return clean_code

    @staticmethod
    def _generate_client_id() -> str:
        return f"C-{str(uuid4())[:8].upper()}"

    def _validate_client_id(self, client_id: str | None) -> str:
        if client_id is None:
            # Generate short random client ID if not provided
            return self._generate_client_id()
        elif not isinstance(client_id, str):
            raise InvalidOperationError("Client ID must be a string")

        clean_id = client_id.strip()

        if not clean_id:
            raise InvalidOperationError("Client ID cannot be empty")

        return clean_id

    def _validate_contacts(self, contacts: dict | None) -> dict[str, str]:
        if contacts is None:
            return {}

        if not isinstance(contacts, dict):
            raise InvalidOperationError("Contacts must be a dictionary")

        return contacts

    def _validate_status(self, status: ClientStatus) -> ClientStatus:
        if not isinstance(status, ClientStatus):
            raise InvalidOperationError("Status must be a ClientStatus")

        return status
