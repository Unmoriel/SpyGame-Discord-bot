from . import connexionBaseDeDonnee
from . import rankRepository


async def get_player_by_puuid(puuid_player: str) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM JOUEURS WHERE puuid=?", (puuid_player,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


async def get_players_by_server(id_server: str) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM JOUEUR j JOIN WATCH w ON w.puuid = j.puuid WHERE id_server=?", (id_server,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    print(result)
    return result


async def add_player(puuid: str,
               sumonerId: str,
               pseudo: str,
               dernier_match: str,
               loose_week: int,
               win_week: int,
               rank_flex: dict,
               rank_solo: dict):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO
        JOUEURS (
            puuid, 
            sumonerId,
            pseudo,
            dernier_match,
            loose_week,
            win_week) 
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (puuid, sumonerId, pseudo, dernier_match, loose_week, win_week)
    )
    conn.commit()

    rankRepository.add_solo_rank(puuid, rank_solo)
    rankRepository.add_flex_rank(puuid, rank_flex)
    cursor.close()
    conn.close()

    print("Player added to the database")