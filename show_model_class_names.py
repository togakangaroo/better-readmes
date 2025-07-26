# coding: utf-8
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

# Read the models.py file
with open('models.py', 'r') as f:
    source_code = f.read()

models_tree = parser.parse(bytes(source_code, 'utf8'))

# Query for all class definitions
query = Query(PY_LANGUAGE, """
(class_definition
  name: (identifier) @class.name
  superclasses: (argument_list)? @class.superclasses
  body: (block) @class.body) @class.definition
""")
query_cursor = QueryCursor(query)
models_captures = query_cursor.captures(models_tree.root_node)
model_class_names = [capture.text for capture in models_captures['class.name']]
import json
print(json.dumps([n.decode('utf-8') for n in model_class_names], indent=2))
