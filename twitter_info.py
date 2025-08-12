#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import os
import json
import argparse
from twitter.scraper import Scraper

def create_auth_template():
    """Create AUTH.yaml template with placeholder values if it doesn't exist"""
    auth_template = {
        'auth_token': 'YOUR_TWITTER_AUTH_TOKEN_HERE',
        'ct0': 'YOUR_CSRF_TOKEN_HERE'
    }
    with open('AUTH.yaml', 'w') as f:
        yaml.dump(auth_template, f, default_flow_style=False)
    return auth_template

def load_auth_credentials():
    """Load authentication credentials from YAML file"""
    if not os.path.exists('AUTH.yaml'):
        print("AUTH.yaml not found. Creating template file...")
        return create_auth_template()
    
    with open('AUTH.yaml', 'r') as f:
        auth = yaml.safe_load(f)
    
    return auth

def validate_auth_credentials(auth):
    """Validate that required credentials are present"""
    if not auth.get('auth_token') or auth['auth_token'] == 'YOUR_TWITTER_AUTH_TOKEN_HERE':
        print("Error: Please update AUTH.yaml with your actual auth_token")
        return False
    if not auth.get('ct0') or auth['ct0'] == 'YOUR_CSRF_TOKEN_HERE':
        print("Error: Please update AUTH.yaml with your actual ct0 token")
        return False
    return True

def main():
    # Load and validate credentials
    auth = load_auth_credentials()
    if not validate_auth_credentials(auth):
        return
    
    # Setup command-line arguments
    parser = argparse.ArgumentParser(description='Inspect Twitter user data structure')
    parser.add_argument('username', help='Twitter username to inspect')
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = Scraper(cookies=auth)
    
    # Get target user information
    try:
        user_data = scraper.users([args.username])
        if not user_data or not user_data[0].get('data', {}).get('user', {}).get('result'):
            print(f"Error: User '{args.username}' not found or inaccessible")
            return
            
        # Extract the full user result data
        user_result = user_data[0]['data']['user']['result']
        
        # Print YAML representation of the full data structure
        print("=" * 80)
        print(f"Full data structure for @{args.username}:")
        print("=" * 80)
        print(yaml.dump(user_result, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000))
        
    except Exception as e:
        print(f"Error fetching user data: {str(e)}")
        return

if __name__ == '__main__':
    main()
