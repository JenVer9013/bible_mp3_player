#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성경 MP3 플레이어 - OneDrive 연동 Kivy 버전
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.network.urlrequest import UrlRequest
import sqlite3
import os
import json
import threading
import time
from pathlib import Path
from onedrive_api import SimplifiedOneDriveAuth

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # 제목
        title = Label(text='성경 MP3 플레이어', font_size=24, size_hint_y=None, height=60)
        layout.add_widget(title)
        
        # 로그인 설명
        info = Label(
            text='OneDrive 계정에 로그인하여\\n성경 음성파일에 액세스하세요',
            size_hint_y=None, height=80, halign='center'
        )
        info.text_size = (None, None)
        layout.add_widget(info)
        
        # 로그인 폼
        form_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        form_layout.add_widget(Label(text='이메일:', size_hint_y=None, height=40))
        self.email_input = TextInput(
            multiline=False, size_hint_y=None, height=40,
            hint_text='your@email.com'
        )
        form_layout.add_widget(self.email_input)
        
        form_layout.add_widget(Label(text='비밀번호:', size_hint_y=None, height=40))
        self.password_input = TextInput(
            multiline=False, password=True, size_hint_y=None, height=40,
            hint_text='password'
        )
        form_layout.add_widget(self.password_input)
        
        layout.add_widget(form_layout)
        
        # 로그인 버튼
        self.login_button = Button(
            text='로그인', size_hint_y=None, height=50,
            on_press=self.login
        )
        layout.add_widget(self.login_button)
        
        # 상태 표시
        self.status_label = Label(
            text='', size_hint_y=None, height=40,
            color=(1, 0, 0, 1)  # 빨간색
        )
        layout.add_widget(self.status_label)
        
        # 오프라인 모드 버튼
        offline_button = Button(
            text='오프라인 모드 (로컬 파일)', size_hint_y=None, height=50,
            on_press=self.offline_mode
        )
        layout.add_widget(offline_button)
        
        self.add_widget(layout)
        
        # OneDrive 인증 객체
        self.onedrive_auth = SimplifiedOneDriveAuth()
    
    def login(self, btn):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        
        if not email or not password:
            self.status_label.text = '이메일과 비밀번호를 입력하세요.'
            return
        
        self.login_button.text = '로그인 중...'
        self.login_button.disabled = True
        
        # 별도 스레드에서 로그인 처리
        threading.Thread(target=self._login_thread, args=(email, password), daemon=True).start()
    
    def _login_thread(self, email, password):
        """로그인 처리 스레드"""
        success = self.onedrive_auth.login_with_credentials(email, password)
        
        # UI 업데이트는 메인 스레드에서
        Clock.schedule_once(lambda dt: self._login_complete(success), 0)
    
    def _login_complete(self, success):
        """로그인 완료 처리"""
        self.login_button.disabled = False
        self.login_button.text = '로그인'
        
        if success:
            self.status_label.text = '로그인 성공!'
            self.status_label.color = (0, 1, 0, 1)  # 초록색
            
            # 메인 화면으로 이동
            app = App.get_running_app()
            app.root.current = 'player'
            app.root.get_screen('player').setup_onedrive_mode(self.onedrive_auth)
        else:
            self.status_label.text = '로그인 실패. 다시 시도하세요.'
            self.status_label.color = (1, 0, 0, 1)  # 빨간색
    
    def offline_mode(self, btn):
        """오프라인 모드로 진입"""
        app = App.get_running_app()
        app.root.current = 'player'
        app.root.get_screen('player').setup_offline_mode()

class PlayerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'player'
        
        # 초기 설정
        self.current_file = None
        self.current_sound = None
        self.current_position = 0
        self.is_playing = False
        self.playback_speed = 1.0
        self.volume = 0.7
        
        # 모드 설정
        self.is_online_mode = False
        self.onedrive_auth = None
        
        # 경로 설정 (오프라인 모드용)
        self.mp3_base_path = "/storage/emulated/0/Bible_mp3"
        self.db_path = "/storage/emulated/0/full_bible.db"

        if os.name == 'nt':  # Windows
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.mp3_base_path = "C:/Users/yong9/projects/Bible_mp3"
            self.db_path = os.path.join(current_dir, "full_bible.db")
        
        self.current_book = None
        self.current_chapter = 1
        
        # OneDrive 파일 목록 캐시
        self.onedrive_files = {}
        
        self.setup_ui()
        Clock.schedule_interval(self.update_position, 0.1)
    
    def setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 뒤로 가기 버튼
        back_button = Button(text='← 로그인 화면', size_hint_y=None, height=40,
                           on_press=self.go_back)
        main_layout.add_widget(back_button)
        
        # 모드 표시
        self.mode_label = Label(text='모드: 초기화 중...', size_hint_y=None, height=30)
        main_layout.add_widget(self.mode_label)
        
        # 책/장 선택
        selection_layout = GridLayout(cols=4, size_hint_y=None, height=50, spacing=5)
        
        selection_layout.add_widget(Label(text="책:", size_hint_x=0.2))
        self.book_spinner = Spinner(text="책 선택", size_hint_x=0.4)
        self.book_spinner.bind(text=self.on_book_selected)
        selection_layout.add_widget(self.book_spinner)
        
        selection_layout.add_widget(Label(text="장:", size_hint_x=0.2))
        self.chapter_spinner = Spinner(text="장 선택", size_hint_x=0.2)
        self.chapter_spinner.bind(text=self.on_chapter_selected)
        selection_layout.add_widget(self.chapter_spinner)
        
        main_layout.add_widget(selection_layout)
        
        # 현재 재생 정보
        self.info_label = Label(text="재생할 파일을 선택하세요", size_hint_y=None, height=40)
        main_layout.add_widget(self.info_label)
        
        # 진행바
        progress_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        self.progress_bar = ProgressBar(max=100, value=0)
        progress_layout.add_widget(self.progress_bar)
        self.time_label = Label(text="00:00 / 00:00", size_hint_x=None, width=100)
        progress_layout.add_widget(self.time_label)
        main_layout.add_widget(progress_layout)
        
        # 재생 제어 버튼
        control_layout = GridLayout(cols=5, size_hint_y=None, height=60, spacing=5)
        
        control_layout.add_widget(Button(text="⏮", on_press=self.prev_chapter))
        control_layout.add_widget(Button(text="⏪", on_press=self.rewind))
        
        self.play_button = Button(text="▶", on_press=self.toggle_play)
        control_layout.add_widget(self.play_button)
        
        control_layout.add_widget(Button(text="⏩", on_press=self.fast_forward))
        control_layout.add_widget(Button(text="⏭", on_press=self.next_chapter))
        
        main_layout.add_widget(control_layout)
        
        # 속도 조절
        speed_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        speed_layout.add_widget(Label(text="재생 속도", size_hint_y=None, height=30))
        
        slider_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        slider_layout.add_widget(Label(text="0.1x", size_hint_x=None, width=40))
        
        self.speed_slider = Slider(min=10, max=100, value=50, size_hint_x=1)
        self.speed_slider.bind(value=self.on_speed_change)
        slider_layout.add_widget(self.speed_slider)
        
        slider_layout.add_widget(Label(text="3.0x", size_hint_x=None, width=40))
        speed_layout.add_widget(slider_layout)
        
        exact_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        exact_layout.add_widget(Label(text="정확한 속도(%):", size_hint_x=0.4))
        
        self.speed_input = TextInput(text="100.00", size_hint_x=0.3, multiline=False)
        exact_layout.add_widget(self.speed_input)
        
        exact_layout.add_widget(Button(text="적용", size_hint_x=0.3, on_press=self.apply_exact_speed))
        speed_layout.add_widget(exact_layout)
        
        self.speed_label = Label(text="속도: 100.00%", size_hint_y=None, height=30)
        speed_layout.add_widget(self.speed_label)
        
        main_layout.add_widget(speed_layout)
        
        # 볼륨 조절
        volume_layout = BoxLayout(size_hint_y=None, height=60, spacing=5)
        volume_layout.add_widget(Label(text="볼륨:", size_hint_x=None, width=50))
        
        self.volume_slider = Slider(min=0, max=100, value=70, size_hint_x=1)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(self.volume_slider)
        
        self.volume_label = Label(text="70%", size_hint_x=None, width=50)
        volume_layout.add_widget(self.volume_label)
        
        main_layout.add_widget(volume_layout)
        
        # 성경 본문
        text_layout = BoxLayout(orientation='vertical', spacing=5)
        text_layout.add_widget(Label(text="성경 본문", size_hint_y=None, height=30))
        
        scroll = ScrollView()
        self.bible_text = Label(text="성경 본문이 여기에 표시됩니다.", 
                               text_size=(None, None), halign="left", valign="top")
        scroll.add_widget(self.bible_text)
        text_layout.add_widget(scroll)
        
        main_layout.add_widget(text_layout)
        
        self.add_widget(main_layout)
    
    def setup_onedrive_mode(self, onedrive_auth):
        """OneDrive 온라인 모드 설정"""
        self.is_online_mode = True
        self.onedrive_auth = onedrive_auth
        self.mode_label.text = '모드: OneDrive 온라인'
        self.mode_label.color = (0, 0, 1, 1)  # 파란색
        
        # OneDrive에서 파일 목록 로드
        self.load_onedrive_books()
    
    def setup_offline_mode(self):
        """오프라인 모드 설정"""
        self.is_online_mode = False
        self.mode_label.text = '모드: 로컬 파일 (오프라인)'
        self.mode_label.color = (0.5, 0.5, 0.5, 1)  # 회색
        
        # 로컬 파일 목록 로드
        self.load_local_books()
    
    def load_onedrive_books(self):
        """OneDrive에서 책 목록 로드"""
        if not self.onedrive_auth:
            return
        
        # 별도 스레드에서 OneDrive 파일 로드
        threading.Thread(target=self._load_onedrive_thread, daemon=True).start()
    
    def _load_onedrive_thread(self):
        """OneDrive 파일 로드 스레드"""
        share_url = "https://1drv.ms/f/c/6c009c9cb6fd0d59/ElWWFuWVuppPrdrWrcWKo7IBtRBnvUF1fPXwcMo3btpv0A?e=30KG3f"
        files = self.onedrive_auth.get_shared_files(share_url)
        
        # 파일 구조를 변환
        books = []
        for file_item in files:
            if file_item.get('type') == 'folder':
                book_name = file_item['name']
                books.append(book_name)
                self.onedrive_files[book_name] = file_item.get('children', [])
        
        # UI 업데이트는 메인 스레드에서
        Clock.schedule_once(lambda dt: self._update_books_ui(books), 0)
    
    def _update_books_ui(self, books):
        """책 목록 UI 업데이트"""
        self.book_spinner.values = books
        if books:
            self.book_spinner.text = books[0]
            self.on_book_selected(self.book_spinner, books[0])
    
    def load_local_books(self):
        """로컬에서 책 목록 로드"""
        books = []
        if os.path.exists(self.mp3_base_path):
            for folder in sorted(os.listdir(self.mp3_base_path)):
                if os.path.isdir(os.path.join(self.mp3_base_path, folder)):
                    books.append(folder)
        
        self.book_spinner.values = books
        if books:
            self.book_spinner.text = books[0]
            self.on_book_selected(self.book_spinner, books[0])
    
    def on_book_selected(self, spinner, text):
        self.current_book = text
        
        if self.is_online_mode:
            # OneDrive 모드
            chapters = []
            if text in self.onedrive_files:
                for file_item in self.onedrive_files[text]:
                    if file_item.get('name', '').endswith('.mp3'):
                        try:
                            chapter_num = int(file_item['name'].split('.')[0])
                            chapters.append(str(chapter_num))
                        except ValueError:
                            continue
        else:
            # 오프라인 모드
            book_path = os.path.join(self.mp3_base_path, text)
            chapters = []
            if os.path.exists(book_path):
                import glob
                mp3_files = glob.glob(os.path.join(book_path, "*.mp3"))
                chapter_numbers = []
                for mp3_file in mp3_files:
                    filename = os.path.basename(mp3_file)
                    try:
                        chapter_num = int(filename.split('.')[0])
                        chapter_numbers.append(chapter_num)
                    except ValueError:
                        continue
                chapters = [str(i) for i in sorted(chapter_numbers)]
        
        self.chapter_spinner.values = chapters
        if chapters:
            self.chapter_spinner.text = chapters[0]
            self.on_chapter_selected(self.chapter_spinner, chapters[0])
    
    def on_chapter_selected(self, spinner, text):
        if not text or not self.current_book:
            return
            
        self.current_chapter = int(text)
        
        if self.is_online_mode:
            # OneDrive에서 파일 찾기
            if self.current_book in self.onedrive_files:
                for file_item in self.onedrive_files[self.current_book]:
                    if file_item.get('name') == f"{text.zfill(2)}.mp3":
                        self.current_file = file_item.get('download_url')
                        break
        else:
            # 로컬 파일
            mp3_file = os.path.join(self.mp3_base_path, self.current_book, f"{text.zfill(2)}.mp3")
            if os.path.exists(mp3_file):
                self.current_file = mp3_file
        
        if self.current_file:
            self.info_label.text = f"{self.current_book} {self.current_chapter}장"
            if not self.is_online_mode:
                self.load_bible_text()
    
    def load_bible_text(self):
        """데이터베이스에서 성경 본문 로드 (오프라인 모드만)"""
        if self.is_online_mode:
            self.bible_text.text = "온라인 모드에서는 성경 본문을 표시하지 않습니다."
            return
        
        if not os.path.exists(self.db_path):
            self.bible_text.text = "성경 데이터베이스를 찾을 수 없습니다."
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            book_name = self.current_book
            if '(' in book_name and ')' in book_name:
                english_name = book_name.split('(')[1].split(')')[0]
            else:
                english_name = book_name
            
            cursor.execute("""
                SELECT verse, text FROM bible_verses 
                WHERE book_short LIKE ? AND chapter = ?
                ORDER BY verse
            """, (f"%{english_name}%", self.current_chapter))
            
            verses = cursor.fetchall()
            
            if verses:
                text = ""
                for verse_num, verse_text in verses:
                    text += f"{verse_num}. {verse_text}\\n\\n"
                self.bible_text.text = text
            else:
                self.bible_text.text = f"{self.current_book} {self.current_chapter}장의 본문을 찾을 수 없습니다."
            
            self.bible_text.text_size = (self.bible_text.parent.width - 20, None) if self.bible_text.parent else (None, None)
            
            conn.close()
            
        except Exception as e:
            self.bible_text.text = f"데이터베이스 오류: {str(e)}"
    
    def toggle_play(self, btn):
        if not self.current_file:
            return
        
        if self.is_playing:
            if self.current_sound:
                self.current_sound.stop()
            self.is_playing = False
            self.play_button.text = "▶"
        else:
            if self.is_online_mode:
                # 온라인 스트리밍 재생
                self.current_sound = SoundLoader.load(self.current_file)
            else:
                # 로컬 파일 재생
                self.current_sound = SoundLoader.load(self.current_file)
            
            if self.current_sound:
                self.current_sound.volume = self.volume
                self.current_sound.play()
                self.is_playing = True
                self.play_button.text = "⏸"
    
    def prev_chapter(self, btn):
        if self.current_chapter > 1:
            chapters = self.chapter_spinner.values
            current_idx = chapters.index(str(self.current_chapter)) if str(self.current_chapter) in chapters else -1
            if current_idx > 0:
                self.chapter_spinner.text = chapters[current_idx - 1]
                self.on_chapter_selected(self.chapter_spinner, chapters[current_idx - 1])
    
    def next_chapter(self, btn):
        chapters = self.chapter_spinner.values
        current_idx = chapters.index(str(self.current_chapter)) if str(self.current_chapter) in chapters else -1
        if current_idx < len(chapters) - 1:
            self.chapter_spinner.text = chapters[current_idx + 1]
            self.on_chapter_selected(self.chapter_spinner, chapters[current_idx + 1])
    
    def rewind(self, btn):
        pass
    
    def fast_forward(self, btn):
        pass
    
    def on_speed_change(self, slider, value):
        slider_val = float(value)
        if slider_val <= 50:
            speed = 0.1 + (slider_val - 10) / 40 * 0.9
        else:
            speed = 1.0 + (slider_val - 50) / 50 * 2.0
        
        self.playback_speed = speed
        self.speed_label.text = f"속도: {speed:.2f}x ({speed*100:.2f}%)"
        self.speed_input.text = f"{speed*100:.2f}"
    
    def apply_exact_speed(self, btn):
        try:
            speed_percent = float(self.speed_input.text)
            speed = speed_percent / 100
            
            if speed < 10 or speed > 1000:
                return
            
            self.playback_speed = speed
            self.speed_label.text = f"속도: {speed:.2f}x ({speed_percent:.2f}%)"
            
            if speed <= 1.0:
                slider_val = 10 + (speed - 0.1) / 0.9 * 40
            else:
                slider_val = 50 + (speed - 1.0) / 2.0 * 50
            
            self.speed_slider.value = min(100, max(10, slider_val))
            
        except ValueError:
            pass
    
    def on_volume_change(self, slider, value):
        self.volume = value / 100
        self.volume_label.text = f"{int(value)}%"
        if self.current_sound:
            self.current_sound.volume = self.volume
    
    def update_position(self, dt):
        if self.is_playing and self.current_sound:
            if self.current_sound.state == 'stop':
                self.is_playing = False
                self.play_button.text = "▶"
    
    def go_back(self, btn):
        """로그인 화면으로 돌아가기"""
        if self.current_sound:
            self.current_sound.stop()
        self.is_playing = False
        self.play_button.text = "▶"
        
        App.get_running_app().root.current = 'login'

class BibleMP3OneDriveApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(PlayerScreen())
        return sm

if __name__ == "__main__":
    BibleMP3OneDriveApp().run()