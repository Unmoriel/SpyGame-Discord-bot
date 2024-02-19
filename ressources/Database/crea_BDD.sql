#CREATE DATABASE lolcam;

CREATE TABLE JOUEURS(
   puuid VARCHAR(100),
   gameName_tagLine VARCHAR(50) NOT NULL,
   sumonerId VARCHAR(100),
   pseudo VARCHAR(50),
   dernier_match VARCHAR(50),
   loose_week INT,
   win_week INT,
   PRIMARY KEY(puuid),
   UNIQUE(gameName_tagLine)
);



CREATE TABLE SOLOQ(
   puuid VARCHAR(100),
   LP SMALLINT,
   rang VARCHAR(25),
   tier VARCHAR(25),
   PRIMARY KEY(puuid),
   FOREIGN KEY(puuid) REFERENCES JOUEURS(puuid) ON DELETE CASCADE
);

CREATE TABLE FLEX(
   puuid VARCHAR(100),
   LP SMALLINT,
   rang VARCHAR(25),
   tier VARCHAR(25),
   PRIMARY KEY(puuid),
   FOREIGN KEY(puuid) REFERENCES JOUEURS(puuid) ON DELETE CASCADE
);

CREATE TABLE SERVERSDISCORD(
   id_server BIGINT,
   name VARCHAR(100),
   recap_channel BIGINT,
   main_channel BIGINT,
   PRIMARY KEY(id_server)
);

CREATE TABLE WATCH(
   puuid VARCHAR(100),
   id_server BIGINT,
   PRIMARY KEY(puuid, id_server),
   FOREIGN KEY(puuid) REFERENCES JOUEURS(puuid) ON DELETE CASCADE,
   FOREIGN KEY(id_server) REFERENCES SERVERSDISCORD(id_server) ON DELETE CASCADE
);
