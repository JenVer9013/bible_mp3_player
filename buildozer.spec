[app]
title = Bible MP3 Player
package.name = bible_mp3_player
package.domain = com.bible.mp3player
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,db
version = 1.0
requirements = python3,kivy,requests
orientation = portrait

[buildozer]
log_level = 1

[app:android]
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.arch = armeabi-v7a

# Android SDK/NDK 경로 설정
android.api = 30
android.minapi = 21
android.ndk_api = 21

# build-tools 버전 강제 지정
# 여러 버전을 명시하여 buildozer가 선택하도록 함
android.build_tools_version = 30.0.3
android.gradle_version = 7.4.2
android.gradle_plugin_version = 7.4.2

# buildozer 내부 설정 강제 지정
android.skip_update = False
android.accept_sdk_license = True

# 로그 레벨 증가 (디버깅용)
log_level = 2