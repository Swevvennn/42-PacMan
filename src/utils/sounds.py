import os

import pygame


SOUND_DIR = os.path.join("assets", "sounds")

CH_MUSIC = 0
CH_GHOST = 1
CH_EFFECT = 2
CH_EAT = 3


class SoundManager:
    """Load every wav file in ``assets/sounds`` and dispatch them by event.

    The manager owns a handful of reserved pygame mixer channels so that
    long loops (siren, frightened mode) do not interrupt short effects
    (pacgum, fruit, ghost) and vice-versa.
    """

    def __init__(self) -> None:
        """Initialise the mixer and pre-load every sound file."""
        self.enabled: bool = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
        except pygame.error as e:
            print(f"sound: cannot init mixer ({e}), sounds disabled")
            self.enabled = False
            return

        self._dot_toggle: int = 0
        self._music_key: str | None = None
        self._load_all()

    def _load_all(self) -> None:
        """Load every ``.wav`` file from ``SOUND_DIR`` into memory."""
        if not os.path.isdir(SOUND_DIR):
            print(f"sound: directory {SOUND_DIR!r} not found, sounds disabled")
            self.enabled = False
            return
        for name in os.listdir(SOUND_DIR):
            if not name.lower().endswith(".wav"):
                continue
            path = os.path.join(SOUND_DIR, name)
            key = name[:-4]
            try:
                self.sounds[key] = pygame.mixer.Sound(path)
            except pygame.error as e:
                print(f"sound: cannot load {name} ({e})")

    def _play(self, key: str, channel_id: int, loops: int = 0,
              volume: float = 1.0) -> None:
        """Play ``key`` on ``channel_id``, ignoring errors silently."""
        if not self.enabled or key not in self.sounds:
            return
        try:
            channel = pygame.mixer.Channel(channel_id)
            channel.set_volume(volume)
            channel.play(self.sounds[key], loops=loops)
        except pygame.error:
            pass

    def _stop(self, channel_id: int) -> None:
        """Stop whatever is currently playing on ``channel_id``."""
        if not self.enabled:
            return
        try:
            pygame.mixer.Channel(channel_id).stop()
        except pygame.error:
            pass

    def play_start(self) -> None:
        """Play the level intro jingle."""
        self._play("start", CH_EFFECT, volume=0.7)

    def play_eat_dot(self) -> None:
        """Play an alternating chomp sound for a pacgum."""
        key = "eat_dot_0" if self._dot_toggle == 0 else "eat_dot_1"
        self._dot_toggle ^= 1
        self._play(key, CH_EAT, volume=0.6)

    def play_eat_super(self) -> None:
        """Play the chomp sound for a super-pacgum."""
        self._play("eat_dot_1", CH_EAT, volume=0.8)

    def play_eat_fruit(self) -> None:
        """Play the fruit pickup sound."""
        self._play("eat_fruit", CH_EFFECT, volume=0.8)

    def play_eat_ghost(self) -> None:
        """Play the ghost pickup sound."""
        self._play("eat_ghost", CH_EFFECT, volume=0.9)

    def play_death(self) -> None:
        """Play the death jingle and stop any background music."""
        self._stop(CH_MUSIC)
        self._stop(CH_GHOST)
        self._play("death_0", CH_EFFECT, volume=0.9)

    def play_extend(self) -> None:
        """Play the extra-life jingle."""
        self._play("extend", CH_EFFECT, volume=0.8)

    def start_siren(self) -> None:
        """Start the looping chase siren if it is not already playing."""
        if self._music_key == "siren0":
            return
        self._music_key = "siren0"
        self._play("siren0", CH_MUSIC, loops=-1, volume=0.4)

    def start_fright(self) -> None:
        """Switch the background loop to the frightened-mode music."""
        if self._music_key == "fright":
            return
        self._music_key = "fright"
        self._play("fright", CH_MUSIC, loops=-1, volume=0.5)

    def stop_music(self) -> None:
        """Stop every looping background sound."""
        self._music_key = None
        self._stop(CH_MUSIC)
        self._stop(CH_GHOST)

    def play_eyes(self) -> None:
        """Start the eaten-ghost-eyes loop on the dedicated channel."""
        try:
            channel = pygame.mixer.Channel(CH_GHOST)
            if channel.get_busy():
                return
        except pygame.error:
            return
        self._play("eyes", CH_GHOST, loops=-1, volume=0.4)

    def stop_eyes(self) -> None:
        """Stop the eaten-ghost-eyes loop."""
        self._stop(CH_GHOST)
