import cadquery as cq
import OCP
from cqdf.design import finish, user_input
from cqdf.parameter import Choice, DesignParameters, Numeric, Text, Unit


def get_font_names() -> list[str]:
    """
    Utility function to get all OCP supported fonts
    """
    fnt_seq = OCP.TColStd.TColStd_SequenceOfHAsciiString()
    alias_seq = OCP.TColStd.TColStd_SequenceOfHAsciiString()
    mgr = OCP.Font.Font_FontMgr.GetInstance_s()
    mgr.GetAllAliases(fnt_seq)
    mgr.GetAvailableFontsNames(alias_seq)

    to_list = lambda seq: [seq.Value(i) for i in range(1, seq.Length() + 1)]
    return ["".join(to_list(fn)) for fn in to_list(fnt_seq) + to_list(alias_seq)]


# Define all parameters for this design
class LabelParams(DesignParameters):
    string = Text("12½")
    size = Numeric(10, unit=Unit.mm)
    thickness = Numeric(2, unit=Unit.mm)
    holeDiameter = Numeric(3, unit=Unit.mm)
    padding = Numeric(2, unit=Unit.mm)
    font = Choice(get_font_names(), "IBM 3270 Narrow Medium")
    font_style = Choice(["regular", "bold", "italic"])


params = user_input(LabelParams)  # Instantiate

# Generate the text shape
text = cq.Workplane().text(
    params.string.value,
    params.size.value,
    -params.thickness.value / 2,
    font=params.font.value,
    kind=params.font_style.value,  # type: ignore
)

# Generate a base-shape and subtract the text
bb = text.findSolid().BoundingBox()
part = (
    cq.Workplane()
    .rect(bb.xlen + params.padding.value * 4, bb.ylen + params.padding.value * 2)
    .moveTo(-bb.xlen / 2 - params.padding.value * 2)
    .circle(bb.ylen / 2 + params.padding.value)
    .extrude(-params.thickness.value)
    .moveTo(-bb.xlen / 2 - params.padding.value * 2)
    .circle(params.holeDiameter.value / 2)
    .cutThruAll()
    .moveTo()
    .cut(text)
    .findSolid()
)

# Complete this design
finish(part)
