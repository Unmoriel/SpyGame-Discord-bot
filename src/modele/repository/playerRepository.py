from src.modele.repository import connexionBaseDeDonnee
from src.modele.repository import rankRepository

async def get_all_player() -> list:
    """
    Get all the players
    """
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT DISTINCT * FROM JOUEURS"
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

async def get_all_players_watch() -> list:
    """
    Get all the players in the watch list
    """
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT DISTINCT * FROM JOUEURS"
        " WHERE puuid IN (SELECT puuid FROM WATCH)")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


async def get_player_by_game_name_tag_line(game_name_tag_line: str) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM JOUEURS WHERE gameName_tagLine=%s", (game_name_tag_line,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


async def get_player_by_puuid(puuid_player: str) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM JOUEURS WHERE puuid=%s", (puuid_player,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


async def get_players_by_server(id_server: str) -> list:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM JOUEUR j JOIN WATCH w ON w.puuid = j.puuid WHERE id_server=%s", (id_server,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    print(result)
    return result


async def add_player(puuid: str,
                     sumonerId: str,
                     game_name_tag_line: str,
                     pseudo: str,
                     dernier_match: str,
                     loose_week: int,
                     win_week: int,
                     rank_flex: dict,
                     rank_solo: dict):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO JOUEURS (
            puuid, 
            gameName_tagLine,
            sumonerId,
            pseudo,
            dernier_match,
            loose_week,
            win_week) 
            VALUES(%s, %s, %s, %s, %s, %s, %s)
        """,
        (puuid, game_name_tag_line, sumonerId, pseudo, dernier_match, loose_week, win_week)
    )
    conn.commit()

    await rankRepository.add_solo_rank(puuid, rank_solo)
    await rankRepository.add_flex_rank(puuid, rank_flex)
    cursor.close()
    conn.close()
    print(f"Player {game_name_tag_line} added to the database")


async def update_player_last_match(puuid: str, last_match: str):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE JOUEURS SET dernier_match=%s WHERE puuid=%s", (last_match, puuid)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Player {puuid} last match updated in the database")


async def increment_player_week(puuid: str, win: bool):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    temp = "win_week = win_week + 1" if win else "loose_week = loose_week + 1"
    cursor.execute(
        f"UPDATE JOUEURS SET {temp} WHERE puuid=%s", (puuid,)
    )
    conn.commit()
    cursor.close()
    conn.close()


async def reset_player_week(puuid: str):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE JOUEURS SET win_week=0, loose_week=0 WHERE puuid=%s", (puuid,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Player {puuid} week reset in the database")
