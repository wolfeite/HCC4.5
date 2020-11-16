from .File import File
import pygame

class Mp3(File):
    def __init__(self, baseDir):
        super(Mp3, self).__init__(baseDir)

    def play(self, fileName):
        self.open(fileName) and pygame.mixer.music.play()

    def open(self, fileName):
        self.url = self.file_path(fileName)
        if self.url:
            pygame.mixer.init()
            self.track = pygame.mixer.music.load(self.url)
        else:
            print("{0}没有该音频文件".format(fileName))
        return self.url

    def write(self, fileName=""):
        pass

    def stop(self):
        self.url and pygame.mixer.music.stop()

    def fadeout(self, duration=50):
        self.url and pygame.mixer.music.fadeout(duration)

    def isBusy(self):
        return True if pygame.mixer.music.get_busy() == 1 else False
