from app.res.const import Const
from . import Language


class Chinese(Language):
    code = 'cn'
    l_this = '简体中文'

    ok = '确定'
    cancel = '取消'
    none = '无'

    unit_dbm = 'dBm'

    status_normal = '已连接'
    status_weak = '信号弱'
    status_disconnect = '已断开'

    menu_bind_bluetooth_device = '绑定蓝牙设备'
    menu_pause = '暂停'
    menu_resume = '恢复'
    menu_preferences = '偏好设置'
    menu_set_weak_signal_value = '设置信号弱临界值'
    menu_set_weak_signal_lock_delay = '设置信号弱锁定延迟'
    menu_set_disconnect_lock_delay = '设置断开连接锁定延迟'
    menu_set_bluetooth_refresh_rate = '设置蓝牙刷新频率'
    menu_set_unlock_delay = '设置解锁延迟'
    menu_signal_value_visible_on_icon = '显示信号值在图标旁'
    menu_set_password = '设置当前用户密码'
    menu_clear_password = '清除已存密码'
    menu_set_startup = '设置登录启动'
    menu_advanced_options = '高级选项'
    menu_export_log = '查看日志'
    menu_clear_config = '清空配置文件'
    menu_select_language = '设置语言'
    menu_check_update = '检查更新'
    menu_about = '关于'
    menu_quit = '退出'

    title_welcome = '欢迎使用'
    title_info = '信息'
    title_crash = '应用崩溃'

    description_set_password = '''设置当前用户的登录密码。
将用于解锁你的 Mac。'''
    description_password_warning = '''注意：密码保存在 macOS 钥匙串中。
由于本应用未签名，该钥匙串项允许任意本机程序访问，因此任何以你身份运行的程序都可读取它。这是在无提权、免密自动解锁下的既定取舍。'''
    description_password_incorrect = '''密码不正确，未保存。
请重试。'''
    description_select_language = '选择你的语言。'
    description_bind_bluetooth_device = '选择一台已配对的蓝牙设备进行绑定。'
    description_no_paired_device = '未找到已配对的蓝牙设备。请先到 "系统设置" - "蓝牙" 配对你的设备。'
    description_bluetooth_off = '蓝牙已关闭。请先到 "系统设置" - "蓝牙" 开启蓝牙。'
    description_set_weak_signal_value = '''信号弱将触发离开锁屏倒计时。
单位：dBm，信号值越小，信号越弱。'''
    description_set_weak_signal_lock_delay = '在蓝牙设备信号弱时，触发锁屏延迟的时间。'
    description_set_disconnect_lock_delay = '在蓝牙设备断开时，触发锁屏延迟的时间。'
    description_set_bluetooth_refresh_rate = '''蓝牙刷新间隔。
单位：秒，最小为 1 秒。'''
    description_set_unlock_delay = '设备在场后解锁前的延迟时间。'
    description_need_accessibility = f'''{Const.app_name} 需要 "辅助功能" 权限以模拟键入并解锁你的 Mac。
请在接下来的窗口中，于 "隐私与安全性" - "辅助功能" 启用 {Const.app_name}。'''
    description_accessibility_enabled = f'''"辅助功能" 已启用 {Const.app_name}。'''
    description_cancel_accessibility = f'''你跳过了 "辅助功能"。{Const.app_name} 将只在离开时锁屏，不会自动解锁。'''
    description_welcome_pair_device = '在绑定蓝牙设备之前，请先在接下来的窗口中完成蓝牙设备的配对。'
    description_set_startup = '是否将本应用设为登录时自动启动？'
    description_clear_config = '这将会删除配置文件，确定吗？'
    description_clear_config_restart = '配置文件已经被删除，请重新启动该应用。'
    description_clear_password_confirm = '从钥匙串中移除已保存的密码？'
    description_need_password = '未保存密码。请设置登录密码以启用自动解锁。'
    description_about_confirm = '是否打开 GitHub 项目页面？'

    prompt_input_password = '密码：'

    noti_connected = '设备已连接。'
    noti_disconnected = '设备已断开。'
    noti_weak_signal_lock = '信号弱，正在锁屏。'
    noti_unlock_success = '已自动解锁。'
    noti_unlock_failed = '自动解锁失败。'
    noti_password_need = '解锁失败！请先设置密码。'
    noti_unlock_error = '解锁失败次数过多，已自动暂停。请检查密码与 "辅助功能" 设置。'
    noti_update_none = '当前已是最新版本。'
    noti_update_star = '（如果你喜欢这个应用，请在 GitHub 给我个 star，thanks。）'
    noti_network_error = '网络出现问题，请稍后重试。'

    def view_device_name(self, name):
        return f'设备名称：{name}'

    def view_device_address(self, address):
        return f'设备地址：{address}'

    def view_device_signal(self, signal):
        return f'设备信号：{signal}'

    def view_status(self, status):
        return f'状态：{status}'

    description_about = f'''{Const.app_name} 版本 {Const.version}

使用蓝牙设备靠近以解锁你的 Mac！

由 {Const.author} 开发。'''

    description_welcome_end = f'''很好！现在 {Const.app_name} 可以开始工作了。
Enjoy yourself!'''

    def noti_update_version(self, version):
        return f'发现新版本：{version}'

    def noti_update_time(self, release_time):
        return f'发布时间：{release_time}'
