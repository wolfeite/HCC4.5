from .File import File
import fitz
import os
class Pdf(File):
    def __init__(self, baseDir):
        super(Pdf, self).__init__(baseDir)

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
