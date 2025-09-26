#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성경 MP3 플레이어 - Kivy 버전 (안드로이드 지원)
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
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import sqlite3
import os
import glob
from pathlib import Path

class BibleMP3PlayerKivy(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 초기 설정
        self.current_file = None
        self.current_sound = None
        self.current_position = 0
        self.is_playing = False
        self.playback_speed = 1.0
        self.volume = 0.7
        
        # 경로 설정
        self.mp3_base_path = "/storage/emulated/0/Bible_mp3"  # 안드로이드 경로
        self.db_path = "/storage/emulated/0/full_bible.db"

        # 윈도우에서는 현재 디렉토리 사용
        if os.name == 'nt':
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.mp3_base_path = "C:/Users/yong9/projects/Bible_mp3"
            self.db_path = os.path.join(current_dir, "full_bible.db")
        
        self.current_book = None
        self.current_chapter = 1
        
        self.setup_ui()
        self.load_books()
        
        # 업데이트 스케줄러
        Clock.schedule_interval(self.update_position, 0.1)
    
    def setup_ui(self):
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
        
        self.add_widget(selection_layout)
        
        # 현재 재생 정보
        self.info_label = Label(text="재생할 파일을 선택하세요", size_hint_y=None, height=40, 
                               text_size=(None, None), halign="center")
        self.add_widget(self.info_label)
        
        # 진행바
        progress_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        self.progress_bar = ProgressBar(max=100, value=0)
        progress_layout.add_widget(self.progress_bar)
        self.time_label = Label(text="00:00 / 00:00", size_hint_x=None, width=100)
        progress_layout.add_widget(self.time_label)
        self.add_widget(progress_layout)
        
        # 재생 제어 버튼
        control_layout = GridLayout(cols=5, size_hint_y=None, height=60, spacing=5)
        
        control_layout.add_widget(Button(text="⏮", on_press=self.prev_chapter))
        control_layout.add_widget(Button(text="⏪", on_press=self.rewind))
        
        self.play_button = Button(text="▶", on_press=self.toggle_play)
        control_layout.add_widget(self.play_button)
        
        control_layout.add_widget(Button(text="⏩", on_press=self.fast_forward))
        control_layout.add_widget(Button(text="⏭", on_press=self.next_chapter))
        
        self.add_widget(control_layout)
        
        # 속도 조절
        speed_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
        speed_layout.add_widget(Label(text="재생 속도", size_hint_y=None, height=30))
        
        # 속도 슬라이더
        slider_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        slider_layout.add_widget(Label(text="0.1x", size_hint_x=None, width=40))
        
        self.speed_slider = Slider(min=10, max=100, value=50, size_hint_x=1)
        self.speed_slider.bind(value=self.on_speed_change)
        slider_layout.add_widget(self.speed_slider)
        
        slider_layout.add_widget(Label(text="3.0x", size_hint_x=None, width=40))
        speed_layout.add_widget(slider_layout)
        
        # 정확한 속도 입력
        exact_layout = BoxLayout(size_hint_y=None, height=30, spacing=5)
        exact_layout.add_widget(Label(text="정확한 속도(%):", size_hint_x=0.4))
        
        self.speed_input = TextInput(text="100.00", size_hint_x=0.3, multiline=False)
        exact_layout.add_widget(self.speed_input)
        
        exact_layout.add_widget(Button(text="적용", size_hint_x=0.3, on_press=self.apply_exact_speed))
        speed_layout.add_widget(exact_layout)
        
        # 속도 표시
        self.speed_label = Label(text="속도: 100.00%", size_hint_y=None, height=30)
        speed_layout.add_widget(self.speed_label)
        
        self.add_widget(speed_layout)
        
        # 볼륨 조절
        volume_layout = BoxLayout(size_hint_y=None, height=60, spacing=5)
        volume_layout.add_widget(Label(text="볼륨:", size_hint_x=None, width=50))
        
        self.volume_slider = Slider(min=0, max=100, value=70, size_hint_x=1)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(self.volume_slider)
        
        self.volume_label = Label(text="70%", size_hint_x=None, width=50)
        volume_layout.add_widget(self.volume_label)
        
        self.add_widget(volume_layout)
        
        # 성경 본문
        text_layout = BoxLayout(orientation='vertical', spacing=5)
        text_layout.add_widget(Label(text="성경 본문", size_hint_y=None, height=30))
        
        scroll = ScrollView()
        self.bible_text = Label(text="성경 본문이 여기에 표시됩니다.", 
                               text_size=(None, None), halign="left", valign="top")
        scroll.add_widget(self.bible_text)
        text_layout.add_widget(scroll)
        
        self.add_widget(text_layout)
    
    def load_books(self):
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
        book_path = os.path.join(self.mp3_base_path, text)
        
        chapters = []
        if os.path.exists(book_path):
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
        
        mp3_file = os.path.join(self.mp3_base_path, self.current_book, f"{text.zfill(2)}.mp3")
        
        if os.path.exists(mp3_file):
            self.current_file = mp3_file
            self.info_label.text = f"{self.current_book} {self.current_chapter}장"
            self.load_bible_text()
    
    def load_bible_text(self):
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
            
            # 텍스트 크기 조정
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
        pass  # Kivy SoundLoader 제한
    
    def fast_forward(self, btn):
        pass  # Kivy SoundLoader 제한
    
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

class BibleMP3App(App):
    def build(self):
        return BibleMP3PlayerKivy()

if __name__ == "__main__":
    BibleMP3App().run()