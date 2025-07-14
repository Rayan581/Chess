import pygame

pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self.sounds = {
            'move': pygame.mixer.Sound('assets/sounds/move.mp3'),
            'capture': pygame.mixer.Sound('assets/sounds/capture.mp3'),
            'check': pygame.mixer.Sound('assets/sounds/check.mp3'),
            'checkmate': pygame.mixer.Sound('assets/sounds/checkmate.mp3'),
            'castle': pygame.mixer.Sound('assets/sounds/castle.mp3'),
            'opening': pygame.mixer.Sound('assets/sounds/opening.mp3'),
            'stalemate': pygame.mixer.Sound('assets/sounds/stalemate.mp3'),
        }

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
