from enum import Enum


class JobModels(Enum):
    ON_SITE = 1
    REMOTE = 2
    HYBRID = 3

    @property
    def lower_case_name(self):
        return self.name.lower()
