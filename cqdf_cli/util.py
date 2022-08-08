from cqdf.interface import ParameterValue
from rich.table import Table


def describe_parameters(params: list[ParameterValue]):
    table = Table(title="Parameters")

    table.add_column("Key", style="cyan")
    table.add_column("Description")
    table.add_column("Type")
    table.add_column("Unit")
    table.add_column("Datatype")
    table.add_column("Category")

    for p in params:
        table.add_row(
            p.key,
            p.value.description,
            p.ptype.name,
            p.value.unit.value
            + (
                ""
                if p.value.unit.value == p.value.unit.name
                else f"({p.value.unit.name})"
            ),
            p.value.vtype.name,
            p.value.category.name if p.value.category else "",
        )

    return table
