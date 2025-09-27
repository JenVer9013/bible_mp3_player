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

# Android SDK/NDK 경로 설정 (GitHub Actions 기본 SDK 사용)
# ANDROID_SDK_ROOT 환경변수를 사용하도록 설정
android.api = 30
android.minapi = 21
android.ndk_api = 21

# build-tools 버전 강제 지정 (36.1 버전 요청 방지)
android.build_tools_version = 30.0.3
android.gradle_version = 7.4.2
android.gradle_plugin_version = 7.4.2

# SDK 경로 강제 지정
android.sdk_path = /opt/android-sdk-linux
android.ndk_path = /opt/android-sdk-linux/ndk/21.4.7075529

# AIDL 및 기타 도구 경로 명시
android.aidl = /opt/android-sdk-linux/build-tools/30.0.3/aidl
android.aapt = /opt/android-sdk-linux/build-tools/30.0.3/aapt
android.dx = /opt/android-sdk-linux/build-tools/30.0.3/dx
android.zipalign = /opt/android-sdk-linux/build-tools/30.0.3/zipalign