# UnlockerX

通过蓝牙设备靠近自动解锁你的 Mac。

* 绑定设备靠近时自动解锁 Mac。
* 设备离开、信号弱、合盖、系统空闲、显示器睡眠时自动锁屏。
* 使用 PyObjC/AppKit 原生菜单栏（无 rumps、无外部二进制）。
* 使用原生 `IOBluetooth` 读取连接状态与 RSSI（无 blueutil / BluetoothConnector）。
* 密码存储在 macOS 钥匙串中，不再本地伪加密。
* 启动时或手动检查更新。

事件驱动状态机，PyObjC/AppKit 原生实现，无外部二进制。

> 需要 **macOS 10.15+**。源码运行需 **Python 3.12+**。

* 多语言支持：英文、简体中文、繁体中文、日文、韩文。

## 安全说明

本应用必须知道你的 macOS 登录密码，才能在锁屏界面键入以解锁。密码保存在 macOS 钥匙串中。由于应用**未签名**，钥匙串项的 ACL 设置为允许所有本机进程静默读取，这是「无提权、不改系统授权链」实现自动解锁的既定取舍。

如无法接受，请勿使用自动解锁功能。未授予「辅助功能」权限时，应用仍会在离开时锁屏，但不会自动解锁。

## 权限

* **辅助功能** — 模拟键入解锁必需。未授予时仅锁屏、不解锁。
* **蓝牙** — 读取绑定设备的连接状态与 RSSI 必需。

## 下载

见 [Releases Page](../../releases)。

## 首次打开（未签名应用）

UnlockerX 以未签名方式分发。首次启动时 Gatekeeper 会拒绝打开。可以**右键点击应用 → 打开**，或清除隔离属性：

```bash
xattr -dr com.apple.quarantine /Applications/UnlockerX.app
```

## 如何构建

需要 Python 3.12 与 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --extra build
uv run python build.py          # 产出 dist/UnlockerX.app 与 dist/UnlockerX-<version>.zip
```

## 提交 Bug

导出日志（偏好设置 → 高级选项），并附到 GitHub issue。导出的日志会屏蔽隐私数据。
