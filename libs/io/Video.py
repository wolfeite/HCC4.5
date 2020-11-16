from .File import File

class Video(File):
    def __init__(self, baseDir):
        super(Video, self).__init__(baseDir)

    def time(self, fileName):
        # 问题在于打包时无法使用-w命令
        from moviepy.editor import VideoFileClip
        file = fileName
        if isinstance(file, (list, tuple)):
            file = self.path.join(*fileName)
        # clip = VideoFileClip(self.path.join(self.dir, file))
        # file_time = self.timeConvert(clip.duration)
        # return file_time
