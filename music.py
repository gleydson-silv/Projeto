"""
Módulo para um player de música em linha de comando (CLI) usando Pygame e Curses.

Este módulo contém classes e funções para gerenciar uma biblioteca de músicas, reproduzir músicas,
e fornecer uma interface de usuário em terminal para controlar a reprodução.

Classes:
    Playable (ABC): Interface abstrata para classes que podem ser reproduzidas.
    Song: Representa uma música com nome e caminho.
    MusicLibrary: Gerencia a biblioteca de músicas, carregando músicas de um diretório.
    MusicPlayer: Controla a reprodução de músicas, implementando a interface Playable.

Funções:
    main(stdscr): Função principal que inicia a interface de terminal usando Curses.
"""

import os
import time
import pygame
import curses
from abc import ABC, abstractmethod


class Playable(ABC):
    """Interface para classes que podem ser reproduzidas."""
    
    @abstractmethod
    def play(self):
        """Reproduz a música."""
        pass

    @abstractmethod
    def pause(self):
        """Pausa a música."""
        pass

    @abstractmethod
    def stop(self):
        """Para a música."""
        pass


class Song:
    """Representa uma música.

    Atributos:
        name (str): Nome da música.
        path (str): Caminho do arquivo da música.
    """
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path


class MusicLibrary:
    """Gerencia a biblioteca de músicas.

    Atributos:
        music_dir (str): Diretório onde as músicas estão armazenadas.
        songs (list): Lista de objetos Song representando as músicas carregadas.

    Métodos:
        _load_songs(): Carrega músicas do diretório especificado.
        get_songs(): Retorna a lista de músicas carregadas.
    """
    def __init__(self, music_dir="music"):
        self.music_dir = music_dir
        self.songs = self._load_songs()

    def _load_songs(self):
        """
        Carrega músicas do diretório especificado.

        Se o diretório não existir, ele será criado.

        Retorna:
            list: Lista de objetos Song representando as músicas carregadas.
        """
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)

        songs = []
        for file in os.listdir(self.music_dir):
            if file.endswith(".mp3"):
                songs.append(Song(file, os.path.join(self.music_dir, file)))
        return songs

    def get_songs(self):
        """
        Retorna a lista de músicas carregadas.

        Retorna:
            list: Lista de objetos Song.
        """
        return self.songs


class MusicPlayer(Playable):
    """Controla a reprodução de músicas.

    Atributos:
        library (MusicLibrary): Instância de MusicLibrary para gerenciar a biblioteca de músicas.
        current_index (int): Índice da música atual na lista de reprodução.
        playing (bool): Indica se uma música está sendo reproduzida no momento.
        volume (float): Volume atual da reprodução (0.0 a 1.0).
        start_time (float): Tempo em que a música atual começou a tocar.
        elapsed_time (float): Tempo total decorrido desde o início da reprodução.

    Métodos:
        play(index=None): Reproduz a música no índice especificado.
        pause(): Pausa ou retoma a reprodução da música.
        stop(): Para a reprodução da música.
        next_song(): Avança para a próxima música na lista.
        previous_song(): Volta para a música anterior na lista.
        change_volume(increase=True): Ajusta o volume da reprodução.
        get_elapsed_time(): Retorna o tempo decorrido desde o início da reprodução.
        format_time(seconds): Formata o tempo em minutos e segundos.
    """
    def __init__(self):
        pygame.mixer.init()
        self.library = MusicLibrary()
        self.current_index = 0
        self.playing = False
        self.volume = 0.5
        self.start_time = None
        self.elapsed_time = 0

    def play(self, index=None):
        """
        Reproduz a música no índice especificado.

        Parâmetros:
            index (int, opcional): Índice da música a ser reproduzida. Se None, reproduz a música atual.
        """
        if index is not None:
            self.current_index = index

        if self.library.songs:
            song = self.library.songs[self.current_index]
            try:
                pygame.mixer.music.load(song.path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                self.start_time = time.time()
                self.playing = True
            except pygame.error as e:
                print(f"Erro ao carregar a música: {e}")

    def pause(self):
        """Pausa ou retoma a reprodução da música."""
        if self.playing:
            pygame.mixer.music.pause()
            self.elapsed_time += time.time() - self.start_time
            self.start_time = None
            self.playing = False
        else:
            pygame.mixer.music.unpause()
            self.start_time = time.time()
            self.playing = True

    def stop(self):
        """Para a reprodução da música."""
        pygame.mixer.music.stop()
        self.elapsed_time = 0
        self.start_time = None
        self.playing = False

    def next_song(self):
        """Avança para a próxima música na lista."""
        self.stop()
        self.current_index = (self.current_index + 1) % len(self.library.songs)
        self.play()

    def previous_song(self):
        """Volta para a música anterior na lista."""
        self.stop()
        self.current_index = (self.current_index - 1) % len(self.library.songs)
        self.play()

    def change_volume(self, increase=True):
        """
        Ajusta o volume da reprodução.

        Parâmetros:
            increase (bool): Se True, aumenta o volume. Se False, diminui o volume.
        """
        self.volume = min(1.0, self.volume + 0.1) if increase else max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)

    def get_elapsed_time(self):
        """
        Retorna o tempo decorrido desde o início da reprodução.

        Retorna:
            float: Tempo decorrido em segundos.
        """
        if self.start_time is None:
            return self.elapsed_time
        return self.elapsed_time + (time.time() - self.start_time if self.playing else 0)

    @staticmethod
    def format_time(seconds):
        """
        Formata o tempo em minutos e segundos.

        Parâmetros:
            seconds (float): Tempo em segundos.

        Retorna:
            str: Tempo formatado no formato MM:SS.
        """
        return time.strftime('%M:%S', time.gmtime(seconds))


def main(stdscr):
    """
    Função principal que inicia a interface de terminal usando Curses.

    Parâmetros:
        stdscr: Objeto de tela do Curses para manipulação da interface.
    """
    player = MusicPlayer()

    if not player.library.songs:
        stdscr.addstr(0, 0, "Nenhuma música encontrada! Adicione arquivos MP3 na pasta 'music'.")
        stdscr.refresh()
        time.sleep(3)
        return

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    
    index = 0
    player.play(index)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 2, "🎵 CLI Music Player 🎵", curses.A_BOLD)
        stdscr.addstr(2, 2, "Use ↑/↓ para navegar | Enter para tocar | Espaço para pausar | q para sair")

        # Lista de músicas
        for i, song in enumerate(player.library.get_songs()):
            if i == index:
                stdscr.addstr(4 + i, 2, f"> {song.name}", curses.A_REVERSE)
            else:
                stdscr.addstr(4 + i, 2, f"  {song.name}")

        # Informações do player
        elapsed = player.format_time(player.get_elapsed_time())
        stdscr.addstr(15, 2, f"Status: {'▶ Tocando' if player.playing else '⏸ Pausado'}")
        stdscr.addstr(16, 2, f"Volume: {'█' * int(player.volume * 10)}")
        stdscr.addstr(17, 2, f"Tempo: {elapsed}")

        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('q'):
            player.stop()
            break
        elif key == curses.KEY_UP and index > 0:
            index -= 1
        elif key == curses.KEY_DOWN and index < len(player.library.songs) - 1:
            index += 1
        elif key == ord('\n'):  # Enter
            player.play(index)
        elif key == ord(' '):  # Espaço
            player.pause()
        elif key == ord('+'):
            player.change_volume(True)
        elif key == ord('-'):
            player.change_volume(False)
        elif key == curses.KEY_RIGHT: # >
            player.next_song()
        elif key == curses.KEY_LEFT: # <
            player.previous_song()


if __name__ == "__main__":
    curses.wrapper(main)