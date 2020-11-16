from .File import File
import os
from flask import request, make_response, send_from_directory
class Loader(File):
    def __init__(self, baseDir=""):
        super(Loader, self).__init__(baseDir)

    def up(self, input_name, dir="", size=0):
        if input_name in request.files:
            file = ""
            paths = dir if isinstance(dir, (list, tuple)) else [dir]
            try:
                fi = request.files[input_name]
                filename = fi.filename
                if filename == '':
                    return ""
                ftype = '.' + filename.rsplit('.', 1)[1]
                file = self.named(ftype)
                dir_Path = os.path.join(self.dir, *paths)
                if not os.path.exists(dir_Path):
                    os.makedirs(dir_Path)
                file_path = os.path.join(dir_Path, file)
                print(file_path)
                fi.save(file_path)
                fsize = os.stat(file_path).st_size
                if fsize > size * 1024 * 1024 and size != 0:
                    os.remove(file_path)
                    return ""

            except Exception as err:
                print(err)
                pass
            return file
        else:
            return ""

    def up_img(self, input_name, dir, size=0, imgs=set(['png', 'jpg', "jpeg"])):
        filename = request.files[input_name].filename
        allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in imgs
        return self.up(request, input_name, dir, size) if allowed else False

    def down(self, filename, dir="", outName=None):
        paths = dir if isinstance(dir, (list, tuple)) else [dir]
        dirpath = os.path.join(self.dir, *paths)
        print(">>>下载路径为：", dirpath, filename)
        # send_from_directory其他配置项：mimetype=mimetype,cache_timeout=30*60
        response = make_response(send_from_directory(dirpath, filename, as_attachment=True))
        # 处理中文名问题，不过尽量避免中文路径及文件名
        outName = outName if outName else filename
        response.headers["Content-Disposition"] = "attachment; filename={}".format(outName.encode().decode('latin-1'))
        # response.headers["Content-Disposition"] = "attachment; filename={}".format(dirpath.encode().decode('latin-1'))
        return response
