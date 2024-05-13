import psycopg2

# Connexion à la base de données
conn = psycopg2.connect(
    dbname="sefas",
    user="sefas",
    password="sefas",
    host="localhost"  # ou l'adresse de votre serveur PostgreSQL
)


# Création d'un curseur pour exécuter des commandes SQL

def get_all_template_sql():
    cur = conn.cursor()

    # Exécution d'une commande SQL
    cur.execute(
        "select RES_DESC.ID from RES_DESC join RESTYP on "
        "RESTYP.ID=RES_DESC.RESTYP_PARENT where RESTYP.NAME  = 'Template'")

    # Récupération des résultats
    resultats = cur.fetchall()

    return resultats



def get_content(xml_id):
    cur = conn.cursor()

    # Exécution d'une commande SQL
    request = ("select RES_DESC.ID, RES_DESC.maxid_version,  RESTYP.NAME TYPE, RES_DESC.NAME from RES_DESC "
               "join RESTYP on RESTYP.ID=RES_DESC.RESTYP_PARENT where RES_DESC.MAXID_VERSION in "
               "(select RES_VERSION_PARENT from RES_VERSION_DEP join RES_DESC "
               "on RES_DESC.MAXID_VERSION=RES_VERSION_DEP.RES_VERSION_CHILD where RES_DESC.ID=%s) "
               "and RESTYP.NAME='Template'" % xml_id)
    cur.execute(request)

    # Récupération des résultats
    resultats = cur.fetchall()
    #for ligne in resultats:
    #    print(ligne)

    return len(resultats) or 0


