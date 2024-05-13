import xml.etree.ElementTree as ET
import json
import os
from pymongo import MongoClient


repository_referentiel = "/home/abdou/Téléchargements/job_stream/archive_repository_20240412_204712/opwd/default/common/template"


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


def check_if_is_template(xml_str):
    if xml_str and xml_str.startswith("<repository:Template ") or "<repository:Template" in xml_str:
        return 1
    return 0


def parse_element(element):
    result = {
        "tag": element.tag.split("}")[1] if "}" in element.tag else element.tag,
        # Supprime la partie namespace de la balise
        "attributes": dict(element.attrib),
        "children": [parse_element(child) for child in element]
    }
    return result


def child_printer(node, dict_json, list_id, parent=""):
    if 'tag' in node:
        key_node = node['tag'].replace('repository_', 'External')
        # if "repository_" in parent and "External" not in key_node:
        # key_node = "External" + key_node
        if key_node in dict_json:
            dict_json[key_node] += 1
        else:
            dict_json[key_node] = 1
        if parent:
            parent += "-->" + node['tag']
        else:
            parent += node['tag']
        if 'attributes' in node and 'resdescid' in node['attributes']:
            id_object = node['attributes']['resdescid']
            parent = id_object + " " + parent
            list_id.append(id_object)

        # print(parent)
        if 'children' in node:
            for child in node['children']:
                child_printer(child, dict_json, list_id, parent)


def scan_xml_file(xml_file, dict_json, list_id):
    # Lit le contenu du fichier XML
    try:
        with open(xml_file, "r", encoding="ISO-8859-1") as file:
            xml_content = file.read()
    except:
        return False
    if not check_if_is_template(xml_content):
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
        result_json = json.dumps(parse_element(root), indent=30)

        template = json.loads(result_json)

        dict_json['id'] = int(get_xml_id(xml_file))
        dict_json['name'] = template['attributes']['name']

        for child in template['children'][0]['children']:
            child_printer(child, dict_json, list_id)
    except:
        return False


# scan_xml_file(xml_file_path, dict_all_content, list_id_used)
# scan_xml_file(xml_file_path2, dict_all_content, list_id_used)
xml_ids = []
list_id_used = []
ref_content = []
files = sorted(os.listdir(repository_referentiel))
# Calculate the total number of files in the directory
total_files = len(files)

# Define the size of the chunk for loading
chunk_size = total_files // 20  # 5% of 100 chunks
print("%s Files Found" % total_files)
# Initialize the counter for files read
files_read = 0
# Boucler sur tous les fichiers du répertoire
for xml_path in files:
    dict_all_content = {}
    xml_total_path = os.path.join(repository_referentiel, xml_path)
    xml_id = get_xml_id(xml_total_path)
    xml_ids.append(xml_id)
    if os.path.isfile(xml_total_path):
        scan_xml_file(xml_total_path, dict_all_content, list_id_used)
        if dict_all_content:
            ref_content.append(dict_all_content)

    files_read += 1

    # Check if we need to print a loading message
    if files_read % chunk_size == 0:
        percentage = (files_read / total_files) * 100
        print(f"Loading: {int(percentage)} %")

# Chemin du fichier dans lequel enregistrer le tableau
fich_content = "referentiel_info.json"
id_used = "xml_id_used.json"

# Enregistrer le tableau dans le fichier
with open(fich_content, 'w') as fichier:
    json.dump(ref_content, fichier)

# Enregistrer le tableau dans le fichier
with open(id_used, 'w') as fic2:
    json.dump(list_id_used, fic2)

# Étape 1: Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Étape 2: Création de la base de données et de la collection
#db = client['scan_referentiel']
#collection = db['referentiel_16_04']

#collection.insert_many(ref_content)

#

# get_unused_id(xml_ids, list_id_used)
print("Tableau enregistré avec succès dans le fichier")
# print(ref_content)
# print(list_id_used)
