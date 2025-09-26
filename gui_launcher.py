#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 런처 - 콘솔 한글 깨짐 문제 완전 해결
tkinter GUI로 모든 콘솔 문제 우회
"""
import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

class BibleMP3Launcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("성경 MP3 플레이어 런처")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # 아이콘 설정 (있다면)
        try:
            # 아이콘이 있다면 설정
            pass
        except:
            pass
        
        self.current_dir = Path(__file__).parent
        self.setup_gui()
        self.check_system()
    
    def setup_gui(self):
        """GUI 구성"""
        # 제목
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🎵 성경 MP3 플레이어", 
            font=('맑은 고딕', 18, 'bold'),
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            title_frame,
            text="한국어 음성 성경 - 속도 조절 및 OneDrive 연동",
            font=('맑은 고딕', 10),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        subtitle_label.pack()
        
        # 메인 컨테이너
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 상태 표시
        status_frame = tk.LabelFrame(main_frame, text="시스템 상태", font=('맑은 고딕', 10), bg='#f0f0f0')
        status_frame.pack(fill='x', pady=(0, 15))
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame, 
            height=6, 
            wrap=tk.WORD,
            font=('맑은 고딕', 9),
            bg='#ffffff',
            fg='#2c3e50'
        )
        self.status_text.pack(fill='x', padx=10, pady=10)
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='both', expand=True)
        
        # 실행 버튼들
        self.create_button(
            button_frame, 
            "🎵 기본 플레이어 실행", 
            "로컬 MP3 파일 재생 + 성경 본문 표시",
            '#3498db',
            lambda: self.run_player('basic')
        ).pack(fill='x', pady=5)
        
        self.create_button(
            button_frame,
            "☁️ OneDrive 연동 플레이어",
            "Microsoft 계정 로그인 + 클라우드 스트리밍",
            '#2ecc71', 
            lambda: self.run_player('onedrive')
        ).pack(fill='x', pady=5)
        
        self.create_button(
            button_frame,
            "📱 Android APK 빌드",
            "안드로이드 설치 파일 생성 (WSL 필요)",
            '#e74c3c',
            self.build_apk
        ).pack(fill='x', pady=5)
        
        self.create_button(
            button_frame,
            "🔍 시스템 점검",
            "데이터베이스 및 파일 상태 확인",
            '#f39c12',
            self.check_system_detailed
        ).pack(fill='x', pady=5)
        
        # 하단 정보
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(fill='x', pady=(15, 0))
        
        info_label = tk.Label(
            info_frame,
            text="💡 팁: 처음 사용하시는 경우 '시스템 점검'을 먼저 실행해보세요",
            font=('맑은 고딕', 9),
            fg='#7f8c8d',
            bg='#f0f0f0'
        )
        info_label.pack()
    
    def create_button(self, parent, title, description, color, command):
        """스타일된 버튼 생성"""
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        
        button = tk.Button(
            button_frame,
            text=title,
            font=('맑은 고딕', 11, 'bold'),
            bg=color,
            fg='white',
            activebackground=self.darken_color(color),
            activeforeground='white',
            bd=0,
            padx=20,
            pady=10,
            command=command,
            cursor='hand2'
        )
        button.pack(side='left', fill='x', expand=True)
        
        desc_label = tk.Label(
            button_frame,
            text=description,
            font=('맑은 고딕', 8),
            fg='#7f8c8d',
            bg='#f0f0f0'
        )
        desc_label.pack(side='right', padx=(10, 0))
        
        return button_frame
    
    def darken_color(self, color):
        """색상 어둡게"""
        color_map = {
            '#3498db': '#2980b9',
            '#2ecc71': '#27ae60', 
            '#e74c3c': '#c0392b',
            '#f39c12': '#e67e22'
        }
        return color_map.get(color, color)
    
    def log_message(self, message):
        """상태창에 메시지 추가"""
        self.status_text.insert(tk.END, message + '\n')
        self.status_text.see(tk.END)
        self.root.update()
    
    def check_system(self):
        """기본 시스템 확인"""
        self.log_message("🔍 시스템 점검을 시작합니다...")
        
        # Python 확인
        version = sys.version_info
        self.log_message(f"✅ Python {version.major}.{version.minor}.{version.micro} 확인됨")
        
        # 프로젝트 파일 확인
        files_to_check = [
            ('kivy_main.py', '기본 플레이어'),
            ('kivy_onedrive_main.py', 'OneDrive 플레이어'),
            ('full_bible.db', '성경 데이터베이스'),
        ]
        
        for filename, description in files_to_check:
            if (self.current_dir / filename).exists():
                self.log_message(f"✅ {description} 파일 확인됨")
            else:
                self.log_message(f"⚠️ {description} 파일 없음: {filename}")
        
        self.log_message("📋 시스템 점검 완료. 위의 버튼을 클릭하여 실행하세요.")
    
    def check_system_detailed(self):
        """상세 시스템 점검"""
        self.status_text.delete(1.0, tk.END)
        self.log_message("🔍 상세 시스템 점검을 시작합니다...")
        
        try:
            # Python으로 테스트 스크립트 실행
            result = subprocess.run([
                sys.executable, 'test_korean.py'
            ], capture_output=True, text=True, cwd=self.current_dir)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        self.log_message(line)
            else:
                self.log_message("❌ 상세 점검 중 오류 발생")
                self.log_message(result.stderr)
                
        except Exception as e:
            self.log_message(f"❌ 점검 오류: {e}")
    
    def install_packages(self):
        """패키지 설치"""
        self.log_message("📦 필요한 패키지를 설치합니다...")
        
        packages = ['kivy[base]', 'pygame', 'requests']
        
        for package in packages:
            self.log_message(f"   설치 중: {package}")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package, '--quiet'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_message(f"   ✅ {package} 완료")
                else:
                    self.log_message(f"   ⚠️ {package} 경고 (계속 진행)")
            except Exception as e:
                self.log_message(f"   ❌ {package} 설치 실패: {e}")
    
    def run_player(self, player_type):
        """플레이어 실행"""
        if player_type == 'basic':
            script = 'kivy_main.py'
            name = '기본 플레이어'
        else:
            script = 'kivy_onedrive_main.py' 
            name = 'OneDrive 연동 플레이어'
        
        script_path = self.current_dir / script
        
        if not script_path.exists():
            messagebox.showerror("파일 없음", f"{script} 파일을 찾을 수 없습니다.")
            return
        
        self.log_message(f"🚀 {name}을(를) 시작합니다...")
        
        # 패키지 설치
        self.install_packages()
        
        try:
            # 별도 프로세스에서 실행
            subprocess.Popen([sys.executable, str(script_path)], cwd=self.current_dir)
            self.log_message(f"✅ {name} 실행됨")
            
            # 선택적으로 런처 최소화
            self.root.iconify()
            
        except Exception as e:
            messagebox.showerror("실행 오류", f"{name} 실행 중 오류:\n{e}")
            self.log_message(f"❌ 실행 오류: {e}")
    
    def build_apk(self):
        """APK 빌드"""
        self.log_message("📱 APK 빌드를 시작합니다...")
        
        # WSL 확인
        try:
            result = subprocess.run(['wsl', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.show_wsl_install_guide()
                return
                
        except FileNotFoundError:
            self.show_wsl_install_guide()
            return
        
        self.log_message("✅ WSL이 설치되어 있습니다")
        self.log_message("🔧 APK 빌드 스크립트를 실행합니다...")
        
        try:
            subprocess.Popen([sys.executable, 'apk_builder_fixed.py'], 
                           cwd=self.current_dir)
            self.log_message("✅ APK 빌드 스크립트 실행됨")
        except Exception as e:
            messagebox.showerror("빌드 오류", f"APK 빌드 스크립트 실행 실패:\n{e}")
    
    def show_wsl_install_guide(self):
        """WSL 설치 안내"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("WSL 설치 안내")
        guide_window.geometry("500x400")
        guide_window.configure(bg='#f0f0f0')
        
        # 제목
        title_label = tk.Label(
            guide_window,
            text="📱 APK 빌드를 위한 WSL 설치",
            font=('맑은 고딕', 14, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)
        
        # 설명
        guide_text = scrolledtext.ScrolledText(
            guide_window,
            height=15,
            wrap=tk.WORD,
            font=('맑은 고딕', 10),
            bg='white'
        )
        guide_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        guide_content = """WSL (Windows Subsystem for Linux) 설치가 필요합니다.

🔧 설치 방법:

1단계: 관리자 PowerShell 실행
   - Windows 키 + X → "Windows PowerShell (관리자)"

2단계: WSL 설치 명령어 실행
   wsl --install

3단계: 컴퓨터 재부팅
   - 명령어 실행 후 컴퓨터 재부팅

4단계: Ubuntu 설정
   - 재부팅 후 Ubuntu 터미널이 자동으로 열림
   - 사용자 이름과 비밀번호 설정

5단계: 설치 완료
   - 다시 이 프로그램에서 APK 빌드 시도

⚠️ 주의사항:
- Windows 10 버전 2004 이상 필요
- 관리자 권한 필요
- 인터넷 연결 필요
- 디스크 공간 2GB 이상 필요

💡 팁:
WSL 설치가 복잡하면 Windows 버전을 먼저 사용해보세요.
동일한 모든 기능을 제공합니다!"""
        
        guide_text.insert(tk.END, guide_content)
        guide_text.config(state='disabled')
        
        # 닫기 버튼
        close_button = tk.Button(
            guide_window,
            text="확인",
            font=('맑은 고딕', 10),
            command=guide_window.destroy,
            bg='#3498db',
            fg='white',
            padx=20,
            pady=5
        )
        close_button.pack(pady=20)
    
    def run(self):
        """런처 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    try:
        app = BibleMP3Launcher()
        app.run()
    except Exception as e:
        # 최후의 수단 - 간단한 에러 표시
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("오류", f"런처 실행 중 오류가 발생했습니다:\n{e}")

if __name__ == "__main__":
    main()