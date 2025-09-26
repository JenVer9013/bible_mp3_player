#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneDrive API 클라이언트
Microsoft Graph API를 사용하여 OneDrive 파일에 액세스
"""

import requests
import json
import urllib.parse
from typing import Optional, Dict, List
import threading
import time

class OneDriveAPI:
    def __init__(self):
        # Microsoft Graph API 엔드포인트
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        
        # 앱 등록 정보 (실제 운영시에는 Azure에서 앱 등록 필요)
        self.client_id = "your_client_id_here"  # Azure에서 발급받은 클라이언트 ID
        self.client_secret = "your_client_secret_here"  # Azure에서 발급받은 클라이언트 시크릿
        self.redirect_uri = "http://localhost:8080/callback"
        self.scopes = "Files.Read Files.Read.All offline_access"
        
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        
    def get_auth_url(self) -> str:
        """OAuth 인증 URL 생성"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scopes,
            'response_mode': 'query',
            'state': 'bible_mp3_player'
        }
        
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"
    
    def exchange_code_for_token(self, auth_code: str) -> bool:
        """인증 코드를 액세스 토큰으로 교환"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'scope': self.scopes
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = time.time() + expires_in
            
            return True
            
        except Exception as e:
            print(f"토큰 교환 오류: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """액세스 토큰 갱신"""
        if not self.refresh_token:
            return False
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'scope': self.scopes
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = time.time() + expires_in
            
            return True
            
        except Exception as e:
            print(f"토큰 갱신 오류: {e}")
            return False
    
    def ensure_valid_token(self) -> bool:
        """유효한 토큰 확인 및 갱신"""
        if not self.access_token:
            return False
        
        # 토큰이 곧 만료되는 경우 갱신
        if time.time() >= self.token_expires_at - 300:  # 5분 전에 갱신
            return self.refresh_access_token()
        
        return True
    
    def get_shared_folder_items(self, share_url: str) -> Optional[List[Dict]]:
        """공유된 OneDrive 폴더의 아이템 목록 조회"""
        if not self.ensure_valid_token():
            return None
        
        try:
            # 공유 URL을 base64로 인코딩
            encoded_url = self._encode_sharing_url(share_url)
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # 공유 아이템의 드라이브 아이템 조회
            url = f"{self.base_url}/shares/{encoded_url}/driveItem/children"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('value', [])
            
        except Exception as e:
            print(f"폴더 아이템 조회 오류: {e}")
            return None
    
    def get_folder_items_recursive(self, share_url: str, folder_path: str = "") -> List[Dict]:
        """재귀적으로 모든 MP3 파일 조회"""
        all_items = []
        items = self.get_shared_folder_items(share_url)
        
        if not items:
            return all_items
        
        for item in items:
            item_name = item.get('name', '')
            item_path = f"{folder_path}/{item_name}".strip('/')
            
            if item.get('folder'):  # 폴더인 경우
                # 재귀적으로 하위 폴더 탐색
                child_url = item.get('@microsoft.graph.downloadUrl', '')
                if child_url:
                    child_items = self.get_folder_items_recursive(child_url, item_path)
                    all_items.extend(child_items)
            elif item_name.lower().endswith('.mp3'):  # MP3 파일인 경우
                item['path'] = item_path
                all_items.append(item)
        
        return all_items
    
    def get_download_url(self, item_id: str) -> Optional[str]:
        """파일의 다운로드 URL 조회"""
        if not self.ensure_valid_token():
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/me/drive/items/{item_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('@microsoft.graph.downloadUrl')
            
        except Exception as e:
            print(f"다운로드 URL 조회 오류: {e}")
            return None
    
    def stream_audio_file(self, download_url: str) -> Optional[requests.Response]:
        """오디오 파일 스트리밍"""
        try:
            headers = {
                'Range': 'bytes=0-',  # 스트리밍을 위한 Range 헤더
            }
            
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()
            
            return response
            
        except Exception as e:
            print(f"오디오 스트리밍 오류: {e}")
            return None
    
    def _encode_sharing_url(self, sharing_url: str) -> str:
        """공유 URL을 base64로 인코딩"""
        import base64
        
        # URL을 적절한 형식으로 변환
        if '1drv.ms' in sharing_url:
            # 1drv.ms 단축 URL을 실제 OneDrive URL로 변환 (리다이렉트 추적)
            try:
                response = requests.head(sharing_url, allow_redirects=True)
                sharing_url = response.url
            except:
                pass
        
        # "https://d.docs.live.net" 형식으로 변환
        sharing_url = sharing_url.replace('https://onedrive.live.com', 'https://1drv.ms')
        
        # base64 인코딩
        encoded_bytes = base64.b64encode(sharing_url.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        
        # Microsoft Graph에서 요구하는 형식으로 변환
        return encoded_str.replace('/', '_').replace('+', '-').rstrip('=') + '='

class SimplifiedOneDriveAuth:
    """간소화된 OneDrive 인증 (사용자 로그인 방식)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        
    def login_with_credentials(self, email: str, password: str) -> bool:
        """이메일과 비밀번호로 로그인 (비추천 - 보안상 위험)"""
        # 실제 운영에서는 OAuth를 사용해야 함
        # 이 방법은 데모용으로만 사용
        print("경고: 실제 운영에서는 OAuth 인증을 사용하세요.")
        
        # 여기서는 단순히 로그인 성공으로 가정
        # 실제로는 Microsoft의 로그인 API를 호출해야 함
        self.logged_in = True
        return True
    
    def get_shared_files(self, share_url: str) -> List[Dict]:
        """공유된 폴더의 파일 목록 조회 (간소화 버전)"""
        if not self.logged_in:
            return []
        
        # 데모용 더미 데이터
        # 실제로는 Microsoft Graph API를 호출
        dummy_files = [
            {
                'name': '01. Genesis(창세기)',
                'type': 'folder',
                'children': [
                    {'name': '01.mp3', 'type': 'file', 'download_url': f'{share_url}/01.Genesis/01.mp3'},
                    {'name': '02.mp3', 'type': 'file', 'download_url': f'{share_url}/01.Genesis/02.mp3'},
                ]
            },
            {
                'name': '02. Exodus(출애굽기)',
                'type': 'folder',
                'children': [
                    {'name': '01.mp3', 'type': 'file', 'download_url': f'{share_url}/02.Exodus/01.mp3'},
                ]
            }
        ]
        
        return dummy_files