from .File import File
import subprocess
import os

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

    def ppt2img(self):
        pass