from app.res.const import Const
from . import Language


class Korean(Language):
    code = 'ko'
    l_this = '한국어'

    ok = '확인'
    cancel = '취소'
    none = '없음'

    unit_dbm = 'dBm'

    status_normal = '연결됨'
    status_weak = '약한 신호'
    status_disconnect = '연결 끊김'

    menu_bind_bluetooth_device = '블루투스 장치 바인딩'
    menu_pause = '일시 중지'
    menu_resume = '재개'
    menu_preferences = '환경설정'
    menu_set_weak_signal_value = '약한 신호 임계값 설정'
    menu_set_weak_signal_lock_delay = '약한 신호 잠금 지연 설정'
    menu_set_disconnect_lock_delay = '연결 끊김 잠금 지연 설정'
    menu_set_bluetooth_refresh_rate = '블루투스 새로 고침 주기 설정'
    menu_set_unlock_delay = '잠금 해제 지연 설정'
    menu_signal_value_visible_on_icon = '아이콘에 신호 값 표시'
    menu_set_password = '현재 사용자 비밀번호 설정'
    menu_clear_password = '저장된 비밀번호 지우기'
    menu_set_startup = '로그인 시 시작 설정'
    menu_advanced_options = '고급 옵션'
    menu_export_log = '로그 보기'
    menu_clear_config = '설정 지우기'
    menu_select_language = '언어 설정'
    menu_check_update = '업데이트 확인'
    menu_about = '정보'
    menu_quit = '종료'

    title_welcome = '환영합니다'
    title_info = '정보'
    title_crash = '애플리케이션 충돌'

    description_set_password = '''현재 사용자의 로그인 비밀번호를 설정하세요.
Mac 잠금 해제에 사용됩니다.'''
    description_password_warning = '''참고: 비밀번호는 macOS 키체인에 저장됩니다.
이 앱은 서명되지 않았기 때문에 키체인 항목은 모든 로컬 프로세스의 접근을 허용하며, 사용자 권한으로 실행되는 모든 프로그램이 읽을 수 있습니다. 이는 권한 상승 없는 비밀번호 없는 자동 잠금 해제를 위한 절충안입니다.'''
    description_password_incorrect = '''비밀번호가 올바르지 않아 저장되지 않았습니다.
다시 시도하세요.'''
    description_select_language = '언어를 선택하세요.'
    description_bind_bluetooth_device = '바인딩할 페어링된 블루투스 장치를 선택하세요.'
    description_no_paired_device = '페어링된 블루투스 장치를 찾을 수 없습니다. 먼저 "시스템 설정" - "블루투스"에서 장치를 페어링하세요.'
    description_bluetooth_off = '블루투스가 꺼져 있습니다. "시스템 설정" - "블루투스"에서 켜주세요.'
    description_set_weak_signal_value = '''약한 신호는 자리 비움 잠금 카운트다운을 시작합니다.
단위: dBm, 값이 작을수록 신호가 약합니다.'''
    description_set_weak_signal_lock_delay = '장치 신호가 약해진 후 화면을 잠그기까지의 지연.'
    description_set_disconnect_lock_delay = '장치 연결이 끊긴 후 화면을 잠그기까지의 지연.'
    description_set_bluetooth_refresh_rate = '''블루투스 새로 고침 주기.
단위: 초, 최소 1초.'''
    description_set_unlock_delay = '장치가 근처에 있은 후 잠금 해제까지의 지연.'
    description_need_accessibility = f'''{Const.app_name}는 키 입력을 시뮬레이션하여 Mac 잠금을 해제하기 위해 "손쉬운 사용" 권한이 필요합니다.
다음 창의 "개인 정보 보호 및 보안" - "손쉬운 사용"에서 {Const.app_name}를 활성화하세요.'''
    description_accessibility_enabled = f'''{Const.app_name}의 "손쉬운 사용"이 이미 활성화되어 있습니다.'''
    description_cancel_accessibility = f'''"손쉬운 사용"을 걸너뛰었습니다. {Const.app_name}는 자리 비움 시 잠금만 하고 자동 잠금 해제는 하지 않습니다.'''
    description_welcome_pair_device = '블루투스 장치를 바인딩하기 전에 다음 창에서 페어링을 완료하세요.'
    description_set_startup = '로그인 시 이 앱을 자동으로 시작하시겠습니까?'
    description_clear_config = '설정 파일을 삭제합니다. 계속하시겠습니까?'
    description_clear_config_restart = '설정 파일이 삭제되었습니다. 앱을 다시 시작하세요.'
    description_clear_password_confirm = '키체인에서 저장된 비밀번호를 제거하시겠습니까?'
    description_need_password = '저장된 비밀번호가 없습니다. 자동 잠금 해제를 사용하려면 로그인 비밀번호를 설정하세요.'
    description_about_confirm = 'GitHub 프로젝트 페이지를 열겠습니까?'

    prompt_input_password = '비밀번호:'

    noti_connected = '장치가 연결되었습니다.'
    noti_disconnected = '장치 연결이 끊겼습니다.'
    noti_weak_signal_lock = '신호가 약해 화면을 잠급니다.'
    noti_unlock_success = '자동으로 잠금 해제되었습니다.'
    noti_unlock_failed = '자동 잠금 해제에 실패했습니다.'
    noti_password_need = '잠금 해제 실패! 비밀번호를 설정하세요.'
    noti_unlock_error = '잠금 해제에 여러 번 실패하여 자동으로 일시 중지되었습니다. 비밀번호와 "손쉬운 사용" 설정을 확인하세요.'
    noti_update_none = '현재 최신 버전입니다.'
    noti_update_star = '(이 앱이 마음에 드신다면 GitHub에서 별을 눌러주세요, 감사합니다.)'
    noti_network_error = '네트워크에 문제가 있을 수 있습니다. 나중에 다시 시도하세요.'

    def view_device_name(self, name):
        return f'장치 이름: {name}'

    def view_device_address(self, address):
        return f'장치 주소: {address}'

    def view_device_signal(self, signal):
        return f'장치 신호: {signal}'

    def view_status(self, status):
        return f'상태: {status}'

    description_about = f'''{Const.app_name} 버전 {Const.version}

블루투스 장치로 Mac을 근접 잠금 해제하세요!

{Const.author} 개발.'''

    description_welcome_end = f'''훌륭합니다! 이제 {Const.app_name}가 작동합니다.
즐기세요!'''

    def noti_update_version(self, version):
        return f'업데이트 발견: {version}'

    def noti_update_time(self, release_time):
        return f'출시 시간: {release_time}'
