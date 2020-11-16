# from flask import Blueprint, request, render_template, redirect, flash, current_app as app, make_response, abort
# import os, sys
# print(">>>>>>", __name__, __path__, __file__, __doc__, __package__, os.sep, sys.argv[0])
#
# # 1.定义蓝图
# web = Blueprint("web", __name__)
# # 2.为蓝图添加路由
# # from app.web import test_route
# test = __import__(__name__ + ".test_route", fromlist=('test_route'))
# test.add_route(web, request, make_response, render_template, redirect, app, flash)
# index = __import__(__name__ + ".index", fromlist="index")
# index.add_route(web, request, make_response, render_template, redirect, app, flash)
#
# # 2.table蓝图
# tableView = Blueprint("table", __name__, url_prefix="/table")
# __import__(__name__ + ".table", fromlist="table").add_route(tableView, request, make_response, render_template,
#                                                             redirect, app, flash)
#
# # 3.form蓝图
# formView = Blueprint("form", __name__, url_prefix="/form")
# __import__(__name__ + ".form", fromlist="form").add_route(formView, request, make_response, render_template, redirect,
#                                                           app, flash)
#
# bps = [web, tableView, formView]

# from libs.request import Params
# def requester(request):
#     with Params(request, ["name", "age", "sex"]) as res:
#         request.role = res
#         print(">>>>>requester:", request.path, request.role.params["name"], res)
# @web.before_app_request
# def auther():
#     print("web模块请求前置处理器》》》》")
#     requester(request)
#     pass
#
# @web.after_app_request
# def excp(res):
#     print("《《《《web模块请求结果处理器", res)
#     return res

# @tableView.before_app_request
# def auther2():
#     print("table模块请求前置处理器》》》》")
#     getParams(request)
#     pass
#
# @tableView.after_app_request
# def excp2(res):
#     print("《《《《table模块请求结果处理器", res)
#     return res
#
# @formView.before_app_request
# def auther3():
#     print("form模块请求前置处理器》》》》")
#     getParams(request)
#     pass
#
# @formView.after_app_request
# def excp3(res):
#     print("《《《《form模块请求结果处理器", res)
#     return res
