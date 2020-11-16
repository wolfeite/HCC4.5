function createCommon(columns, url, params, opt_btn = {}) {
    var opt_btn_def = {del: true, update: true}
    var opt_btn = Object.assign(opt_btn_def, opt_btn)

    function setForm(optForm, data) {
        var optEls = optForm.find("[name]")
        for (var i = 0; i < optEls.length; i++) {
            var opt_el = optEls.eq(i)
            var name = opt_el.attr("name")
            opt_el.val(data[name])
        }
    }

    //查询
    $.request({url: url.list, data: params}, function (res) {
        controller.clients = res.data
        gridList.jsGrid("loadData");
    })

    var addForm = $("#addModal form")
    var addOpt = $("#addOpt")
    var addOptClose = $("#addOptClose")
    setForm(addForm, params)

    var updateForm = $("#updateModal form")
    var updateOpt = $("#updateOpt")
    var updateOptClose = $("#updateOptClose")
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
                    '</div>').on("click", "a", function (e) {
                    e.stopPropagation();
                    var $e = $(this), type = $e.data("type")
                    type == "back" ? gridList.jsGrid("clearFilter").done(function () {
                        console.log("清空搜索条件完成");
                    }) : gridList.jsGrid("loadData");
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
                var html_detail = opt_btn.detail ? '<button type="button" class="btn btn-default" data-type="detail">图片</button>' : ''
                var html_del = opt_btn.del ? '<button type="button" class="btn btn-default" data-type="delete">删除</button>' : ''
                var html_update = opt_btn.update ? '<button type="button" class="btn btn-default" data-type="update">修改</button>' : ''
                return $('<div class="btn-group">' +
                    html_update +
                    html_del +
                    html_detail +
                    '</div>').on("click", "button",
                    function (e) {
                        e.stopPropagation();
                        var $el_btn = $(this), type_btn = $el_btn.data("type")
                        if (type_btn == "update") {
                            updateForm[0].reset()
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
                            var detail_exec = opt_btn.detail || "#"
                            window.location.href = detail_exec(item)
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


    //新增
    addOpt.on("click", function (e) {
        // var params = addForm.serialize()
        var params = new FormData(addForm.get(0));
        $.request({
            url: url.add, data: params, type: "post", tip: true, contentType: false, processData: false
        }, function (res) {
            controller.clients = res.data
            console.log("》》》》????", controller.clients)
            gridList.jsGrid("loadData");
            addOptClose.trigger("click")
            addForm[0].reset()
        })
    })
    //修改
    updateOpt.on("click", function (e) {
        // var params = updateForm.serialize()
        var params = new FormData(updateForm.get(0));
        $.request({
            url: url.update, data: params, type: "post", tip: true, contentType: false, processData: false
        }, function (res) {
            controller.clients = res.data
            console.log("》》》》????", controller.clients)
            gridList.jsGrid("loadData");
            updateOptClose.trigger("click")
        })
    })
    updateOptClose.on("click", function () {
        var media = updateForm.find("[name='preVideo'],[name='preAudio'],[name='preImage']")
        media.css("display", "none").attr('src', '')
    })
    //删除
    delOpt.on("click", function (e) {
        var params = delForm.serialize()
        $.request({url: url.del, data: params, type: "post", tip: true}, function (res) {
            controller.clients = res.data
            console.log("》》》》????", controller.clients)
            gridList.jsGrid("loadData");
            delOptClose.trigger("click")
        })
    })

}