import xml.etree.ElementTree as ET
import json
import os

from ultimate_scan import get_content, get_all_template_sql

repository_referentiel = "/Users/abdoundao/Downloads/template/"


def get_xml_id(xml_file_path):
    xml_file = xml_file_path.split("/")[-1]  # Récupère le nom du fichier (122285.xml)
    xml_id = xml_file.split(".")[0]  # Récupère le nombre en retirant l'extension .xml
    return xml_id


def parse_element(element):
    result = {
        "tag": element.tag.split("}")[1] if "}" in element.tag else element.tag,
        # Supprime la partie namespace de la balise
        "attributes": dict(element.attrib),
        "children": [parse_element(child) for child in element]
    }
    return result


def print_tree_decalage(tree):
    decal = ""
    for i in range(tree - 1):
        decal += "          "
    return decal


def child_printer(node, tree):
    if 'tag' in node:
        id_object = ""
        node['is_external'] = False
        if 'repository_' in node['tag']:
            node['is_external'] = True
        node['used_time'] = 1

        if 'attributes' in node and 'resdescid' in node['attributes']:
            node['resdescid'] = node['attributes']['resdescid']
            node['used_time'] = get_content(node['attributes']['resdescid'])
        node.pop('attributes')
        if 'children' in node:
            children = node['children'].copy()
            node.pop('children')
            # Enlever et remettre children comme cela il sera en bas du référentiel
            node['children'] = children
            tree += 1
            for child in node['children']:
                child_printer(child, tree)


def scan_xml_file(xml_file):
    dict_file = {}

    # Lit le contenu du fichier XML
    try:
        with open(xml_file, "r", encoding="ISO-8859-1") as file:
            xml_content = file.read()
    except:
        print("Fichier %s Non trouvé" % xml_file)
        return False

    # Corrige le problème de namespace
    try:
        xml_content_fixed = xml_content.replace('<repository:', '<repository_').replace('</repository:',
                                                                                        '</repository_')
        xml_content_fixed = xml_content_fixed.replace('<TemplateClass:', '<TemplateClass_').replace('</TemplateClass:',
                                                                                                    '</TemplateClass_')
        xml_content_fixed = xml_content_fixed.replace(':', '_')
        # Parse le XML
        root = ET.fromstring(xml_content_fixed)
        result_json = json.dumps(parse_element(root), indent=100)

        template = json.loads(result_json)

        for child in template['children'][0]['children']:
            tree = 1
            child_printer(child, tree)
    except:
        return False
    return template


for template in get_all_template_sql():
    path = "%s%s.xml" % (repository_referentiel, template[0])
    print("####################Analyse %s #########################" % path)
    template = scan_xml_file(path)
    xml_id = get_xml_id(path)
    fich_content = "without_detail_json/referentiel_info_detail_%s.json" % xml_id

    # Enregistrer le tableau dans le fichier
    with open(fich_content, 'w') as fichier:
        json.dump(template, fichier)
