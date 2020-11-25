function combine(cols) {
    var infoEl = $("#infoEl"), prefix = infoEl.attr("path"), foreign = eval("(" + infoEl.attr("foreign") + ")");
    var tableName = infoEl.attr("table_name"), related = infoEl.attr("related"),
        relatedName = infoEl.attr("related_name"), rootPrefix = prefix, detailName = "detail";
    if (rootPrefix.indexOf("detail") > -1) {
        detailName = "deep"
        var rootArr = rootPrefix.split("/")
        rootArr.splice(rootArr.indexOf("detail"), 1)
        rootPrefix = rootArr.join("/")
    } else if (rootPrefix.indexOf("deep") > -1) {
        var rootArr = rootPrefix.split("/")
        rootArr.splice(rootArr.indexOf("deep"), 1)
        rootPrefix = rootArr.join("/")
    }

    var url = {
        list: prefix + "list",
        add: prefix + "add",
        update: prefix + "update",
        del: prefix + "del",
        exhibit: rootPrefix + "assist/query/exhibit?type=" + tableName
    }

    var editForm = $("#addModal form,#updateModal form"), columns = cols,
        temp = eval("(" + infoEl.attr("template") + ")"), isDetail = infoEl.attr("isDetail");
    //1.1根据route判断是否显示该项
    editForm.find("[route]").css("display", "none")
    editForm.find("[route='" + prefix + "']").css("display", "flex")
    //1.2根据配置的template来判断是否显示该项
    var readOnly = temp.readOnly || [], invisible = temp.invisible || []
    if (Boolean(temp.on_off) && temp.on_off != "false") {
        for (var t in readOnly) {
            editForm.find("[name='" + readOnly[t] + "']").attr("readOnly", "readOnly")
        }
        for (var v in invisible) {
            editForm.find("[name='" + invisible[v] + "']").parents(".form-group.row").css("display", "none")
        }
    }

    for (var num in columns) {
        var col = columns[num], name = col.name, index = invisible.indexOf(name);
        if ((col.route && col.route !== prefix) || index > -1) {
            col.visible = false
        }
    }


    //2.添加默认项目
    var tagCols = [
        {name: "id", type: "number", width: 30, align: "left", title: "ID", visible: false},
        {name: "number", type: "number", width: 50, align: "center", title: "序号"},
    ]
    tagCols = tagCols.concat(columns)
    var params = {}
    //3.添加外键项且不显示，并设置查询参数params
    for (var i in foreign) {
        var nm = foreign[i], ty = nm == "route" ? "text" : "number"
        tagCols.push({name: nm, type: ty, width: 30, align: "left", title: nm, visible: false})
        params[nm] = null
        if (relatedName && nm == relatedName) {
            params[nm] = related
        } else if (nm == "route") {
            params[nm] = prefix
        }
    }

    //4.操作按钮控制
    var detailFn = function (item) {
        var id = item.id, name = item.name ? item.name : id
        return rootPrefix + detailName + "?id=" + id + "&name=" + name
    }

    var opt_btn_def = {del: true, update: true, add: true, detail: isDetail == "True" ? detailFn : false},
        opt_btn = temp.opt_btn || opt_btn_def;
    if (opt_btn == true || opt_btn == "true") {
        opt_btn = {del: true, update: true, add: true, detail: detailFn}
    } else if (opt_btn == false || opt_btn == "false") {
        opt_btn = {del: false, update: false, add: false, detail: false}
    } else if ($.isPlainObject(opt_btn)) {
        for (var o in opt_btn) {
            var val = opt_btn[o];
            opt_btn[o] = val == "false" ? false : val == "true" ? true : Boolean(val);
        }
        if (opt_btn.detail == undefined || opt_btn.detail == true) {
            opt_btn.detail = detailFn
        }
        opt_btn = Object.assign(opt_btn_def, opt_btn)
    } else {
        opt_btn = opt_btn_def
    }

    createCommon(tagCols, url, params, opt_btn)
}