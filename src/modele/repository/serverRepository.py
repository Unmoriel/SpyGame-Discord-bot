from src.modele.repository import connexionBaseDeDonnee


async def add_server(id_server: int):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO SERVERSDISCORD (id_server, recap_channel, main_channel) VALUES (?, ?, ?)",
        (id_server, None, None)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Server {id_server} added to the database")


async def delete_server(id_server: int):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM SERVERSDISCORD WHERE id_server=?",
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
        "UPDATE SERVERSDISCORD SET recap_channel=?, main_channel=? WHERE id_server=?",
        (recap_channel, main_channel, id_server)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Server {id_server} updated in the database")


async def get_server(id_server: int) -> dict:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SERVERSDISCORD WHERE id_server=?", (id_server,))
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


