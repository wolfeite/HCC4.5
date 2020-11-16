import sys
import json
import os
import datetime
import random
import fitz
import subprocess

class Path():
    def __init__(self, dir=""):
        self.sep = os.sep
        self.set_path_root()
        self.dir = dir
    def set_path_root(self):
        pathArr = os.path.abspath(sys.argv[0]).split(self.sep)
        self.enter = pathArr.pop()
        self.root = self.sep.join(pathArr)
        self.frozen = getattr(sys, "frozen", False)
        print("Path对象路径分析：入口文件{0}，项目根路径{1}, frozen路径{{2}}".format(self.enter, self.root, self.frozen))

    def __getitem__(self, item):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, item)

    @property
    def dir(self):
        return self.path

    @dir.setter
    def dir(self, dirName):
        self.set_dir(dirName)

    def set_dir(self, dir, root=None):
        print("set_dir>>>", dir, isinstance(dir, (list, tuple)))
        self.path = self.merge(root or self.root, *dir) if isinstance(dir, (list, tuple)) else self.merge(
            root or self.root, dir)

    def merge(self, *args):
        print("merge>>>>>", args)
        return self.sep.join(args)

    @classmethod
    def join(cls, *args):
        # 注意加入self.sep将会重置路径
        return os.path.join(*args)

class File():
    def __init__(self, baseDir):
        self.path = Path(baseDir)

    @property
    def dir(self):
        return self.path.dir

    def size(self, fileName, byte=True):
        file = fileName
        if isinstance(file, (list, tuple)):
            file = self.path.join(*fileName)
        file_byte = os.path.getsize(self.path.join(self.dir, file))
        return file_byte if byte else self.sizeConvert(file_byte)

    @classmethod
    def sizeConvert(cls, size):  # 单位换算
        K, M, G = 1024, 1024 ** 2, 1024 ** 3  # Bytes
        if size >= G:
            return str(round(size / G, 3)) + 'GB'
        elif size >= M:
            return str(round(size / M, 3)) + 'MB'
        elif size >= K:
            return str(round(size / K, 3)) + 'KB'
        else:
            return str(round(size, 3)) + 'B'

    def file_path(self, fileName):
        url = os.path.join(self.dir, fileName)
        res = False
        if os.path.isfile(url):
            self.url = url
            res = url
        return res

    def readLines(self, fileName, encoding="utf-8", newline=False):
        url = self.file_path(fileName)
        if url:
            with open(url, "r", encoding=encoding, errors='ignore') as f:
                # res = f.readlines()#带有\n
                res = f.read().splitlines(newline)
            return res

    def read2json(self, fileName):
        url = self.file_path(fileName)
        if url:
            with open(url, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith(u'\ufeff'):
                    content = content.encode('utf8')[3:].decode('utf8')
                self.result = json.loads(content)
                return self.result

    def _wr(self, url=""):
        url = self.url if not url == "" else url
        if not self.result:
            return False
        print("开始写入文件", url)
        # with open(url, "w", encoding='utf-8',newline='\n') as f:
        with open(url, "w", encoding='utf-8') as f:
            json.dump(self.result, f, indent=4, ensure_ascii=False)

    def edit(self):
        if not self.result:
            return False
        self._wr(self.result)

    def write(self, fileName=""):
        if (not fileName):
            return False
        url = os.path.join(self.dir, fileName)
        self._wr(url)

    def named(self, type):
        type = type if type.startswith(".") else "." + type
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 999)) + type

    def up(self, request, input_name, dir="", size=0):
        if input_name in request.files:
            file = ""
            try:
                fi = request.files[input_name]
                filename = fi.filename
                if filename == '':
                    return ""
                ftype = '.' + filename.rsplit('.', 1)[1]
                file = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 999)) + ftype
                dir_Path = os.path.join(self.dir, dir)
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

    def up_img(self, request, input_name, dir, size=0, imgs=set(['png', 'jpg', "jpeg"])):
        filename = request.files[input_name].filename
        allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in imgs
        return self.up(request, input_name, dir, size) if allowed else False

    def pdf2img(self, fileName, src_dir, tar_dir=None):
        print("准备打开PDF文件", os.path.join(self.dir, src_dir, fileName))
        doc = fitz.open(os.path.join(self.dir, src_dir, fileName))  # 打开一个PDF文件，doc为Document类型，是一个包含每一页PDF文件的列表
        if not doc.isPDF:
            return False

        fileName = fileName.split(".")[0]
        out_path = self.outPath(src_dir, tar_dir)
        out_path_png = os.path.join(out_path, fileName)

        trans = fitz.Matrix(1, 1).preRotate(0)
        pm = doc[0].getPixmap(matrix=trans, alpha=False)
        tarHeight = 1080
        tarWidth = pm.width / pm.height * tarHeight
        zoom_x = tarWidth / pm.width
        zoom_y = tarHeight / pm.height
        # print("pm>..", pm.width, pm.height,tarWidth,tarHeight,zoom_x,zoom_y)

        rotate = int(0)  # 设置图片的旋转角度
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        # zoom_x = 1.33333333  # 设置图片相对于PDF文件在X轴上的缩放比例(1.33333333-->1056x816)   (2-->1584x1224)
        # zoom_y = 1.33333333  # 设置图片相对于PDF文件在Y轴上的缩放比例
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)  # 缩放系数1.3在每个维度  .preRotate(rotate)是执行一个旋转
        fileNames = []
        print("%s开始转换..." % src_dir)
        if doc.pageCount > 0:  # 获取PDF的页数
            for pg in range(doc.pageCount):
                page = doc[pg]  # 获得第pg页
                pm = page.getPixmap(matrix=trans, alpha=False)  # 将其转化为光栅文件（位数）
                str_path = "%s%s%s.png" % (out_path_png, "_", pg)  # 保证输出的文件名不变
                pm.writeImage(str_path)  # 将其输入为相应的图片格式，可以为位图，也可以为矢量图
                fileNames.append("%s%s%s.png" % (fileName, "_", pg))
                # 我本来想输出为jpg文件，但是在网页中都是png格式（即调用writePNG），再转换成别的图像文件前，最好查一下是否支持
        # else:
        #     page = doc[0]
        #     pm = page.getPixmap(matrix=trans, alpha=False)
        #     pm.writeImage("%s.png" % target)
        #     fileNames.append("%s.png" % page_prefix)
        print("转换至%s完成！" % out_path_png)
        return fileNames

    def remove(self, dir, fileName):
        path = os.path.join(self.dir, dir, fileName)
        os.path.exists(path) and os.remove(path)

    def removes(self, dir, arrs):
        for fileName in arrs:
            self.removeImg(dir, fileName)

    def outPath(self, src_dir, tar_dir):
        tar_dir = src_dir if not tar_dir else os.path.join(src_dir, tar_dir)
        path = os.path.join(self.dir, tar_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

class Office(File):
    def __init__(self, baseDir):
        super(Office, self).__init__(baseDir)

    # libreoffice 命令行方式 --- ubuntu环境下方案，注意win10环境下，打包需要开启后台窗口
    def ppt2pdf(self, fileName, src_dir, tar_dir=None, timeout=None):
        ppt_path = os.path.join(self.dir, src_dir, fileName)
        out_path = self.outPath(src_dir, tar_dir)
        name = "{0}{1}".format(fileName.rsplit('.')[0], ".pdf")
        # outPath_pdf = os.path.join(out_path, name)
        # args = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', out_path, ppt_path]
        args = ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', out_path, ppt_path]
        # subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, shell=True)
        subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        # re.search('-> (.*?) using filter', process.stdout.decode())
        return name

    # pywin32实现方式 --- win10环境下不希望打包后有命令框方案！
    # def ppt2pdf(self, fileName, src_dir, tar_dir=None):
    #     import win32com
    #     from win32com.client import Dispatch, constants, gencache, DispatchEx
    #     import pythoncom
    #
    #     ppt_path = os.path.join(self.dir, src_dir, fileName)
    #     out_path = self.outPath(src_dir, tar_dir)
    #     name = "{0}{1}".format(fileName.rsplit('.')[0], ".pdf")
    #     outPath_pdf = os.path.join(out_path, name)
    #     # outPath_png = os.path.join(out_path, "{0}{1}".format(name, ".png"))
    #
    #     pythoncom.CoInitialize()
    #     # gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
    #     p = Dispatch("PowerPoint.Application")
    #     ppt = p.Presentations.Open(ppt_path, False, False, False)
    #     res = ppt.ExportAsFixedFormat(outPath_pdf, 2, PrintRange=None)
    #     print('保存 PDF 文件：', outPath_pdf, res)
    #     ppt.Close()
    #     p.Quit()
    #     return name
    #
    # def ppt2img(self, fileName, src_dir, tar_dir=None):
    #     # import win32com
    #     # from win32com.client import Dispatch, constants, gencache, DispatchEx
    #     # import pythoncom
    #
    #     ppt_path = os.path.join(self.dir, src_dir, fileName)
    #     out_path = self.outPath(src_dir, tar_dir)
    #     name = fileName.rsplit('.')[0]
    #     # outPath_pdf = os.path.join(out_path, "{0}{1}".format(name, ".pdf"))
    #     outPath_png = os.path.join(out_path, "{0}{1}".format(name, ".png"))
    #
    #     pythoncom.CoInitialize()
    #     powerpoint = win32com.client.Dispatch('PowerPoint.Application')
    #     # powerpoint.Visible = True
    #     ppt = powerpoint.Presentations.Open(ppt_path)
    #     # 保存为图片
    #     res = ppt.SaveAs(outPath_png, 17)
    #     # 保存为pdf
    #     # res = ppt.SaveAs(outPath_pdf, 32)  # formatType = 32 for ppt to pdf
    #     # 关闭打开的ppt文件
    #     ppt.Close()
    #     # 关闭powerpoint软件
    #     powerpoint.Quit()

class Movie(File):
    def __init__(self, baseDir):
        super(Movie, self).__init__(baseDir)

    def time(self, fileName):
        # 问题在于打包时无法使用-w命令
        from moviepy.editor import VideoFileClip
        file = fileName
        if isinstance(file, (list, tuple)):
            file = self.path.join(*fileName)
        # clip = VideoFileClip(self.path.join(self.dir, file))
        # file_time = self.timeConvert(clip.duration)
        # return file_time

    @classmethod
    def timeConvert(cls, size):  # 单位换算
        M, H = 60, 60 ** 2
        if size < M:
            return str(size) + u'秒'
        if size < H:
            return u'%s分钟%s秒' % (int(size / M), int(size % M))
        else:
            hour = int(size / H)
            mine = int(size % H / M)
            second = int(size % H % M)
            tim_srt = u'%s小时%s分钟%s秒' % (hour, mine, second)
            return tim_srt
