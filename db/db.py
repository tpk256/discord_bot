import sqlite3


def create_tables():
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Playlist (
        id  INTEGER PRIMARY KEY
        channel_id INTEGER,
        name_playlist TEXT NOT NULL,
        playlist_id INTEGER UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Song (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        ref_playlist INTEGER,
        FOREIGN KEY (ref_playlist) REFERENCES Playlist (playlist_id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()


def add_playlist(channel_id, name_playlist, playlist_id):
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Playlist (channel_id, name_playlist, playlist_id) VALUES (?, ?, ?)",
                       (channel_id, name_playlist, playlist_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()


def add_song(url, ref_playlist):
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Song (url, ref_playlist) VALUES (?, ?)", (url, ref_playlist))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()


def get_playlists(channel_id):
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Playlist WHERE channel_id = ?", (channel_id,))
    playlists = cursor.fetchall()
    conn.close()
    return playlists


def get_songs_by_playlist(playlist_id):
    conn = sqlite3.connect("music.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Song WHERE ref_playlist = ?", (playlist_id,))
    songs = cursor.fetchall()
    conn.close()
    for song in songs:
        yield song


if __name__ == "__main__":
    create_tables()
    # add_playlist(1, "Rock Classics", 101)
    # add_song("https://example.com/song1", 101)
