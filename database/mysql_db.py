import mysql.connector
from config import MYSQL_CONFIG

from mysql.connector import Error


def get_connection():
    return mysql.connector.connect(
        host=MYSQL_CONFIG["host"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"]
    )

def inserer_patrimoine(p):
    conn = None
    cursor = None
    try:
        conn = get_connection()  # ta fonction de connexion
        cursor = conn.cursor()

        sql = """
        INSERT INTO patrimoine(nom_patrimoine, latitude, longitude, id_user)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (p.nom, p.latitude, p.longitude, p.id_user))

        conn.commit()
        return True

    except mysql.connector.errors.IntegrityError as e:
        # Doublon sur UNIQUE(latitude, longitude)
        return False


    except Error as e:
        # autre erreur
        print("Erreur insertion patrimoine:", e)
        return False

    finally:
        if cursor: cursor.close()
        if conn: conn.close()



def recuperer_patrimoines():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        p.nom_patrimoine ,
        p.latitude,
        p.longitude,
        u.nom_utilisateur
    FROM patrimoine p
    JOIN utilisateur u ON p.id_user = u.id_user
    """

    cursor.execute(sql)
    resultats = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultats

def inserer_utilisateur(utilisateur):
    """
    Insère un nouvel utilisateur dans la base de données.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO utilisateur (nom_utilisateur, mot_de_passe)
    VALUES (%s, %s)
    """
    values = (
        utilisateur.nom_utilisateur,
        utilisateur.mot_de_passe
    )

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

def get_utilisateur(nom_utilisateur, mot_de_passe):
    """
    Récupère un utilisateur à partir de son nom et mot de passe.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT * FROM utilisateur
    WHERE nom_utilisateur = %s AND mot_de_passe = %s
    """
    cursor.execute(sql, (nom_utilisateur, mot_de_passe))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

def recuperer_patrimoines_par_user(id_user):
    """
    Récupère les patrimoines d'un utilisateur donné.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT 
        p.nom_patrimoine,
        p.latitude,
        p.longitude,
        u.nom_utilisateur
    FROM patrimoine p
    JOIN utilisateur u ON p.id_user = u.id_user
    WHERE p.id_user = %s
    """

    cursor.execute(sql, (id_user,))
    resultats = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultats
