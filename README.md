# Abaqus INP node parser

Extract explicit mesh node labels and Cartesian coordinates into CSV for downstream CAE automation. Adapted and refactored from a research preprocessing script; the included fixture is entirely synthetic.

## Run

Requires Python 3.9 or newer; no third-party packages or Abaqus installation needed.

```sh
python extract_nodes.py example.inp nodes.csv
python -m unittest discover -s tests -v
```

Output columns: `part_name,node_id,x,y,z`. Node labels are unique within each part, not necessarily across the model. The example emits five nodes from two parts.

## Scope

Supports explicit part-level `*Node` blocks, case-insensitive keywords, comments, two- or three-dimensional coordinates and scientific notation. It rejects duplicate labels within a part, non-finite coordinates, includes, generated nodes and coordinate-system transformations instead of silently returning incomplete coordinates.

This is a focused node extractor, not a complete Abaqus parser. Coordinates remain in each part's local coordinate system. Instance placement and assembly transformations are not applied. Convert coordinates to a common frame before spatial load mapping. All examples are synthetic; no research meshes, measured loads or project identifiers are included.
