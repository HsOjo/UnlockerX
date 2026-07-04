from app.res.const import Const
from . import Language


class TraditionalChinese(Language):
    code = 'cn_t'
    l_this = '繁體中文'

    ok = '確定'
    cancel = '取消'
    none = '無'

    unit_dbm = 'dBm'

    status_normal = '已連線'
    status_weak = '訊號弱'
    status_disconnect = '已中斷'

    menu_bind_bluetooth_device = '綁定藍牙裝置'
    menu_pause = '暫停'
    menu_resume = '恢復'
    menu_preferences = '偏好設定'
    menu_set_weak_signal_value = '設定訊號弱臨界值'
    menu_set_weak_signal_lock_delay = '設定訊號弱鎖定延遲'
    menu_set_disconnect_lock_delay = '設定中斷連線鎖定延遲'
    menu_set_bluetooth_refresh_rate = '設定藍牙重新整理頻率'
    menu_set_unlock_delay = '設定解鎖延遲'
    menu_signal_value_visible_on_icon = '在圖示旁顯示訊號值'
    menu_set_password = '設定目前使用者密碼'
    menu_clear_password = '清除已儲存密碼'
    menu_set_startup = '設定登入啟動'
    menu_advanced_options = '進階選項'
    menu_export_log = '檢視日誌'
    menu_clear_config = '清空設定檔案'
    menu_select_language = '設定語言'
    menu_check_update = '檢查更新'
    menu_about = '關於'
    menu_quit = '結束'

    title_welcome = '歡迎使用'
    title_info = '資訊'
    title_crash = '應用程式當機'

    description_set_password = '''設定目前使用者的登入密碼。
將用於解鎖你的 Mac。'''
    description_password_warning = '''注意：密碼儲存在 macOS 鑰匙圈中。
由於本應用程式未簽署，該鑰匙圈項目允許任意本機程式存取，因此任何以你身分執行的程式都可讀取它。這是在無提權、免密自動解鎖下的既定取捨。'''
    description_password_incorrect = '''密碼不正確，未儲存。
請重試。'''
    description_select_language = '選擇你的語言。'
    description_bind_bluetooth_device = '選擇一台已配對的藍牙裝置進行綁定。'
    description_no_paired_device = '找不到已配對的藍牙裝置。請先到 "系統設定" - "藍牙" 配對你的裝置。'
    description_bluetooth_off = '藍牙已關閉。請先到 "系統設定" - "藍牙" 開啟藍牙。'
    description_set_weak_signal_value = '''訊號弱將觸發離開鎖屏倒數。
單位：dBm，訊號值越小，訊號越弱。'''
    description_set_weak_signal_lock_delay = '在藍牙裝置訊號弱時，觸發鎖屏延遲的時間。'
    description_set_disconnect_lock_delay = '在藍牙裝置中斷時，觸發鎖屏延遲的時間。'
    description_set_bluetooth_refresh_rate = '''藍牙重新整理間隔。
單位：秒，最小為 1 秒。'''
    description_set_unlock_delay = '裝置在場後解鎖前的延遲時間。'
    description_need_accessibility = f'''{Const.app_name} 需要 "輔助使用" 權限以模擬鍵入並解鎖你的 Mac。
請在接下來的視窗中，於 "隱私權與安全性" - "輔助使用" 啟用 {Const.app_name}。'''
    description_accessibility_enabled = f'''"輔助使用" 已啟用 {Const.app_name}。'''
    description_cancel_accessibility = f'''你略過了 "輔助使用"。{Const.app_name} 將只在離開時鎖屏，不會自動解鎖。'''
    description_welcome_pair_device = '在綁定藍牙裝置之前，請先在接下來的視窗中完成藍牙裝置的配對。'
    description_set_startup = '是否將本應用程式設為登入時自動啟動？'
    description_clear_config = '這將會刪除設定檔案，確定嗎？'
    description_clear_config_restart = '設定檔案已經被刪除，請重新啟動該應用程式。'
    description_clear_password_confirm = '從鑰匙圈中移除已儲存的密碼？'
    description_need_password = '未儲存密碼。請設定登入密碼以啟用自動解鎖。'
    description_about_confirm = '是否打開 GitHub 專案頁面？'

    prompt_input_password = '密碼：'

    noti_connected = '裝置已連線。'
    noti_disconnected = '裝置已中斷。'
    noti_weak_signal_lock = '訊號弱，正在鎖屏。'
    noti_unlock_success = '已自動解鎖。'
    noti_unlock_failed = '自動解鎖失敗。'
    noti_password_need = '解鎖失敗！請先設定密碼。'
    noti_unlock_error = '解鎖失敗次數過多，已自動暫停。請檢查密碼與 "輔助使用" 設定。'
    noti_update_none = '目前已是最新版本。'
    noti_update_star = '（如果你喜歡這個應用程式，請在 GitHub 給我個 star，thanks。）'
    noti_network_error = '網路出現問題，請稍後重試。'

    def view_device_name(self, name):
        return f'裝置名稱：{name}'

    def view_device_address(self, address):
        return f'裝置位址：{address}'

    def view_device_signal(self, signal):
        return f'裝置訊號：{signal}'

    def view_status(self, status):
        return f'狀態：{status}'

    description_about = f'''{Const.app_name} 版本 {Const.version}

使用藍牙裝置靠近以解鎖你的 Mac！

由 {Const.author} 開發。'''

    description_welcome_end = f'''很好！現在 {Const.app_name} 可以開始工作了。
Enjoy yourself!'''

    def noti_update_version(self, version):
        return f'發現新版本：{version}'

    def noti_update_time(self, release_time):
        return f'發佈時間：{release_time}'
