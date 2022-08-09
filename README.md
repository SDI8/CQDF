# CADQuery Design Format

Structure your CADQuery scripts as proper parametric designs. Define and constrain parameters explicitly, without magic and with full type support, and evaluate the design in whatever way suits you best - directly as a python file or through any application implementing the CQDF Driver.

This repository is in its early days. Expect neither tests nor documentation.

## Why not CADQuery Gateway Interface?

TODO

## Writing your first design

TODO

For now, have a look at `./samples`

# Development

## Architecture

## CQDF core

The core library, `cqdf`, defines all logic and models for all default parameter types. Besides that, it implements the CQDF driver. The driver provides an interface for executing designs.

## CQDF CLI

The CLI exposes the CQDF driver to the user and is the most direct way of using CQDF. Use `cqdf_cli -h` or `python -m cqdf_cli -h` for help on the tool.
This tool is particularly useful when evaluating batches of designs or quickly iterating over different sets of parameters.

## Future

TODO
