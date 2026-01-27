#!/usr/bin/env python3
"""Boolean operations: union, difference, intersection."""

import argparse
import json
import sys
from rhino_client import RhinoClient


def boolean_operation(operation: str, object_ids: list, delete_input: bool = True) -> dict:
    """Perform a boolean operation on objects.
    
    Args:
        operation: One of 'union', 'difference', 'intersection'
        object_ids: List of object GUIDs (first is base for difference)
        delete_input: Whether to delete input objects
    """
    params = {
        "operation": operation.lower(),
        "object_ids": object_ids,
        "delete_input": delete_input
    }
    
    with RhinoClient() as client:
        return client.send_command("boolean_operation", params)


def union(object_ids: list, delete_input: bool = True) -> dict:
    """Boolean union of objects."""
    return boolean_operation("union", object_ids, delete_input)


def difference(base_id: str, cutter_ids: list, delete_input: bool = True) -> dict:
    """Boolean difference: subtract cutters from base."""
    return boolean_operation("difference", [base_id] + cutter_ids, delete_input)


def intersection(object_ids: list, delete_input: bool = True) -> dict:
    """Boolean intersection of objects."""
    return boolean_operation("intersection", object_ids, delete_input)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Boolean operations')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Union
    union_p = subparsers.add_parser('union', help='Boolean union')
    union_p.add_argument('ids', nargs='+', help='Object GUIDs to union')
    union_p.add_argument('--keep', action='store_true', help='Keep input objects')
    
    # Difference
    diff_p = subparsers.add_parser('difference', help='Boolean difference')
    diff_p.add_argument('base', help='Base object GUID')
    diff_p.add_argument('cutters', nargs='+', help='Cutter object GUIDs')
    diff_p.add_argument('--keep', action='store_true', help='Keep input objects')
    
    # Intersection
    inter_p = subparsers.add_parser('intersection', help='Boolean intersection')
    inter_p.add_argument('ids', nargs='+', help='Object GUIDs to intersect')
    inter_p.add_argument('--keep', action='store_true', help='Keep input objects')
    
    args = parser.parse_args()
    
    if args.action == 'union':
        result = union(args.ids, delete_input=not args.keep)
    elif args.action == 'difference':
        result = difference(args.base, args.cutters, delete_input=not args.keep)
    elif args.action == 'intersection':
        result = intersection(args.ids, delete_input=not args.keep)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, indent=2))
