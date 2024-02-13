from src.modele.repository import connexionBaseDeDonnee


async def add_solo_rank(puuid: str, solo_rank: dict):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    if not solo_rank:
        solo_rank = {"tier": None, "rank": None, "LP": None }
    cursor.execute(
        "INSERT INTO SOLOQ (puuid, LP, rang, tier) VALUES (?, ?, ?, ?)",
        (puuid, solo_rank['LP'], solo_rank['rank'], solo_rank['tier'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Solo rank added for {puuid} to the database")


async def add_flex_rank(puuid: str, flex_rank: dict):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    if not flex_rank:
        flex_rank = {"tier": None, "rank": None, "LP": None }
    cursor.execute(
        "INSERT INTO FLEX (puuid, LP, rang, tier) VALUES (?, ?, ?, ?)",
        (puuid, flex_rank['LP'], flex_rank['rank'], flex_rank['tier'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Flex rank added {puuid} to the database")


async def update_solo_rank(puuid: str, solo_rank: dict):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE SOLOQ SET LP=?, rang=?, tier=? WHERE puuid=?",
        (solo_rank['LP'], solo_rank['rank'], solo_rank['tier'], puuid)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Solo rank updated for {puuid} to the database")


async def update_flex_rank(puuid: str, flex_rank: dict):
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE FLEX SET LP=?, rang=?, tier=? WHERE puuid=?",
        (flex_rank['LP'], flex_rank['rank'], flex_rank['tier'], puuid)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Flex rank updated for {puuid} to the database")


async def get_solo_rank(puuid: str) -> dict:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SOLOQ WHERE puuid=?", (puuid,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    # Change the key name to match the other functions
    result["rank"] = result["rang"]
    del result["rang"]
    return result


async def get_flex_rank(puuid: str) -> dict:
    conn = connexionBaseDeDonnee.connexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM FLEX WHERE puuid=?", (puuid,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    # Change the key name to match the other functions
    result["rank"] = result["rang"]
    del result["rang"]
    return result
