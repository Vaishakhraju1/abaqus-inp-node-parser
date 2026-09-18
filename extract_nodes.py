"""Extract explicit Cartesian part nodes from a self-contained Abaqus input file."""
import argparse
import csv
import math
from pathlib import Path


def parse_nodes(lines):
    part = None
    reading = False
    seen = set()
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith('**'):
            continue
        if line.startswith('*'):
            fields = [item.strip() for item in line.split(',')]
            keyword = fields[0].lower()
            params = dict(item.lower().split('=', 1) for item in fields[1:] if '=' in item)
            reading = False
            if keyword in ('*include', '*system', '*ngen', '*nfill', '*ncopy'):
                raise ValueError('Line %d: unsupported keyword %s' % (number, keyword))
            if keyword == '*part':
                part = next((item.split('=', 1)[1].strip() for item in fields[1:]
                             if item.lower().startswith('name=')), None)
                if not part:
                    raise ValueError('Line %d: part name is required' % number)
            elif keyword == '*end part':
                part = None
            elif keyword == '*node':
                if part is None:
                    raise ValueError('Line %d: only part-level nodes are supported' % number)
                if any(key != 'nset' for key in params):
                    raise ValueError('Line %d: unsupported node parameters' % number)
                reading = True
            continue
        if reading:
            values = [item.strip() for item in line.split(',')]
            if len(values) not in (3, 4):
                raise ValueError('Line %d: expected label,x,y[,z]' % number)
            label = int(values[0])
            xyz = [float(item.replace('D', 'E').replace('d', 'e')) for item in values[1:]]
            if len(xyz) == 2:
                xyz.append(0.0)
            if label < 1 or not all(math.isfinite(value) for value in xyz):
                raise ValueError('Line %d: invalid label or coordinates' % number)
            key = (part, label)
            if key in seen:
                raise ValueError('Duplicate node %s in part %s' % (label, part))
            seen.add(key)
            yield dict(zip(('part_name', 'node_id', 'x', 'y', 'z'), (part, label, *xyz)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Input and output must be different files')
    with args.input.open(encoding='utf-8-sig') as source:
        rows = list(parse_nodes(source))
    if not rows:
        parser.error('No explicit part nodes found')
    with args.output.open('w', newline='', encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames=('part_name', 'node_id', 'x', 'y', 'z'))
        writer.writeheader()
        writer.writerows(rows)
    print('Wrote %d nodes to %s' % (len(rows), args.output))


if __name__ == '__main__':
    main()
