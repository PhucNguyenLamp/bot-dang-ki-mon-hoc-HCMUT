import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
load_dotenv()

def login_to_sso(username, password):
    session = requests.Session()
    
    sso_base_url = 'https://sso.hcmut.edu.vn'
    mybk_base_url = 'https://mybk.hcmut.edu.vn'
    login_url = f'{sso_base_url}/cas/login'
    service_url = f'{mybk_base_url}/app/login/cas'
    
    # đúng link
    response = session.get(f'{login_url}?service={service_url}')
    # đúng form data và action
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', id='fm1')
    form_data = {input.get('name'): input.get('value') for input in form.find_all('input') if input.get('name')}
    form_data.update({'username': username, 'password': password})
    session.post(urljoin(sso_base_url, form['action']), data=form_data, allow_redirects=True)

    return session

def is_logged_in(session):
    test_url = 'https://mybk.hcmut.edu.vn/app/he-thong-quan-ly/sinh-vien/thong-tin-tuyen-sinh'
    response = session.get(test_url)
    return 'Đăng nhập' not in response.text  # Check if login text is not in the response

# Usage
username = os.getenv('ACCOUNT')
password = os.getenv('PASSWORD')

session = login_to_sso(username, password)

if session and is_logged_in(session):
    print("Successfully logged in!")
    protected_url = 'https://mybk.hcmut.edu.vn/app/he-thong-quan-ly/sinh-vien/thong-tin-tuyen-sinh'
    response = session.get(protected_url)



else:
    print("Login failed or unable to access protected content")