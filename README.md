# UnlockerX

Near unlock your Mac by Bluetooth device!

> This program can work normally in macOS **10.14/10.15/11**.

* Multiple language support ! ! !
  * English
  * Simple Chinese
  * Tradtional Chinese
  * Japanese (By Translater)
  * Korean (By Translater)

* Events callback execute custom program support !!!
  * Weak Signal
  * Connect Status Changed
  * Lock Status Changed
  * Lid Status Changed

Base on above contents, You can free to extend this program. (example code on folder "/docs/".)

![Thumbnail](docs/img/thumbnail_en.png)

## Downloads

Please view [Releases Page](../../releases).

## Some Problems

* After macOS 10.15, Sometimes can not unlock normally. (Like password edit unfocused.)
  * You can set unlock delay time (in "Preferences" - "Advanced Options") to solve this problem. (maybe)

## How To Build

* Install Requirement.

```bash
pip3 install -r requirements.txt
```

* Build

```bash
python3 build.py [--translate-baidu] [--py2app]
```

## Report Bug

If you meet some bug in this app, You can try to export log (in "Preferences" - "Advanced Options"), and send to this project issues page.

It will be export log file to directory, your private data will replace with hider text.

And the next step, you can send this log file on this project' s GitHub page issues.
