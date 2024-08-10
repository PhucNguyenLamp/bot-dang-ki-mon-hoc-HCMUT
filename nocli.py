import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import json
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

def get_jwt_token(session):
    url = 'https://mybk.hcmut.edu.vn/app/he-thong-quan-ly/sinh-vien/ket-qua-hoc-tap'
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    token_input = soup.find('input', {'id': 'hid_Token'})
    return token_input['value']


# Usage
def get_student_info(session, jwt_token):
    student_info_url = 'https://mybk.hcmut.edu.vn/api/v1/student/get-student-info'
    headers = {
        'Authorization': jwt_token
    }
    response = session.get(student_info_url, headers=headers)
    student_info = response.json()
    student_info = student_info['data']['id']
    print(student_info)

    grade_url = 'https://mybk.hcmut.edu.vn/api/v1/student/subject-grade'
    params = {
        'studentId': int(student_info),
        'semesterYear': -1,
        'null': None
    }
    response = session.get(grade_url, params=params, headers=headers)
    data = response.text
    return data


