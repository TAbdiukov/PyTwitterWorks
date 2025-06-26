import os
import yaml
import argparse
import json
from tqdm import tqdm
from twitter.scraper import Scraper

def check_and_create_auth():
    """Create AUTH.yaml template if not present and terminate"""
    if not os.path.exists('AUTH.yaml'):
        with open('AUTH.yaml', 'w') as f:
            yaml.dump({
                'auth_token': 'YOUR_AUTH_TOKEN_HERE',
                'ct0': 'YOUR_CT0_TOKEN_HERE'
            }, f)
        print("AUTH.yaml file created. Please fill in your Twitter authentication tokens.")
        exit(1)

def load_auth_credentials():
    """Load authentication credentials from YAML file"""
    with open('AUTH.yaml', 'r') as f:
        auth = yaml.safe_load(f)
    return {
        'auth_token': auth['auth_token'],
        'ct0': auth['ct0']
    }

def extract_user_fields(user):
    """Extract specified fields from user object"""
    legacy = user.get('legacy', {})
    return {
        'id_str': str(user.get('rest_id', '')),
        'name': legacy.get('name', ''),
        'screen_name': legacy.get('screen_name', ''),
        'description': legacy.get('description', ''),
        'statuses_count': legacy.get('statuses_count', 0),
        'followers_count': legacy.get('followers_count', 0),
        'friends_count': legacy.get('friends_count', 0),
        'favourites_count': legacy.get('favourites_count', 0),
        'profile_image_url_https': legacy.get('profile_image_url_https', ''),
        'location': legacy.get('location', ''),
        'url': legacy.get('url', ''),
        'verified': legacy.get('verified', False),
        'is_blue_verified': user.get('is_blue_verified', False),
        'verified_type': user.get('verified_type', ''),
        'protected': legacy.get('protected', False),
        'can_dm': user.get('can_dm', False),
        'created_at': legacy.get('created_at', ''),
        'profile_banner_url': legacy.get('profile_banner_url', ''),
        'media_count': legacy.get('media_count', 0),
        'professional': bool(user.get('professional'))
    }

def main():
    # Check and create auth file if needed
    check_and_create_auth()
    
    # Load authentication credentials
    cookies = load_auth_credentials()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Extract Twitter followers')
    parser.add_argument('username', help='Twitter username to scrape followers from')
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = Scraper(cookies=cookies)
    
    # Get target user information
    try:
        users = scraper.users([args.username])
        if not users:
            print(f"User '{args.username}' not found")
            exit(1)
            
        user_data = users[0]
        user_id = user_data['rest_id']
        followers_count = user_data['legacy']['followers_count']
    except Exception as e:
        print(f"Error fetching user data: {e}")
        exit(1)
    
    # Prepare output file
    output_file = f"{args.username}_followers.jsonl"
    total_followers = 0
    
    # Fetch and save followers
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            with tqdm(total=followers_count, unit='followers') as pbar:
                for batch in scraper.followers([user_id]):
                    if not batch:
                        break
                    
                    for follower in batch:
                        extracted = extract_user_fields(follower)
                        f.write(json.dumps(extracted, ensure_ascii=False) + '\n')
                    
                    total_followers += len(batch)
                    pbar.update(len(batch))
        
        print(f"\nCompleted! Saved {total_followers} followers to {output_file}")
        print(f"Note: Actual count may differ due to private/suspended accounts")
        
    except Exception as e:
        print(f"\nError during scraping: {e}")
        exit(1)

if __name__ == '__main__':
    main()
