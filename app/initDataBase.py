def init_db(app, dataFn):
    db = app.attr["db"]
    init_base_db(db, app)
    # init_dev_db(db, app)
    # init_material_db(db, app)
    # init_content_db(db, app)

    dataFn(db, app)

# >>>>base 基础表
def init_base_db(db, app):
    mode = app.config.get("MODE")
    super = app.config.get("SUPER")
    admin = app.config.get("ADMIN")
    pat = app.config.get("PATTERN", mode.DEFAULT.value if mode else 1)
    sheets = app.config.get("SHEETS", {})

    # 版本 version
    version = db.model("version", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",
        "time": "DATE DEFAULT (datetime('now','localtime'))",
        "pattern": "integer default 1",
        "intro": "text"
    })
    versionRes = version.find("*", clause="where number=1.0")
    if len(versionRes["data"]) == 0:
        version.insert({"number": "1.0", "pattern": pat, "intro": "后台配置版：主页，表单，路由配置"})
    # version.update({"pattern": pat}, clause="where number=3.7")

    # 账号 account
    from app.models.Account import Account
    account = db.model("account", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",
        "name": "text not null unique",  # 账号
        "password": "text not null",
        "nickname": "text",
        "time": "DATE DEFAULT (datetime('now','localtime'))",
        "rank": "integer default 100",
        "right": "text default null",
        "tel": "text default null",
        "email": "text default null"
    })
    heroAge = account.find("*", clause="where name='heroAge'")
    other_admin = account.find("*", clause="where name='admin'")
    if len(heroAge["data"]) == 0:
        account.insert(
            {"id": super.ID.val, "number": super.NUMBER.val, "name": super.NAME.val, "nickname": super.NICKNAME.val,
             "password": Account.md5(super.PASSWORD.val), "rank": super.RANK.value})

    if len(other_admin["data"]) == 0:
        account.insert(
            {"id": admin.ID.val, "number": admin.NUMBER.val, "name": admin.NAME.val, "nickname": admin.NICKNAME.val,
             "password": Account.md5(admin.PASSWORD.val), "rank": admin.RANK.value})

    # >>>>set 系统设置
    # 展区管理
    exhibit_opt = sheets.get("exhibit", {})
    exhibit_col, exhibit_data = exhibit_opt.get("column", {}), exhibit_opt.get("data", [])
    exhibit = db.model("exhibit", exhibit_col if exhibit_col else {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # 展厅序号
        "type": "text not null",  # 所展示的类型
        "name": "text"  # 展厅名字
    })
    exhibitRes = exhibit.find("*")
    if len(exhibitRes["data"]) == 0 and exhibit_data:
        exhibit.insert(exhibit_data)

    # 主题管理
    # theme_opt = sheets.get("theme", {})
    # theme_col, theme_data = theme_opt.get("column", {}), theme_opt.get("data", [])
    # theme = db.model("theme", theme_col if theme_col else {
    #     "id": "integer not null primary key autoincrement unique",  # 主键
    #     "number": "integer default 1",  # 主题序号
    #     "type": "text not null",  # 所展示的类型
    #     "name": "text not null"  # 主题名字
    # })
    # themeRes = theme.find("*")
    # if len(themeRes["data"]) == 0 and theme_data:
    #     theme.insert(theme_data)

    # 标签管理
    label = db.model("label", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # 标签序号
        "name": "text not null"  # 标签名字
    })
    labelRes = label.find("*", clause="where id=0")
    if len(labelRes["data"]) == 0:
        label.insert({"number": 0, "id": 0, "name": "未标签"})

# >>>>dev 设备管理
def init_dev_db(db, app):
    # 灯光管理
    lamp = db.model("lamp", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "exhibit": "int not null references exhibit(id) on delete cascade",  # 展区外键
        # "exhibit": "int default 0 references exhibit(id) on delete set default",
        "number": "integer default 1",  # 灯光序号
        "port": "text not null",  # 端口号
        "name": "text not null",  # 灯光名称
        "tag": "text not null",  # 灯光标识
        "type": "boolean not null",  # 灯光类型
        "delay_start": "int",  # 灯光开机延迟
        "delay_end": "int",  # 灯光关机延迟
        "grouped": "text",  # 所属组
        "display": "boolean not null",  # APP是否显示
        "style": "text",  # APP样式
        "offset_x": "int",  # APP偏移X
        "offset_y": "int",  # APP偏移Y
        "scale": "float"  # APP缩放大小

    }, foreign="foreign key(exhibit) references exhibit(id)")
    # 主机管理
    host = db.model("host", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "exhibit": "int not null references exhibit(id) on delete cascade",  # 展区外键
        # "exhibit": "int default 0 references exhibit(id) on delete set default",
        "number": "integer default 1",  # 主机序号
        "name": "text not null",  # 主机名称
        "tag": "text not null",  # 主机标识
        "delay_start": "int",  # 主机开机延迟
        "delay_end": "int",  # 主机关机延迟
        "display": "boolean not null",  # APP是否显示
        "style": "text",  # APP样式
        "offset_x": "int",  # APP偏移X
        "offset_y": "int",  # APP偏移Y
        "scale": "float",  # APP缩放大小
        "grouped": "text"  # 所属组
    })
    # 设备组管理
    groups = db.model("groups", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "exhibit": "int not null references exhibit(id) on delete cascade",  # 展区外键
        # "exhibit": "int default 0 references exhibit(id) on delete set default",
        "number": "integer default 1",  # 设备组序号
        "name": "text not null",  # 设备组名称
        # "host": "text not null",  # 主机名称
        "tag": "text not null",  # 设备组标识
        "delay_start": "int",  # 设备组开机延迟
        "delay_end": "int",  # 设备组关机延迟
        "display": "boolean not null",  # APP是否显示
        "style": "text",  # APP样式
        "offset_x": "int",  # APP偏移X
        "offset_y": "int",  # APP偏移Y
        "scale": "float"  # APP缩放大小
    })
    # 红外管理
    infrared = db.model("infrared", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "exhibit": "int not null references exhibit(id) on delete cascade",  # 展区外键
        # "exhibit": "int default 0 references exhibit(id) on delete set default",
        "number": "integer default 1",  # 红外序号
        "name": "text not null",  # 红外名称
        "tag": "text not null",  # 红外编号
        "type": "text not null",  # 设备类型
        "delay_start": "int",  # 红外开机延迟
        "delay_end": "int",  # 红外关机延迟
        "num_start": "int",  # 开次数
        "num_end": "int",  # 关次数
        "grouped": "text",  # 所属组
        "params": "text",  # 定制参数
        "style": "text"  # APP样式
    })
    # 串口管理
    serial_port = db.model("serial_port", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "exhibit": "int not null references exhibit(id) on delete cascade",  # 展区外键
        # "exhibit": "int default 0 references exhibit(id) on delete set default",
        "number": "integer default 1",  # 串口序号
        "name": "text not null",  # 串口名称
        "tag": "text not null",  # 串口编号
        "type": "text not null",  # 串口类型
        "delay_start": "int",  # 串口开机延迟
        "delay_end": "int",  # 串口关机延迟
        "grouped": "text",  # 所属组
        "params": "text",  # 定制参数
        "style": "text"  # APP样式
    })

# >>>>material 素材管理
def init_material_db(db, app):
    # 视频
    video = db.model("video", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # 视频序号
        "name": "text not null",  # 视频名字
        "label": "integer default 0 references label(id) on delete set default",
        # "label": "int references label(id) on delete set null",  # 标签外键
        "path": "text",  # 视频存放路径
        "size": "text",  # 视频大小
        "time": "text"  # 视频时长
    })
    # 图片
    image = db.model("image", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # 图片序号
        "name": "text not null",  # 图片名字
        "path": "text",  # 图片存放路径
        "label": "integer default 0 references label(id) on delete set default",  # 标签外键
        "size": "text"  # 图片大小
    })
    # pdf
    pdf = db.model("pdf", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # pdf序号
        "name": "text not null",  # pdf名字
        "path": "text",  # pdf存放路径
        "label": "integer default 0 references label(id) on delete set default",  # 标签外键
        # "size": "text",  # pdf大小
        "page": "int default 0"  # 页数
    })
    # ppt
    ppt = db.model("ppt", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # ppt序号
        "name": "text not null",  # ppt名字
        "path": "text",  # ppt存放路径
        "label": "integer default 0 references label(id) on delete set default",  # 标签外键
        # "size": "text",  # ppt大小
        "page": "int default 0"  # 页数
    })
    # 声频
    voice = db.model("voice", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "number": "integer default 1",  # 音频序号
        "name": "text not null",  # 音频名字
        "path": "text",  # 音频存放路径
        "label": "integer default 0 references label(id) on delete set default",  # 标签外键
        "size": "text",  # 音频大小
        "time": "text"  # 音频时长
    })

# >>>>content 内容管理
def init_content_db(db, app):
    content = db.model("content", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "exhibit": "int not null references exhibit(id) on delete cascade",  # 展区外键
        "number": "integer default 1",  # 屏幕序号
        "name": "text not null",  # 屏幕名称
        "tag": "text not null",  # 屏幕编号标识
        "ip": "text not null",  # 屏幕IP
        "width": "int",  # 屏宽
        "height": "int",  # 屏高
        "play": "text",  # 默认播放的内容
        "volume": "int",  # 播放音量
        "loop": "boolean",  # 是否循环播放
        "cover_play": "text",  # 封面播放模式
        "display": "boolean not null",  # APP是否显示
        "style": "text",  # APP样式
        "scale": "float",  # APP缩放大小
        "offset_x": "int",  # APP偏移X
        "offset_y": "int",  # APP偏移Y
        "time": "DATE DEFAULT (datetime('now','localtime'))",  # 更新时间
        "links": "json default '[]'",  # 关联集合
        "content_type": "text",  # 内容类型：包含第三方控制，复杂\简易模式
        "themes": "text default ''"  # 多场景主题集合
    })
    # 内容详情-视频
    content_video = db.model("content_video", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # 视频序号
        "name": "text not null",  # 视频名称
        "path": "text",  # 视频真实所在路径
        "cover": "text",  # 视频封面所在路径
        "display_modal": "int",  # 视频显示模式0full全屏|1custom自定义,
        "play_modal": "int",  # 视频播放模式 0回到封面，1单循环，2顺序播放，3停止
        "offset_x": "int",  # APP偏移X
        "offset_y": "int",  # APP偏移Y
        "zoom_x": "int",  # APP缩放X
        "zoom_y": "int",  # APP缩放Y
        "width": "int",  # 源视频宽
        "height": "int",  # 源视频高
        "action_start": "text",  # 开始播放动作
        "action_end": "text",  # 结束播放动作
        "time": "text",  # 视频时长
        "size": "text",  # 视频大小
        "cover_size": "text"  # 视频封面大小
    })
    # 内容详情-图片
    content_image = db.model("content_image", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # 图片序号
        "name": "text not null",  # 图片名称
        "path": "text",  # 图片真实所在路径
        "style": "text",  # 图片展示样式
        "size": "text"  # 图片大小
    })
    # 内容详情-网页
    content_web = db.model("content_web", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # web序号
        "name": "text not null",  # web名称
        "url": "text"  # web地址
    })
    # 内容详情-欢迎词
    content_welcome = db.model("content_welcome", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # 序号
        "path": "text",  # 背景所在路径
        "title": "text not null",  # 主标题
        "color": "text",  # 主标题颜色
        "font": "text",  # 主标题字体大小
        "offset_x": "int",  # 主标题X偏移
        "offset_y": "int",  # 主标题Y偏移
        "align": "text",  # 主标题对齐方式0center,1right,2left
        "sub_title": "text not null",  # 副标题
        "sub_color": "text",  # 副题颜色
        "sub_font": "text",  # 副标题字体大小
        "sub_offset_x": "int",  # 副标题X偏移
        "sub_offset_y": "int",  # 副标题Y偏移
        "sub_align": "text",  # 副标题对齐方式0center,1right,2left
        "size": "text"  # 背景图大小
    })
    # 内容详情-封面
    content_cover = db.model("content_cover", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # 封面序号
        "name": "text not null",  # 封面名称
        "path": "text",  # 封面所在路径
        "size": "text"  # 封面图片大小
    })
    # 内容详情-屏保
    content_saver = db.model("content_saver", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # 屏保序号
        "type": "number",  # 屏保类型 image | video
        "path": "text",  # 屏保文件所在路径
        "size": "text"  # 屏保大小
    })
    # 内容详情-解说词
    content_caption = db.model("content_caption", {
        "id": "integer not null primary key autoincrement unique",  # 主键
        "content": "int not null references content(id) on delete cascade",  # 内容外键
        "theme": "int not null references theme(id) on delete cascade",  # 主题外键
        "number": "integer default 1",  # 解说词序号
        "text": "text not null",  # 解说词文字
        "path": "text",  # 解说词声音文件所在路径
        "size": "text"  # 音频大小
    })
