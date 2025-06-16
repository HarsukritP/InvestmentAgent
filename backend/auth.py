"""
OAuth Authentication module for Google OAuth2 integration
"""
import os
import jwt
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import json

class AuthenticationService:
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expire_hours = 24
        
    def get_google_oauth_url(self, redirect_uri: str) -> str:
        """Generate Google OAuth2 authorization URL"""
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": self.google_client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Token exchange failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def verify_google_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and extract user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                "sub": idinfo['sub'],
                "email": idinfo['email'],
                "name": idinfo['name'],
                "picture": idinfo.get('picture'),
                "verified_email": idinfo.get('email_verified', False)
            }
            
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    def create_jwt_token(self, user_info: Dict[str, Any]) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            "sub": user_info["sub"],
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info.get("picture"),
            "db_user_id": user_info.get("db_user_id"),
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expire_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and extract user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user information from JWT token"""
        payload = self.verify_jwt_token(token)
        if payload:
            return {
                "sub": payload["sub"],
                "email": payload["email"],
                "name": payload["name"],
                "picture": payload.get("picture"),
                "db_user_id": payload.get("db_user_id")
            }
        return None 