function createCommon(columns, url, params, opt_btn = {}, opts = {
    add: {}, update: {}, del: {}, pops: [], text: {}, btn: {}
}) {
    !opt_btn.add && $("#addBtn").css("display", "none")

    function setForm(optForm, data) {
        var optEls = optForm.find("[name]")
        for (var i = 0; i < optEls.length; i++) {
            var opt_el = optEls.eq(i)
            var name = opt_el.attr("name")
            opt_el.val(data[name])
        }
    }

    var exhibitor = $("#exhibitor")
    if (Object.keys(params).indexOf("exhibit") > -1) {
        exhibitor.css("display", "block")
        exhibitor.on("change", function (e) {
            //var options = exhibitor.find("option:selected").val(); //获取选中的项
            var options = exhibitor.val()
            console.log("exhibitor选中项为：>>", options)
            options != null && addForm.find("[name='exhibit']").val(options)
            params["exhibit"] = options
            setForm(addForm, params)
            //查询
            $.request({url: url.list, data: params}, function (res) {
                controller.clients = res.data
                gridList.jsGrid("loadData");
            })
        })

        //获取可显示列表
        $.request({url: url.exhibit}, function (res) {
            console.log(">>", res)
            var data = res.data
            exhibitor.html("")
            if (data.length == 0) {
                alert("请先配置展区")
                return false
            }
            for (var i  in data) {
                var item = data[i], val = item.id, name = item.name
                exhibitor.append($.parseHTML("<option value='" + val + "'>" + name + "</option>"))
            }
            exhibitor.trigger("change")
        })
    } else {
        //查询
        exhibitor.css("display", "none")
        $.request({url: url.list, data: params}, function (res) {
            controller.clients = res.data
            gridList.jsGrid("loadData");
        })
    }


    var addForm = $("#addModal form")
    var addOpt = $("#addOpt")
    var addOptClose = $("#addOptClose")
    var addOptPro = $("#addOptPro")
    setForm(addForm, params)
    $("#addModal,#updateModal").modal({backdrop: "static", show: false})

    var updateForm = $("#updateModal form")
    var updateOpt = $("#updateOpt")
    var updateOptClose = $("#updateOptClose")
    var updateOptPro = $("#updateOptPro")
    var updateModalBtn = $("#updateModalBtn")

    var delForm = $("#delModal form")
    var delOpt = $("#delOpt")
    var delOptClose = $("#delOptClose")
    var delModalBtn = $("#delModalBtn")

    jsGrid.locale("zh-cn");
    var controller = {
        loadData: function (filterRow) {
            console.log("》》》》loadData", controller.clients, controller.clients.length, controller, filterRow)
            //return controller.clients
            return $.grep(controller.clients, function (row) {
                var res = true
                for (var i in filterRow) {
                    filterVal = filterRow[i], val = row[i]
                    filterVal = typeof filterVal == "string" ? filterVal.trim() : filterVal
                    val = typeof val == "string" ? val.trim() : val
                    if (filterVal !== "" && filterVal !== undefined && filterVal !== null) {
                        res = val.indexOf ? val.indexOf(filterVal) > -1 : val == filterVal
                    }
                }
                return res
            });
        },
        clients: []
    }
    var fields = columns.concat([
        {
            name: "opt", type: "text", title: "操作",
            width: 160,
            align: "center",
            readOnly: false,
            //filtering: false,
            //visible: false,
            disabled: false,
            inserting: false,
            editing: false,
            sorting: false,
            filterTemplate: function () {
                return $('<div>' +
                    '<a href="#" class="fas fa-search" style="font-size:18px;align-text:center;line-height:32px;" data-type="search"></a>' +
                    '<a href="#" class="fas fa-share mr-1" style="font-size:18px;align-text:center;line-height:32px; margin-left:5px" data-type="back"></a>' +
                    // '<a href="#" class="fas fa-caret-down" style="font-size:22px;align-text:center;line-height:32px;" data-type="search"></a>' +
                    // '<a href="#" class="fas fa-angle-double-up" style="font-size:20px;align-text:center;line-height:32px;" data-type="sort" data-sort="asc"></a>' +
                    '<a href="#" class="fas fa-sort-numeric-down" style="font-size:20px;align-text:center;line-height:32px;" data-type="asc"></a>' +
                    '<a href="#" class="fas fa-retweet" style="font-size:20px;align-text:center;line-height:32px;margin-left:4px;" data-type="reverse"></a>' +
                    '</div>').on("click", "a", function (e) {
                    e.stopPropagation();
                    //DESC
                    var $e = $(this), type = $e.data("type")
                    type == "back" ? gridList.jsGrid("clearFilter").done(function () {
                        console.log("清空搜索条件完成");
                    }) : type == "search" ? gridList.jsGrid("loadData") : "";
                    if (type == "asc" || type == "reverse") {
                        //排序
                        params["sort"] = type
                        $.request({url: url.sort, data: params}, function (res) {
                            controller.clients = res.data
                            gridList.jsGrid("loadData");
                        })
                    }
                    //console.log("搜索。。。", arguments[0], arguments[1], $(this).data("type"))
                })
            },
            insertTemplate: function () {
                return ""
            },
            filterValue: function () {
                return ""
            },
            itemTemplate: function (value, item) {
                // var html_detail = opt_btn.detail ? '<button type="button" class="btn btn-default" data-type="detail">详情</button>' : ''
                var html_detail = '', html_custom = ''
                if (opt_btn.detail) {
                    for (let i = 0; i < opts.children.length; i++) {
                        let t = opts.text.detail, c = opts.children[i], f = t ? t[c] : undefined
                        html_detail += '<button type="button" class="btn btn-default" data-type="detail" data-child="' + c + '">' + (f ? f : "详情") + '</button>'
                    }
                }
                for (let k in opts.btn) {
                    html_custom += '<button type="button" class="btn btn-default" data-type="custom" data-custom="' + k + '">' + opts.btn[k].text + '</button>'
                }
                var html_del = opt_btn.del ? '<button type="button" class="btn btn-default" data-type="delete">删除</button>' : ''
                var html_update = opt_btn.update ? '<button type="button" class="btn btn-default" data-type="update">修改</button>' : ''
                return $('<div class="btn-group">' +
                    html_update +
                    html_del +
                    html_detail +
                    html_custom +
                    '</div>').on("click", "button",
                    function (e) {
                        e.stopPropagation();
                        var $el_btn = $(this), type_btn = $el_btn.data("type")
                        if (type_btn == "update") {
                            updateForm[0].reset()
                            opts.update.set && opts.update.set(item)
                            var media = updateForm.find("[name='preVideo'],[name='preAudio'],[name='preImage']")
                            media.css("display", "none").attr('src', '')
                            if (media.length > 0) {
                                var media_file = media.siblings().find("input")
                                for (var m = 0; m < media_file.length; m++) {
                                    var fileName = media_file.eq(m).attr("name")
                                    var fileEl = media.eq(m)
                                    var fileType = fileEl.attr("name").split("pre")[1].toLowerCase()
                                    item[fileName] && fileEl.css("display", "block").attr('src', $.url_for(fileType + "/" + item[fileName]))
                                }
                            }
                            var app = updateForm.find("[name='preApp']")
                            if (app.length > 0) {
                                var app_file = app.siblings().find("input")
                                for (var m = 0; m < app_file.length; m++) {
                                    var fileName = app_file.eq(m).attr("name")
                                    var fileEl = app.eq(m)
                                    item[fileName] && fileEl.css("display", "block").attr('href', $.url_for("other/" + item[fileName]))
                                }
                            }

                            updateModalBtn.trigger("click")
                            for (var i in fields) {
                                var name = fields[i].name
                                var $el = updateForm.find("[name='" + name + "']")
                                var type = $el.attr("type")
                                var val = item[name]
                                if (type == "radio") {
                                    //$el.prop("checked",false);
                                    $el.each(function () {
                                        var $radio = $(this)
                                        if ($radio.val() == val) {
                                            console.log(">>>>", $radio.val(), val)
                                            $radio.prop("checked", true);
                                        }
                                    })
                                } else if (type == "file") {
                                    $el.siblings(".custom-file-label").text(val)
                                } else {
                                    $el.val(val)
                                }
                            }
                            //updateForm.find("[name='number']").val(item.number)
                            //updateForm.find("[name='name']").val(item.name)
                        } else if (type_btn == "delete") {
                            delModalBtn.trigger("click")
                            setForm(delForm, item)
                        } else if (type_btn == "detail") {
                            var exec = opt_btn.detail, child = $el_btn.data("child")
                            if (exec) {
                                window.location.href = exec(item, child)
                            }
                        } else if (type_btn == "custom") {
                            var custom_key = $el_btn.data("custom"), exec = opts.btn[custom_key]["func"]
                            exec && exec(item)
                        }

                        //$.request({url: "/set/exhibit/add", data: {name: "大厅", number: 3}}, function (res) {
                        //controller.clients = res.data
                        //gridList.jsGrid("loadData");
                        //})
                    })
            }

        }
    ])

    var gridList = $("#contentList")
    gridList.jsGrid({
        height: "690",
        width: "100%",
        pageSize: 11,
        paging: true,
        //pageButtonCount: 5,
        deleteConfirm: "确定要删除吗",
        loadMessage: "正在装载数据，请稍候......",
        sorting: true,
        filtering: true,
        //data: db.clients,
        controller: controller,
        fields: fields
    });

    var pops = function (params) {
        for (var i in opts.pops) {
            params.delete(opts.pops[i])
        }
    }
    //点击添加按钮时操作
    // $("#addBtn").on("click", function () {
    //     addForm[0].reset()
    //     addForm.find("[name='preVideo'],[name='preAudio'],[name='preImage']").css("display", "none").attr('src', '')
    // })
    //点击保存按钮

    //点击取消按钮执行
    var cancelOpt = function ($form, $save) {
        //清理值
        $form[0].reset()
        //清理预览多媒体
        var media = $form.find("[name='preVideo'],[name='preAudio'],[name='preImage'],[name='preApp']")
        media.css("display", "none").attr('src', '').attr("href", "javascript:0;")
        //清理异步请求
        $save.xhr && $save.xhr.abort()
        $save.xhr = null
    }
    //创建xhr
    var createXHR = function (pro, $save) {
        return function () {
            pro.find("progress").attr({max: 0, value: 0})
            pro.find(".percent").text(0 + "%")
            pro.find(".speed").text("0b/s")
            pro.find(".leftTime").text("预计剩余0秒")
            pro.css("display", "block")
            $save.css("display", "none")
            let stime = 0, sloaded = 0, xhr = $.ajaxSettings.xhr()
            // let stime, sloaded, xhr = new XMLHttpRequest()
            console.log("--创建xhr--")
            xhr.upload.onprogress = function (e) {
                let percent = (e.loaded / e.total * 100).toFixed(0)
                pro.find("progress").attr({max: e.total, value: e.loaded})
                pro.find(".percent").text(percent + "%")

                //上传速度
                let endTime = new Date().getTime();
                let dTime = (endTime - stime) / 1000;
                let dloaded = e.loaded - sloaded
                let speed = dloaded / dTime, unit = "b/s"
                let leftTime = (e.total - e.loaded) / speed, d = Math.floor(leftTime / (60 * 60 * 24)),
                    h = Math.floor((leftTime % 86400) / (60 * 60)),
                    m = Math.floor(((leftTime % 86400) % 3600) / 60),
                    //s = (((leftTime % 86400) % 3600) % 60).toFixed(2)
                    s = Math.floor(((leftTime % 86400) % 3600) % 60)
                if (speed / (1024 * 1024) > 1) {
                    unit = "mb/s"
                    speed = speed / (1024 * 1024)
                } else if (speed / 1024 > 1) {
                    unit = "kb/s"
                    speed = speed / 1024
                }
                var dateStr = "预计剩余"
                if (d > 31) {
                    dateStr += "1月以上"
                    unit += " 蜗速，请取消"
                } else {
                    if (d > 0) {
                        dateStr += d + "天"
                        unit += " 龟速，请取消"
                    }
                    if (h > 0) {
                        dateStr += h + "时"
                    }
                    if (m > 0) {
                        dateStr += m + "分"
                    }
                    if (s > 0) {
                        dateStr += s + "秒"
                    }
                }
                stime = new Date().getTime(), sloaded = e.loaded;
                pro.find(".speed").text(speed.toFixed(2) + unit)
                // console.log(speed + unit, dateStr)
                pro.find(".leftTime").text(dateStr)
            }
            // xhr.upload.addEventListener("progress", doProgress, false)
            xhr.upload.onloadstart = function () {
                console.log("开始上传")
                stime = new Date().getDate()
                sloaded = 0;
            }
            xhr.upload.onloadend = function () {
                console.log("上传结束，开始删除监听")
                // xhr.upload.removeEventListener("progress", doProgress)
                xhr.upload.onprogress = null
                xhr.upload.onloadstart = null
                xhr.upload.onloadend = null
                xhr = null
                //还原数据
                pro.css("display", "none")
                $save.css("display", "block")
            }
            return xhr
        }
    }
    addOptClose.on("click", function () {
        console.log("取消----请求")
        cancelOpt(addForm, addOpt)
        // addOpt.xhr && addOpt.xhr.abort()
        // addOpt.xhr = null
    })
    updateOptClose.on("click", function () {
        cancelOpt(updateForm, updateOpt)
        // var media = updateForm.find("[name='preVideo'],[name='preAudio'],[name='preImage']")
        // media.css("display", "none").attr('src', '')
    })
    //选取上传文件时操作
    $("[type='file']", [addForm[0], updateForm[0]]).on("change", function (e) {
        var el = this, video = el.files[0], url = video ? URL.createObjectURL(video) : "";
        var preEl = $(el).parents(".input-group.col-sm-9").siblings("[name^='pre']"), name = preEl.attr("name")
        preEl.css("display", "block")
        name == "preApp" ? preEl.attr("href", url) : preEl.attr("src", url)
    })

    //新增
    addOpt.on("click", function (e) {
        // var params = addForm.serialize()
        var params = new FormData(addForm.get(0));
        opts.add.pre && opts.add.pre(params)
        pops(params)

        addOpt.xhr = $.request({
            url: url.add, data: params, type: "post", tip: true, contentType: false, processData: false,
            xhr: createXHR(addOptPro, addOpt),
            complete: function (x, status) {
                cancelOpt(addForm, addOpt)
            }
        }, function (res) {
            controller.clients = res.data
            gridList.jsGrid("loadData");
            addOptClose.trigger("click")
            addForm[0].reset()
            opts.add.end && opts.add.end(res)
        }, function (res) {
            res.msg = "上传已取消"
        })
    })
    //修改
    updateOpt.on("click", function (e) {
        // var params = updateForm.serialize()
        var params = new FormData(updateForm.get(0));
        opts.update.pre && opts.update.pre(params)
        pops(params)

        updateOpt.xhr = $.request({
            url: url.update, data: params, type: "post", tip: true, contentType: false, processData: false,
            xhr: createXHR(updateOptPro, updateOpt),
            complete: function (x, status) {
                cancelOpt(updateForm, updateOpt)
            }
        }, function (res) {
            controller.clients = res.data
            gridList.jsGrid("loadData");
            updateOptClose.trigger("click")
            opts.update.end && opts.update.end(res)
        }, function (res) {
            res.msg = "上传已取消"
        })
    })

    //删除
    delOpt.on("click", function (e) {
        var params = delForm.serialize()
        opts.del.pre && opts.del.pre(params)

        $.request({url: url.del, data: params, type: "post", tip: true}, function (res) {
            controller.clients = res.data
            gridList.jsGrid("loadData");
            delOptClose.trigger("click")
            opts.del.end && opts.del.end(res)
        })
    })

}