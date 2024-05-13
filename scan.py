import xml.etree.ElementTree as ET
import json
import os

from scooter_referentiel.ultimate_scan import get_content

repository_referentiel = "/home/abdou/Téléchargements/job_stream/archive_repository_20240412_204712/opwd/default/common/template/"

path = repository_referentiel + "1097079.xml"


def get_xml_id(xml_file_path):
    xml_file = xml_file_path.split("/")[-1]  # Récupère le nom du fichier (122285.xml)
    xml_id = xml_file.split(".")[0]  # Récupère le nombre en retirant l'extension .xml
    return xml_id


def get_unused_id(all_id, used_id):
    unused_ids = []
    # Parcourir les valeurs du dictionnaire A
    for content in all_id:
        # Vérifier si la valeur est présente dans le dictionnaire B
        if content not in used_id:
            unused_ids.append(content)
    unused_percentage = len(unused_ids) / (len(all_id) or 1) * 100
    print(" %s %% du référentiel n'est pas utilisé, la liste est définie dans unused_id.json/" % unused_percentage)
    id_unused = "unused_ids.json"
    # Enregistrer le tableau dans le fichier
    with open(id_unused, 'w') as fic3:
        json.dump(unused_ids, fic3)
    return unused_ids


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
    for i in range(tree-1):
        decal += "          "
    return decal


def child_printer(node, tree, dict_file):
    if 'tag' in node:
        id_object = ""
        key_node = node['tag'].replace('repository_', 'External')
        used_time = 1
        if 'attributes' in node and 'resdescid' in node['attributes']:
            print(node['attributes'])
            id_object = node['attributes']['resdescid']
            used_time = get_content(id_object)
        print(print_tree_decalage(tree), id_object, key_node, used_time)
        if 'children' in node:
            tree += 1
            for child in node['children']:
                 child_printer(child, tree, dict_file)


def scan_xml_file(xml_file):
    dict_file = {}

    # Lit le contenu du fichier XML
    try:
        with open(xml_file, "r", encoding="ISO-8859-1") as file:
            xml_content = file.read()
    except:
        # print("Fichier %s Non trouvé" % xml_file)
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
            child_printer(child, tree, dict_file)
    except:
        return False


scan_xml_file(path)


