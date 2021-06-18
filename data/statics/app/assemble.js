function combine(cols, options = {}, url_params = {}) {
    var infoEl = $("#infoEl"), prefix = infoEl.attr("path"), foreign = eval("(" + infoEl.attr("foreign") + ")");
    var tableName = infoEl.attr("table_name"), related = infoEl.attr("related"),
        relatedName = infoEl.attr("related_name"), rootPrefix = prefix, detailName = "detail",
        children = eval("(" + infoEl.attr("children") + ")");
    if (rootPrefix.indexOf("detail") > -1) {
        detailName = "deep"
        var rootArr = rootPrefix.split("/")
        rootArr.splice(rootArr.indexOf("detail"), 1)
        rootPrefix = rootArr.join("/")
    } else if (rootPrefix.indexOf("deep") > -1) {
        detailName = "deep"
        var rootArr = rootPrefix.split("/")
        rootArr.splice(rootArr.indexOf("deep"), 1)
        rootPrefix = rootArr.join("/")
    }

    var url = {
        list: prefix + "list" + "?child=" + tableName,
        add: prefix + "add" + "?child=" + tableName,
        update: prefix + "update" + "?child=" + tableName,
        del: prefix + "del" + "?child=" + tableName,
        exhibit: rootPrefix + "assist/query/exhibit?type=" + tableName,
        sort: prefix + "sort" + "?child=" + tableName
    }

    var editForm = $("#addModal form,#updateModal form"), columns = cols,
        temp = eval("(" + infoEl.attr("template") + ")"), isDetail = infoEl.attr("is_detail");
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

    //2.添加默认项目
    var defCol = {
        "id": {name: "id", type: "number", width: 30, align: "left", title: "ID", visible: false},
        "number": {name: "number", type: "number", width: 50, align: "center", title: "序号"}
    }, tagCols = [], srcCols = []
    for (var num in columns) {
        var col = columns[num], name = col.name, index = invisible.indexOf(name);
        if (!col.visible && ((col.route && col.route !== prefix) || index > -1)) {
            col.visible = false
        }
        if (defCol[name]) {
            defCol[name] = Object.assign(defCol[name], col)
            continue;
        }
        tagCols.push(col)
    }

    for (var s in defCol) {
        srcCols.push(defCol[s])
    }
    tagCols = srcCols.concat(tagCols)

    //3.添加外键项且不显示，并设置查询参数params
    var params = {}
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
    var detailFn = function (item, chd, exhibitVal) {
        var id = item.id, name = item.name ? item.name : id
        var detail_url = rootPrefix + detailName + "?id=" + id + "&name=" + name + "&child=" + chd + (exhibitVal ? "&exhibit=" + exhibitVal : "")
        let other = url_params.detail ? url_params.detail : {}
        for (let k in other) {
            detail_url += k == "item" ? "&" + other[k] + "=" + item[other[k]] : "&" + k + "=" + other[k]
        }
        return detail_url
    }

    isDetail = isDetail == "True" ? true : false
    var opt_btn_def = {del: true, update: true, add: true, detail: isDetail ? detailFn : false},
        opt_btn = temp.opt_btn || opt_btn_def;
    if (opt_btn == true || opt_btn == "true") {
        opt_btn = opt_btn_def
    } else if (opt_btn == false || opt_btn == "false") {
        opt_btn = {del: false, update: false, add: false, detail: false}
    } else if ($.isPlainObject(opt_btn)) {
        for (var o in opt_btn) {
            var val = opt_btn[o];
            opt_btn[o] = val == "false" ? false : val == "true" ? true : Boolean(val);
        }
        if (opt_btn.detail != undefined) {
            opt_btn.detail = opt_btn.detail == true && isDetail ? detailFn : false
        }
        opt_btn = Object.assign(opt_btn_def, opt_btn)
    } else {
        opt_btn = opt_btn_def
    }

    var opts = $.isPlainObject(options) ? Object.assign({
        add: {}, update: {}, del: {}, pops: [], text: {}, btn: {}
    }, options) : {}
    opts.children = children
    return createCommon(tagCols, url, params, opt_btn, opts)
}