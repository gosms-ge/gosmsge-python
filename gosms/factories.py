import random
from dataclasses import dataclass


@dataclass
class SMSFactory:
    sender: str = ''.join([chr(random.randint(65, 91)) for _ in range(random.randint(10, 20))])
    to: str = f"9955{''.join([str(random.randint(0, 9)) for _ in range(8)])}"
    text: str = ''.join([chr(random.randint(97, 123)) for _ in range(random.randint(10, 60))])

    def __str__(self) -> str:
        return f"{self.sender} - {self.to}"
