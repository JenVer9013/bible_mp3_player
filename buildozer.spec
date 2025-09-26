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
android.sdk_path = /home/runner/android-sdk
android.ndk_path = /home/runner/android-sdk/ndk/21.4.7075529
android.api = 30
android.minapi = 21
android.ndk_api = 21

# build-tools 버전 명시 (빌드에 사용될 정확한 버전)
android.build_tools_version = 30.0.3

# AIDL 도구 경로 명시
android.aidl = /home/runner/android-sdk/build-tools/30.0.3/aidl