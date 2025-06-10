import requests
import logging
from typing import Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
db = SQLAlchemy()

class WordPressRestAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth = (username, password)
        self.token = None
        self.api_url = f"{self.base_url}/wp-json/wp/v2"

    def authenticate(self):
        """Authenticate with WordPress REST API"""
        try:
            auth_url = f"{self.base_url}/wp-json/jwt-auth/v1/token"
            response = requests.post(auth_url, data={
                'username': self.username,
                'password': self.password
            })
            response.raise_for_status()
            self.token = response.json().get('token')
            return self.token is not None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def create_post(self, title: str, content: str, status: str = 'draft') -> Optional[Dict[str, Any]]:
        try:
            if not self.token:
                self.authenticate()

            endpoint = f"{self.api_url}/posts"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            data = {
                'title': title,
                'content': content,
                'status': status
            }
            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None

    def get_posts(self, per_page: int = 10, page: int = 1) -> Optional[Dict[str, Any]]:
        try:
            if not self.token:
                self.authenticate()

            endpoint = f"{self.api_url}/posts"
            headers = {'Authorization': f'Bearer {self.token}'}
            params = {'per_page': per_page, 'page': page}
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return None

    def update_post(self, post_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            if not self.token:
                self.authenticate()

            endpoint = f"{self.api_url}/posts/{post_id}"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            response = requests.put(endpoint, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating post: {e}")
            return None

    def delete_post(self, post_id: int) -> bool:
        try:
            if not self.token:
                self.authenticate()

            endpoint = f"{self.api_url}/posts/{post_id}"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.delete(endpoint, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return False

    def get_core_version(self) -> Dict[str, Any]:
        try:
            if not self.token:
                self.authenticate()

            version_url = f"{self.api_url}/settings"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(version_url, headers=headers)
            response.raise_for_status()

            current_version = response.json().get('wordpress_version', 'Unknown')
            return {
                'update_available': current_version != '6.5.0',
                'current_version': current_version,
                'latest_version': '6.5.0'
            }
        except Exception as e:
            logger.error(f"Error checking core version: {e}")
            return {
                'update_available': False,
                'current_version': 'Unknown',
                'latest_version': 'Unknown'
            }

    def upload_media(self, file_obj, alt_text: str = '') -> Optional[Dict[str, Any]]:
        try:
            if not self.token:
                self.authenticate()

            media_url = f"{self.api_url}/media"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Disposition': f'attachment; filename={file_obj.filename}'
            }

            file_data = file_obj.read()
            response = requests.post(media_url, headers=headers, data=file_data)
            response.raise_for_status()

            media_data = response.json()

            if alt_text and media_data.get('id'):
                self.update_media_alt_text(media_data['id'], alt_text)

            return media_data
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            return None

    def update_media_alt_text(self, media_id: int, alt_text: str) -> bool:
        try:
            if not self.token:
                self.authenticate()

            media_url = f"{self.api_url}/media/{media_id}"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            data = {'alt_text': alt_text}

            response = requests.post(media_url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error updating media alt text: {e}")
            return False

    def sync_generated_content(self, content_data: Dict[str, Any], content_type: str = 'post') -> Optional[Dict[str, Any]]:
        try:
            if not self.token:
                self.authenticate()

            if content_type == 'post':
                return self.create_post(
                    title=content_data.get('title', 'Generated Post'),
                    content=content_data.get('content', ''),
                    status=content_data.get('status', 'draft')
                )
            elif content_type == 'page':
                page_url = f"{self.api_url}/pages"
                headers = {
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                }
                data = {
                    'title': content_data.get('title', 'Generated Page'),
                    'content': content_data.get('content', ''),
                    'status': content_data.get('status', 'draft')
                }
                response = requests.post(page_url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error syncing content: {e}")
            return None