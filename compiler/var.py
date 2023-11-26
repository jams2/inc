from dataclasses import dataclass


@dataclass
class Var:
    name: str

    def __hash__(self):
        return hash((Var, self.name))
