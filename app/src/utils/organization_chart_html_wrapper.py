import json
import dash_html_components as html
import dash_bootstrap_components as dbc
from utils.organization_chart import OrganizationChart, Entity


from anytree import LevelGroupOrderIter, PreOrderIter
from anytree.search import find as find_tree
from anytree.exporter import JsonExporter
from anytree.importer import JsonImporter
from anytree.importer import DictImporter


def load_oc_to_json(organization_chart):
    root = EntityHtmlWrapper(id="root", label="root")
    elements = {}
    elements["root"] = root
    for entity in PreOrderIter(organization_chart._root):
        if entity.id == "root":
            continue
        parent_id = entity.parent.id
        entity = EntityHtmlWrapper(
            **{k: v for k, v in entity.__dict__.items() if (("parent" not in k) and ("children" not in k))},
            expand=False,
        )
        # Only displaying first level elements

        entity.parent = elements[parent_id]

        if entity.parent.id == "root":
            entity.visible = True

        elements[entity.id] = entity
    return JsonExporter().export(root)


class EntityHtmlWrapper(Entity):
    def __init__(
        self,
        id,
        label,
        code_chorus=None,
        code_osfi=None,
        code_odrive=None,
        parent=None,
        activated=False,
        expand=False,
        valid=False,
        selected=False,
        visible=False,
    ):
        super().__init__(
            id=id,
            label=label,
            code_chorus=code_chorus,
            code_osfi=code_osfi,
            code_odrive=code_odrive,
            parent=parent,
            activated=activated,
        )
        self.expand = expand
        self.valid = valid
        self.selected = selected
        self.visible = visible

    def to_json(self):
        to_return_dict = {k: v for k, v in self.__dict__.items() if (("parent" not in k) and ("children" not in k))}
        to_return_dict["parent"] = self.parent.id
        return json.dumps(to_return_dict, encoding="utf-8")

    def to_html(self):
        class_name = "back_office_entity"
        if self.selected:
            class_name += " selected"

        if (self.expand == True) and self.children:
            expand_span = html.Div(
                id={"type": "back-office-entity-expand", "id": self.id},
                children=[html.Span(className="glyphicon glyphicon-menu-up"), html.P("Shrink")],
            )
        elif (self.expand == False) and self.children:
            expand_span = html.Div(
                id={"type": "back-office-entity-expand", "id": self.id},
                children=[html.Span(className="glyphicon glyphicon-menu-down"), html.P("Expand")],
            )
        else:
            expand_span = html.Div(id={"type": "back-office-entity-expand", "id": self.id}, children=[])
        return html.Div(
            id={"type": "back-office-entity", "id": self.id},
            children=[
                dbc.Row(
                    [
                        dbc.Col(expand_span, width={"size": 1}, className="mx-0"),
                        dbc.Col(html.P(" -- " * self.depth + self.label), width={"size": 3}),
                        dbc.Col([html.P("OSFI:\n"), html.P(self.code_osfi)], width=2),
                        dbc.Col([html.P("Odrive:\n"), html.P(self.code_odrive)], width=2),
                        dbc.Col([html.P("Chorus:\n"), html.P(self.code_chorus)], width=2),
                        dbc.Col(
                            dbc.FormGroup(
                                [
                                    dbc.Checkbox(
                                        id={"type": "back-office-entity-activated", "id": self.id},
                                        checked=self.activated,
                                    ),
                                    dbc.Label(
                                        "Active",
                                        html_for={"type": "back-office-entity-activated", "id": self.id},
                                        className="form-check-label",
                                    ),
                                ]
                            ),
                            width=1,
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Modifier",
                                id={"type": "back-office-entity-update-open-button", "id": self.id},
                                block=True,
                                style={"vertical-align": "middle"},
                                color="primary",
                            ),
                            width=1,
                            # className="mx-0",
                        ),
                    ]
                )
            ],
            className=class_name,
        )


class OrganizationChartHtmlWrapper:
    def __init__(self):
        self._root = None

    def get_html_elements(self):
        elements = []
        for entity in PreOrderIter(self._root):
            if entity.id == "root":
                continue
            if entity.visible:
                elements.append(entity.to_html())
        return elements

    def load_json(self, tree_json):
        dict_importer = DictImporter(nodecls=EntityHtmlWrapper)
        self._root = JsonImporter(dict_importer).import_(tree_json)

    def get_parent_options(self, entity_id=None) -> dict:
        options = []
        for entity in PreOrderIter(self._root):
            if entity.id == "root":
                options.append({"label": "Pas de parent", "value": entity.id})
            elif entity_id and (entity.id == entity_id):
                continue
            else:
                options.append({"label": entity.label, "value": entity.id})
        return options

    def to_json(self):
        return JsonExporter().export(self._root)

    def get_entity_by_id(self, id) -> Entity:
        return find_tree(self._root, lambda entity: entity.id == id)

    def toggle_select(self, id):
        for entity in PreOrderIter(self._root):
            if entity.id != id:
                entity.selected = False
        entity = self.get_entity_by_id(id)
        entity.selected = not entity.selected

    def toggle_activation(self, id):
        entity = self.get_entity_by_id(id)
        entity.activated = not entity.activated

    def toggle_expand(self, id):
        entity = self.get_entity_by_id(id)
        if entity.expand == False:
            entity.expand = True
            for child in entity.children:
                child.visible = True
        else:
            entity.expand = False
            for descendor in PreOrderIter(entity):
                if descendor.id == entity.id:
                    continue
                descendor.visible = False
                descendor.expand = False


if __name__ == "__main__":
    organization_chart = OrganizationChart("/data/entities_test_tree_2.tsv")
    och = OrganizationChartHtmlWrapper(organization_chart)

    tree_json = json.dumps(PreOrderIter(organization_chart._root), cls=OrganizationChartJsonEncoder)
    # oc = OrganizationChartJsonEncoder().from_json(tree_json)
