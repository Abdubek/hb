"""Deduplicate generated single-byte codec maps in build-time frozen bytecode.

Keep public dictionary contents and iteration order. Unknown generator layouts
are left alone; no codec modules or APIs are removed.
"""
import ast


def compact_codec_maps(tree):
    table = None
    table_index = -1
    identity_index = -1
    for index, node in enumerate(tree.body):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        name = node.targets[0]
        if not isinstance(name, ast.Name):
            continue
        if name.id == 'decoding_table':
            try:
                table = ast.literal_eval(node.value)
                table_index = index
            except (ValueError, TypeError):
                return tree, False
        if name.id == 'decoding_map' and ast.dump(node.value) == ast.dump(
            ast.parse('codecs.make_identity_dict(range(256))', mode='eval').body
        ):
            identity_index = index
    if not isinstance(table, str) or len(table) != 256:
        return tree, False
    encoding = {ord(c): i for i, c in enumerate(table) if ord(c) != 65534}
    decoding = {i: None if ord(c) == 65534 else ord(c) for i, c in enumerate(table)}
    changed = False
    for index, node in enumerate(tree.body):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == 'encoding_map' and index > table_index):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if isinstance(value, dict) and value == encoding and list(value) == sorted(value):
                expression = ('{key:value for key,value in sorted((ord(c),i) '
                              'for i,c in enumerate(decoding_table) if ord(c)!=65534)}')
                node.value = ast.copy_location(ast.parse(expression, mode='eval').body, node.value)
                changed = True
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if (identity_index >= 0 and index > identity_index
                    and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == 'decoding_map' and call.func.attr == 'update'
                    and len(call.args) == 1 and not call.keywords):
                try:
                    value = ast.literal_eval(call.args[0])
                except (ValueError, TypeError):
                    continue
                if isinstance(value, dict) and {**dict(enumerate(range(256))), **value} == decoding:
                    expression = ('{i:None if ord(c)==65534 else ord(c) for i,c in enumerate('
                                  + repr(table) + ') if ord(c)!=i}')
                    call.args[0] = ast.copy_location(ast.parse(expression, mode='eval').body, call.args[0])
                    changed = True
    return ast.fix_missing_locations(tree), changed
