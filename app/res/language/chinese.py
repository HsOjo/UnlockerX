from app.res.const import Const
from .english import English


class Chinese(English):
    l_this = '简体中文'
    unknown = '未知内容: (%s)'
    cancel = '取消'
    ok = '确定'

    description_about = '''%s 版本 %s

由%s开发。
以下是GitHub页面链接。''' % (Const.app_name, Const.version, Const.author)
    description_set_password = '''设置管理员用户密码。
将用于执行更改“电源管理设置”。（阻止合盖睡眠）'''
    description_set_username = '''设置管理员用户名。（这里的用户名不是全名！您可以在“terminal.app”上查看，登录您的管理用户，并在终端上输入"whoami"。）
将用于执行更改“电源管理设置”。（阻止合盖睡眠）
(如果当前用户是管理员，可留空。如果为空，将使用当前用户名。)'''
    description_crash = '''卧槽! 应用崩溃了!
接下来将导出日志，请将日志提交给开发者，谢谢配合。'''
    description_set_startup = '''你确定要将该应用添加到登录启动项吗？
(你可以在 `系统偏好设置` - `用户与群组` - `登录项`取消。)'''
    description_set_event = '''在此输入可执行程序的路径。如果该事件被触发，将会执行这个程序。
事件参数将通过环境变量进行传递。（JSON 格式, 键值: %s）

有关更多信息，请访问 GitHub 页面下的 “doc/” 目录。（例如使用样例）''' % Const.app_env
    description_clear_config = '''这将会删除配置文件，确定吗？'''
    description_clear_config_restart = '''配置文件已经被删除，现在重新启动该应用？'''

    menu_lock_now = '立即锁定'
    menu_preferences = '偏好设置'
    menu_advanced_options = '高级选项'
    menu_event_callback = '事件回调'
    menu_set_lock_status_changed_event = '设置锁定状态改变事件'
    menu_set_username = '设置管理员用户名 (非管理员用户使用)'
    menu_set_password = '设置管理员用户密码'
    menu_select_language = '设置语言'
    menu_set_startup = '设置登录启动'
    menu_check_update = '检查更新'
    menu_clear_config = '清空配置文件'
    menu_export_log = '导出日志文件'
    menu_about = '关于'
    menu_quit = '退出'

    title_crash = '应用崩溃'
    title_welcome = '欢迎使用'

    noti_update_version = '发现新版本: %s'
    noti_update_time = '发布时间: %s'
    noti_update_none = '当前已是最新版本。'
    noti_update_star = '（如果你喜欢这个应用，请在GitHub给我个star，thanks。）'
    noti_network_error = '网络出现问题，请稍后重试。'
