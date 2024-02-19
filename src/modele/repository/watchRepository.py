from src.modele.repository import connexionBaseDeDonnee


async def add_player_watch(puuid: str, id_server: int):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO WATCH (puuid, id_server) VALUES (%s, %s)", (puuid, id_server)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Player {puuid} added to the watch list")


async def delete_player_watch(puuid: str, id_server: int):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM WATCH WHERE puuid=%s AND id_server=%s", (puuid, id_server)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Player {puuid} deleted from the watch list")


async def get_players_by_server(id_server: int) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM JOUEURS j JOIN WATCH w ON w.puuid = j.puuid WHERE id_server=%s", (id_server,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


async def get_server_by_player(puuid: str) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_server FROM WATCH WHERE puuid=%s", (puuid,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


async def player_watch(puuid: str, id_server: int) -> bool:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM WATCH WHERE puuid=%s AND id_server=%s", (puuid, id_server)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result != []

