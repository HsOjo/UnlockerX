from app.res.const import Const
from .english import English


class Chinese(English):
    l_this = '简体中文'
    unknown = '未知内容: (%s)'
    cancel = '取消'
    ok = '确定'
    none = '无'

    description_about = '''%s 版本 %s

使用蓝牙设备靠近以解锁你的Mac！

由%s开发。
以下是GitHub页面链接。''' % (Const.app_name, Const.version, Const.author)
    description_set_password = '''设置当前用户密码。
将用于解锁你的Mac。'''
    description_crash = '''卧槽! 应用崩溃了!
接下来将导出日志，请将日志提交给开发者，谢谢配合。'''
    description_set_startup = '''你确定要将该应用添加到登录启动项吗？
(你可以在 `系统偏好设置` - `用户与群组` - `登录项`取消。)'''
    description_set_event = '''在此输入可执行程序的路径。如果该事件被触发，将会执行这个程序。
事件参数将通过环境变量进行传递。（JSON 格式, 键值: %s）

有关更多信息，请访问 GitHub 页面下的 “doc/” 目录。（例如使用样例）''' % Const.app_env
    description_clear_config = '''这将会删除配置文件，确定吗？'''
    description_clear_config_restart = '''配置文件已经被删除，现在重新启动该应用？'''
    description_bind_bluetooth_device = '''绑定蓝牙设备。如果你的设备不在该列表，你应该先到 "系统偏好设置" - "蓝牙" 配对你的设备。'''
    description_set_weak_signal_value = '''信号弱将触发弱信号事件。
单位：dBm，信号值越小，信号越弱。'''
    description_welcome_need_accessibility = '''%s 需要权限以解锁你的Mac。
你需要在接下来的窗口中点击 "隐私" - "辅助功能"，并将 "%s" 添加到控制列表。''' % (Const.app_name, Const.app_name)
    description_welcome_pair_device = '''在绑定蓝牙设备之前，你需要在接下来的窗口中，完成蓝牙设备的配对。'''
    description_welcome_end = '''很好！现在 %s 可以开始工作了。
Enjoy yourself!''' % Const.app_name

    view_device_name = '设备名称：%s'
    view_device_address = '设备地址：%s'
    view_device_signal_value = '设备信号：%s'

    menu_bind_bluetooth_device = '绑定蓝牙设备'
    menu_lock_now = '立即锁定（需要手动解锁）'
    menu_disable_leave_lock = '禁用离开锁定'
    menu_disable_near_unlock = '禁用靠近解锁'
    menu_preferences = '偏好设置'
    menu_advanced_options = '高级选项'
    menu_event_callback = '事件回调'
    menu_set_lock_status_changed_event = '设置锁定状态改变事件'
    menu_set_lid_status_changed_event = '设置合盖状态改变事件'
    menu_set_signal_weak_event = '设置信号弱事件'
    menu_set_connect_status_changed_event = '设置连接状态改变事件'
    menu_set_weak_signal_lock_delay = '设置信号弱锁定延迟'
    menu_set_disconnect_lock_delay = '设置断开连接锁定延迟'
    menu_set_weak_signal_value = '设置弱信号值'
    menu_set_password = '设置当前用户密码'
    menu_select_language = '设置语言'
    menu_set_startup = '设置登录启动'
    menu_check_update = '检查更新'
    menu_clear_config = '清空配置文件'
    menu_use_screen_saver_replace_lock = '使用屏幕保护替代锁定'
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

    title_info = '信息'
    noti_password_need = '解锁失败！需要设置密码。'
    noti_unlock_error = '解锁失败！操作无效。'
