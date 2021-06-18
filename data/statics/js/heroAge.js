+function ($) {
    var spinner = new Spinner();
    $.extend({
        cookie: {
            set: function (cname, cvalue, exdays) {
                var str = cname + "=" + cvalue + ";"
                if (exdays) {
                    var d = new Date();
                    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
                    var expires = "expires=" + d.toUTCString();
                    str = str + expires
                }
                str = str + ";path=/";
                document.cookie = str;
                //document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
                //即document.cookie= name+"="+value+";path=/";  时间默认为当前会话可以不要，但路径要填写，因为JS的默认路径是当前页，如果不填，此cookie只在当前页面生效！
            },
            get: function (name) {
                var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)"); //匹配字段
                if (arr = document.cookie.match(reg)) {
                    return unescape(arr[2]);
                } else {
                    return null;
                }
            },
            check: function () {
                var user = getCookie("username");
                if (user != "") {
                    alert("Welcome again " + user);
                } else {
                    user = prompt("Please enter your name:", "");
                    if (user != "" && user != null) {
                        setCookie("username", user, 365);
                    }
                }
            },
            delete: function (name) {
                /**
                 * 清除指定cookie值
                 * */
                var exp = new Date();
                exp.setTime(exp.getTime() - 1);
                var cval = setCookie(name);
                if (cval && cval != null) {
                    document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString()
                }
            },
            clear: function () {
                /**
                 * 清除全部cookie值
                 * */
                var keys = document.cookie.match(/[^ =;]+(?=\=)/g);
                if (keys) {
                    for (var i = keys.length; i--;) {
                        // document.cookie = keys[i] +'=0;expires=' + new Date( 0).toUTCString()
                        document.cookie = keys[i] + '=0;expires=' + new Date(0).toUTCString() + ";path=/" + ";domain=localhost";
                    }
                }
            }
        },
        request: function (config, resolve, reject) {
            var con = $.extend({
                type: "get", dataType: "json", url: "#", tip: false
            }, config)
            spinner.spin(document.body);
            toastr.clear()
            var xhr = $.ajax(con).done(function (response) {
                var info = response.msg || '数据加载成功!'
                console.log("同步结果：", info, response)
                if (con.tip) {
                    response.success ? toastr.success(info) : toastr.error(info)
                }
                resolve && resolve(response)
            }).fail(function (e) {
                reject && reject(e)
                var info = e.msg || '数据加载失败!'
                con.tip && toastr.error(info)
                //alert('数据加载失败!');
            }).always(function (e) {
                spinner.stop();
            })
            return xhr
        },
        getQueryParam: function (name) {
            //获取地址栏的查询参数
            var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
            var r = window.location.search.substr(1).match(reg);
            if (r != null) return unescape(r[2]);
            return null;
        },
        parseUrl: function () {
            //获取当前网址，如： http://localhost:8083/uimcardprj/share/meun.jsp
            var curWwwPath = window.document.location.href;
            //获取主机地址之后的目录，如： uimcardprj/share/meun.jsp
            var pathName = window.document.location.pathname;
            var pos = curWwwPath.indexOf(pathName);
            //获取主机地址，如： http://localhost:8083
            var localhostPath = curWwwPath.substring(0, pos);
            //获取带"/"的项目名，如：/uimcardprj
            var projectName = pathName.substring(0, pathName.substr(1).indexOf('/') + 1);
            return [localhostPath, pathName, projectName];
        },
        alertInfo: function (info, el, type, expire = 2000) {
            var style = type === 'error' ? 'alert-danger' : 'alert-success';
            var str = '<div id="alert" class="alert ' + style + ' fade show" role="alert">' + info + '</div>'
            var el = el || document.body
            $(el).prepend(str);
            setTimeout(() => {
                $('#alert').alert('close');
            }, expire);
        },
        url_for: function () {
            var $body = $("body")
            return function (path) {
                var url_for = $body.attr("url_for");
                return url_for + path
            }
        }(),
        pattern: function () {
            return $("body").attr("pattern");
        },
        str2json: function (str) {
            if (str == "" || str == " " || str == null || $.type(str) === "number") {
                //Number("") 为0
                return str
            }
            let isNum = isNaN(Number(str)) ? false : str.startsWith("0") && str !== "0" ? false : true;
            let isStr = !isNum && !((str.startsWith("{") && str.endsWith("}")) || (str.startsWith("[") && str.endsWith("]")))
            if (isStr) {
                return str
            }
            var res = ""
            try {
                res = eval('(' + str + ')');
            } catch (error) {
                res = str
                console.log("Cannot eval JSON: " + error)
                //return alert("Cannot eval JSON: " + error);
            }
            return res
        }
    })

    var asideLeft = $("#asideLeft")
    var navList = $("#asideLeftList")
    var branches = navList.children("li")
    navList.on("click", "li>a", function (e) {
        var el = $(this), branch = el.data("branch"), leave = el.data("leave");
        // if (el.attr("leave")) {
        //     branch = $(this.parentNode.parentNode.parentNode).children("a").data("branch")
        //     leave = el.data("leave")
        // }
        if (el.attr("href") != "#") {
            $.cookie.set("branch", branch)
            $.cookie.set("leave", leave)
        }
    })

    toastr.options = {
        "positionClass": "toast-top-center",
        "showDuration": "300",
        "hideDuration": "500",
        "progressBar": true,
        "timeOut": "1000"
    }

}(jQuery)


$(function () {

});

$(document).ready(function () {
    var req = function (url, text_suc, text_fail, cb) {
        $.request({url: url}, function (res) {
            res.success ? toastr.success(res.msg ? res.msg : text_suc) : toastr.error(res.msg ? res.msg : text_fail)
            // console.log("设备及平台模式更新成功！")
            cb && cb(res)
        })
    }

    var asideDev = $("#asideLeftList").children()
    $("[href='#']", asideDev).on("click", function (e) {
        var $el = $(this), url = "/api/" + $el.attr("key");
        req(url, "操作成功！", "操作失败！")
    })
    $("[openwin]", asideDev).on("click", function (e) {
        var el = $(this), newUrl = el.attr("openwin")
        //alert(newUrl)
        newUrl && newUrl != "None" && window.open(newUrl, "_blank");
    })
    //window.bsCustomFileInput && bsCustomFileInput.init();
});