from cqdf.design import finish, user_input
from cqdf.parameter import (
    Category,
    Choice,
    DesignParameters,
    Numeric,
    Range,
    Text,
    Toggle,
    Unit,
)

my_category = Category("Text")


class Params(DesignParameters):
    size = Numeric(4.2, description="Parameters can be described")
    left_offset = Numeric(10, unit=Unit.μm)
    string = Text("London", name="City")
    fill = Choice(("All", "Nothing"))
    placement = Choice([10, 12, 0], 0)
    placement2 = Choice([10.0, 12.2, 0.0], 0)
    text_size = Range(0.0, 10, 0, unit=Unit.inch, category=my_category)
    text_size2 = Range(0, 10, 0, unit=Unit.mm, category=my_category)
    side = Toggle(False, description="Should it be done?", name="Do it")


params = user_input(Params)

print(vars(params))

finish(None)
