import os


class Const:
    author = 'HsOjo'
    app_name = 'UnlockerX'
    version = '2.0.0'

    bundle_id = f'com.{author}.{app_name}'.lower()
    github_page = f'https://github.com/{author}/{app_name}'
    releases_url = f'{github_page}/releases'

    # Keychain service name for the stored login password.
    keychain_service = f'{bundle_id}.password'

    # LaunchAgent label and plist path for login startup.
    agent_label = bundle_id
    launch_agent_plist = os.path.expanduser(f'~/Library/LaunchAgents/{agent_label}.plist')

    # Config/log directories under ~/Library/Application Support/<bundle_id>.
    config_dir = os.path.expanduser(f'~/Library/Application Support/{bundle_id}')
    config_path = os.path.join(config_dir, 'config.json')
    log_dir = os.path.join(config_dir, 'logs')
    log_path = os.path.join(log_dir, f'{app_name}.log')

    idle_time = 30
    idle_time_short = 2
    unlock_count_limit = 3
