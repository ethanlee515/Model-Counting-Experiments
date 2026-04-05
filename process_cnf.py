#!/usr/bin/env python3

from __future__ import annotations
import argparse
import re
from pathlib import Path


AAG_HEADER_RE = re.compile(r"^aag\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
CNF_MAP_RE = re.compile(r"^c\s+(\d+)\s*->\s*(\d+)\s*$")


def parse_aag_inputs(aag_path: Path, assert_even_inputs: bool = True) -> list[int]:
    lines = aag_path.read_text().splitlines()
    if not lines:
        raise ValueError(f"Empty AAG file: {aag_path}")

    m = AAG_HEADER_RE.match(lines[0])
    if m is None:
        raise ValueError(f"Invalid AAG header in {aag_path}: {lines[0]!r}")

    _maxvar, num_inputs, num_latches, num_outputs, num_ands = map(int, m.groups())

    input_lines = lines[1 : 1 + num_inputs]
    if len(input_lines) != num_inputs:
        raise ValueError(
            f"AAG says {num_inputs} inputs, but file ended early in {aag_path}"
        )

    input_literals = [int(x.strip()) for x in input_lines]

    if assert_even_inputs:
        expected = [2 * i for i in range(1, num_inputs + 1)]
        assert input_literals == expected, (
            f"Unexpected AAG input literals.\n"
            f"  expected: {expected}\n"
            f"  actual:   {input_literals}"
        )

    return input_literals


def parse_cnf_port_map(cnf_path: Path) -> dict[int, int]:
    """
    Parse comment lines of the form:
        c 2 -> 2
        c 4 -> 3
    returning a map {aig_literal: cnf_var}.
    """
    mapping: dict[int, int] = {}
    for line in cnf_path.read_text().splitlines():
        m = CNF_MAP_RE.match(line)
        if m is not None:
            aig_lit = int(m.group(1))
            cnf_var = int(m.group(2))
            mapping[aig_lit] = cnf_var
    return mapping


def strip_port_map_lines(lines: list[str]) -> list[str]:
    """
    Remove only the port-map comment lines:
        c <aig_lit> -> <cnf_var>

    Keep all other CNF lines/comments unchanged.
    """
    return [line for line in lines if CNF_MAP_RE.match(line) is None]


def build_processed_cnf_text(
    cnf_path: Path,
    projection_vars: list[int],
    one_show_per_line: bool = True,   # default behavior
) -> str:
    original_lines = cnf_path.read_text().splitlines()

    # Remove port-map comments from the processed output
    cleaned_lines = strip_port_map_lines(original_lines)

    out_lines: list[str] = []
    out_lines.append("c t pmc")
    out_lines.extend(cleaned_lines)

    if one_show_per_line:
        for var in projection_vars:
            out_lines.append(f"c p show {var} 0")
    else:
        joined = " ".join(str(v) for v in projection_vars)
        out_lines.append(f"c p show {joined} 0")

    return "\n".join(out_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post-process CNF for projected model counting using AAG input info."
    )
    parser.add_argument("aag", type=Path, help="Input .aag file")
    parser.add_argument("cnf", type=Path, help="Input .cnf file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output processed CNF file",
    )
    parser.add_argument(
        "--single-show-line",
        action="store_true",
        help="Emit one combined 'c p show v1 v2 ... 0' line instead of one variable per line",
    )
    parser.add_argument(
        "--no-assert-even-inputs",
        action="store_true",
        help="Disable sanity-check that AAG inputs are exactly 2,4,6,...,2*I",
    )
    args = parser.parse_args()

    input_literals = parse_aag_inputs(
        args.aag,
        assert_even_inputs=not args.no_assert_even_inputs,
    )

    port_map = parse_cnf_port_map(args.cnf)
    if not port_map:
        raise ValueError(
            f"No 'c <aig_lit> -> <cnf_var>' port-mapping comments found in {args.cnf}"
        )

    missing = [lit for lit in input_literals if lit not in port_map]
    if missing:
        raise ValueError(
            f"Some AAG input literals are missing from the CNF port map: {missing}"
        )

    projection_vars = [port_map[lit] for lit in input_literals]

    processed_text = build_processed_cnf_text(
        args.cnf,
        projection_vars,
        one_show_per_line=not args.single_show_line,
    )
    args.output.write_text(processed_text)

    print(f"Wrote: {args.output}")
    print(f"AAG input literals: {input_literals}")
    print(f"Projection CNF vars: {projection_vars}")
    print(f"Show format: {'one variable per line' if not args.single_show_line else 'single combined line'}")


if __name__ == "__main__":
    main()
