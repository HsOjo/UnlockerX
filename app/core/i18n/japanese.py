from app.res.const import Const
from . import Language


class Japanese(Language):
    code = 'jp'
    l_this = '日本語'

    ok = 'OK'
    cancel = 'キャンセル'
    none = 'なし'

    unit_dbm = 'dBm'

    status_normal = '接続済み'
    status_weak = '信号が弱い'
    status_disconnect = '切断'

    menu_bind_bluetooth_device = 'Bluetooth デバイスをバインド'
    menu_pause = '一時停止'
    menu_resume = '再開'
    menu_preferences = '環境設定'
    menu_set_weak_signal_value = '弱信号のしきい値を設定'
    menu_set_weak_signal_lock_delay = '弱信号ロック遅延を設定'
    menu_set_disconnect_lock_delay = '切断ロック遅延を設定'
    menu_set_bluetooth_refresh_rate = 'Bluetooth 更新間隔を設定'
    menu_set_unlock_delay = 'ロック解除遅延を設定'
    menu_signal_value_visible_on_icon = 'アイコンに信号値を表示'
    menu_set_password = '現在のユーザーパスワードを設定'
    menu_clear_password = '保存したパスワードを消去'
    menu_set_startup = 'ログイン時に起動'
    menu_advanced_options = '詳細オプション'
    menu_export_log = 'ログを表示'
    menu_clear_config = '設定をクリア'
    menu_select_language = '言語を設定'
    menu_check_update = 'アップデートを確認'
    menu_about = 'について'
    menu_quit = '終了'

    title_welcome = 'ようこそ'
    title_info = '情報'
    title_crash = 'アプリケーションクラッシュ'

    description_set_password = '''現在のユーザーのログインパスワードを設定します。
Mac のロック解除に使用されます。'''
    description_password_warning = '''注意：パスワードは macOS キーチェーンに保存されます。
このアプリは署名されていないため、キーチェーン項目は任意のローカルプロセスからアクセス可能で、あなたとして実行される任意のプログラムが読み取れます。これは権限昇格なしのパスワードレス自動ロック解除のための既定のトレードオフです。'''
    description_password_incorrect = '''パスワードが正しくありません。保存されませんでした。
もう一度お試しください。'''
    description_select_language = '言語を選択してください。'
    description_bind_bluetooth_device = 'バインドするペア済み Bluetooth デバイスを選択してください。'
    description_no_paired_device = 'ペア済みの Bluetooth デバイスが見つかりません。まず "システム設定" - "Bluetooth" でデバイスをペアリングしてください。'
    description_bluetooth_off = 'Bluetooth がオフになっています。"システム設定" - "Bluetooth" でオンにしてください。'
    description_set_weak_signal_value = '''弱信号は離席ロックのカウントダウンを開始します。
単位：dBm、値が小さいほど信号が弱くなります。'''
    description_set_weak_signal_lock_delay = 'デバイス信号が弱くなってから画面をロックするまでの遅延。'
    description_set_disconnect_lock_delay = 'デバイスが切断されてから画面をロックするまでの遅延。'
    description_set_bluetooth_refresh_rate = '''Bluetooth の更新間隔。
単位：秒、最小は 1 秒です。'''
    description_set_unlock_delay = 'デバイスが在圏になってからロック解除するまでの遅延。'
    description_need_accessibility = f'''{Const.app_name} はキー入力をシミュレートして Mac のロックを解除するため "アクセシビリティ" 権限が必要です。
次のウィンドウで "プライバシーとセキュリティ" - "アクセシビリティ" にて {Const.app_name} を有効にしてください。'''
    description_accessibility_enabled = f'''{Const.app_name} の "アクセシビリティ" は既に有効です。'''
    description_cancel_accessibility = f'''"アクセシビリティ" をスキップしました。{Const.app_name} は離席時のロックのみ行い、自動ロック解除はしません。'''
    description_welcome_pair_device = 'Bluetooth デバイスをバインドする前に、次のウィンドウでペアリングを完了してください。'
    description_set_startup = 'このアプリをログイン時に自動起動しますか？'
    description_clear_config = '設定ファイルを削除します。よろしいですか？'
    description_clear_config_restart = '設定ファイルを削除しました。アプリを再起動してください。'
    description_clear_password_confirm = 'キーチェーンから保存済みのパスワードを削除しますか？'
    description_need_password = '保存されたパスワードがありません。自動ロック解除を有効にするにはログインパスワードを設定してください。'
    description_about_confirm = 'GitHub プロジェクトページを開きますか？'

    prompt_input_password = 'パスワード：'

    noti_connected = 'デバイスが接続されました。'
    noti_disconnected = 'デバイスが切断されました。'
    noti_weak_signal_lock = '信号が弱いため、画面をロックします。'
    noti_unlock_success = '自動的にロック解除しました。'
    noti_unlock_failed = '自動ロック解除に失敗しました。'
    noti_password_need = 'ロック解除に失敗しました！パスワードを設定してください。'
    noti_unlock_error = 'ロック解除に何度も失敗したため自動的に一時停止しました。パスワードと "アクセシビリティ" 設定を確認してください。'
    noti_update_none = '現在は最新バージョンです。'
    noti_update_star = '（このアプリが気に入ったら GitHub でスターをください、ありがとう。）'
    noti_network_error = 'ネットワークに問題があるようです。後でもう一度お試しください。'

    def view_device_name(self, name):
        return f'デバイス名：{name}'

    def view_device_address(self, address):
        return f'デバイスアドレス：{address}'

    def view_device_signal(self, signal):
        return f'デバイス信号：{signal}'

    def view_status(self, status):
        return f'状態：{status}'

    description_about = f'''{Const.app_name} バージョン {Const.version}

Bluetooth デバイスで Mac を近接ロック解除！

{Const.author} による開発。'''

    description_welcome_end = f'''素晴らしい！{Const.app_name} が動作を開始しました。
お楽しみください！'''

    def noti_update_version(self, version):
        return f'アップデートが見つかりました：{version}'

    def noti_update_time(self, release_time):
        return f'リリース日時：{release_time}'
