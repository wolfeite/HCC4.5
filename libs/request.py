class Params():
    def __init__(self, request, params=[]):
        self.isGet = True if request.method == "GET" else False
        self.request = request
        self.paramList = params
        self.result = {"data": [], "success": True, "mes": "", "error": False}

    def __enter__(self):
        self.method = self.request.args if self.isGet else self.request.form
        # self.params = self.map()
        self.params = self.dictList()
        # if not self.isGet:
        #     for i in range(len(self.params)):
        #         val = self.params[i]
        #         if val == None:
        #             self.params[i]=self.request.args.get(self.paramList[i])
        print("最后结果为>>>>：", self.params, len(list(self.params)), self.dictList())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print("报错》》", exc_type, exc_val, exc_tb)
            self.result["success"] = False
            self.result["mes"] = "异常:{}".format(exc_type)
            self.result["error"] = "信息:{},栈信息:{}".format(exc_val, exc_tb)
        return True

    def map(self):
        return list(map(self.value, self.paramList))

    def dictList(self):
        dicts = {}
        for key in self.paramList:
            dicts[str(key)] = self.value(key)
        return dicts

    def value(self, val):
        param = self.method.get(val)
        return self.request.args.get(val) if param == None and not self.isGet else param
    def mix(self,f = False):
        params = self.params
        type(f)=="function" and f(params)
