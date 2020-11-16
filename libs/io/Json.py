from .File import File
import json

class Json(File):
    def __init__(self, baseDir):
        super(Json, self).__init__(baseDir)

    def open(self, fileName):
        url = self.file_path(fileName)
        if url:
            with open(url, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith(u'\ufeff'):
                    content = content.encode('utf8')[3:].decode('utf8')
                self.result = json.loads(content)
                return self.result

    def write(self, fileName="", result=None, type="w", encoding="utf-8", **kwargs):
        url = self.file_path(fileName)
        if url and result:
            # with open(url, "w", encoding='utf-8',newline='\n') as f:
            with open(url, type, encoding=encoding, **kwargs) as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
