import argparse
import requests
import pyquery
import re

def login(session, email, password):
    
    '''
    Attempt to login to Facebook. Returns user ID and
    fb_dtsg token. These are required to make requests to
    Facebook endpoints as a logged in user. Returns False if
    login failed.
    '''

    # Navigate to Facebook's homepage to load Facebook's cookies.
    response = session.get('https://m.facebook.com')
    
    # Attempt to login to Facebook with given credentials
    response = session.post('https://m.facebook.com/login.php', data={
        'email': email,
        'pass': password
    }, allow_redirects=False)
    
    # If c_user cookie is present, login was successful
    if 'c_user' in response.cookies:

        # Make a request to homepage to get fb_dtsg token
        homepage_resp = session.get('https://m.facebook.com/home.php')
        
        dom = pyquery.PyQuery(homepage_resp.text.encode('utf8'))
        fb_dtsg = dom('input[name="fb_dtsg"]').val()

        return fb_dtsg, response.cookies['c_user'], response.cookies['xs']
    else:
        return False 

def change_emoji(fb_dtsg, user_id, partner_id):
    '''
    Changes the default emoji to the choosen one in the chat
    with the selected partner or group.
    '''
    # Getting the chat ID of partner or group
    idre = re.compile(b'"entity_id":"([0-9]+)"')
    response = session.get('https://www.facebook.com/' + partner_id)
    fbid = idre.findall(response.text.encode('utf-8'))[0].decode('utf-8')
    
    # Sending the HTTP request to change the default emoji
    response = session.post('https://www.facebook.com/messaging/save_thread_emoji/?source=thread_settings&dpr=1',
        data = {
            'emoji_choice': '😁',
            'thread_or_other_fbid': fbid,
            '__user': user_id,
            'fb_dtsg': fb_dtsg
        }, allow_redirects=False)

# Main function
if __name__ == "__main__":
    
    # Collecting the parameters
    parser = argparse.ArgumentParser(description='Login to Facebook')
    parser.add_argument('email', help='Email address')
    parser.add_argument('password', help='Login password')
    parser.add_argument('partner_id', help='The facebook ID of your chat partner(end of their profile link)')

    args = parser.parse_args()

    # Creating the session
    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })

    fb_dtsg, user_id, xs = login(session, args.email, args.password)
    
    if user_id:
        print('{0}:{1}:{2}'.format(fb_dtsg, user_id, xs))
        change_emoji(fb_dtsg, user_id, args.partner_id)
    else:
        print('Login Failed')
    