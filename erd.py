import os
import django
import pygraphviz as pgv
from django.apps import apps

def generate_erd():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
    django.setup()

    graph = pgv.AGraph(strict=False, directed=True)
    graph.node_attr['shape'] = 'box'

    for model in apps.get_models():
        # Create a label with the model name and its fields
        label = f"{model._meta.object_name}\n"
        label += "\n".join(f"{field.name} ({field.get_internal_type()})" for field in model._meta.fields)

        graph.add_node(model._meta.object_name, label=label)

        for field in model._meta.fields + model._meta.many_to_many:
            if field.is_relation:
                target = field.related_model
                if target:
                    graph.add_edge(model._meta.object_name, target._meta.object_name, label=field.name)

    filename = 'erd.png'
    graph.draw(filename, prog='dot', format='png')
    print(f"ERD generated: {filename}")

if __name__ == '__main__':
    generate_erd()
