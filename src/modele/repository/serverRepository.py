from src.modele.repository import connexionBaseDeDonnee


async def add_server(id_server: int, name: str):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO SERVERSDISCORD (id_server, name, recap_channel, main_channel) VALUES (%s, %s, %s, %s)",
        (id_server, name, None, None)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Server {id_server} added to the database")


async def delete_server(id_server: int):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM SERVERSDISCORD WHERE id_server=%s",
        (id_server,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Server {id_server} deleted from the database")


async def update_server(id_server: str, recap_channel: int = None, main_channel: int = None):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE SERVERSDISCORD SET recap_channel=%s, main_channel=%s WHERE id_server=%s",
        (recap_channel, main_channel, id_server)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Server {id_server} updated in the database")


async def get_server(id_server: int) -> dict:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SERVERSDISCORD WHERE id_server=%s", (id_server,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return {}


async def get_all_servers():
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SERVERSDISCORD")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


