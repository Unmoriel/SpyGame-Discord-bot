import mariadb
from src.configuration import conf


def connexion():
    '''
        Fonction qui permet de se connecter à la base de donnée
        Switch between the two following lines to use the conf.json file or the conf.py file
    '''
    # ids = conf.get_conf_file()
    ids = conf.get_bdd_conf()
    try:
        conn = mariadb.connect(
            user=ids['user'],
            password=ids['password'],
            host=ids['host'],
            database=ids['database']
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        exit(e)


def delete_all_data():
    """
        Fonction qui permet de supprimer toutes les données de la base de donnée
    """
    print("Are you sure (y/n) ?")
    if input() != "y":
        print("Aborted")
        return
    conn = connexion()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE SOLOQ")
    cursor.execute("TRUNCATE TABLE FLEX")
    cursor.execute("TRUNCATE TABLE SERVERSDISCORD")
    cursor.execute("TRUNCATE TABLE WATCH")
    cursor.execute("TRUNCATE TABLE JOUEURS")
    cursor.close()
    conn.close()
    print("All data deleted from the database")

