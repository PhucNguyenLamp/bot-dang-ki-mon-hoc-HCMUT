import json
import re
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

def login_to_sso(username, password):
    session = requests.Session()
    
    sso_base_url = 'https://sso.hcmut.edu.vn'
    mybk_base_url = 'https://mybk.hcmut.edu.vn'
    login_url = f'{sso_base_url}/cas/login'
    service_url = f'{mybk_base_url}/dkmh/'
    # đúng link
    response = session.get(f'{login_url}?service={service_url}')
    # đúng form data và action
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', id='fm1')
    form_data = {input.get('name'): input.get('value') for input in form.find_all('input') if input.get('name')}
    form_data.update({'username': username, 'password': password})
    response = session.post(urljoin(sso_base_url, form['action']), data=form_data, allow_redirects=True)
    response = session.get(f'{mybk_base_url}/dkmh/home.action')
    response = session.get(f'{mybk_base_url}/dkmh/dangKyMonHocForm.action')
    
    data = session.get(f'{service_url}/ketQuaDangKyView.action', data={'hocKyId': '574'})
    session.post(f'{service_url}/getDanhSachDotDK.action',data={'hocKyId': '574'})
    session.post(f'{service_url}/getLichDangKy.action', data={'dotDKId':'656','dotDKHocVienId':'656'})
    session.post(f'{service_url}/getDanhSachMonHocDangKy.action', data={'dotDKId':'656'})
    session.post(f'{service_url}/getKetQuaDangKy.action')

    return session

def get_subject_code(session, subject_id):
    payload = {
        'msmh': subject_id
    }
    response = session.post('https://mybk.hcmut.edu.vn/dkmh/searchMonHocDangKy.action', data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    tr_element = soup.find('tr', id=lambda x: x and x.startswith('monHoc'))
    if tr_element is None:
        return None
    subject_code = tr_element['id'].replace('monHoc', '')
    return subject_code

def get_class_id(session, subject_code):
    payload = {
        'monHocId': subject_code
    }
    response = session.post('https://mybk.hcmut.edu.vn/dkmh/getThongTinNhomLopMonHoc.action', data=payload)
    with open('response.html', 'w') as f:
        f.write(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    n_group = soup.find('td', class_='item_list', string='N--- ')
    tr = n_group.find_parent('tr')
    button = tr.find('button', onclick=lambda x: x and 'dangKyNhomLopMonHoc' in x)
    onclick_value = button['onclick']
    start_index = onclick_value.index('this,') + 5
    end_index = onclick_value.index(',', start_index)
    class_id = onclick_value[start_index:end_index].strip()
    return class_id


def register_class(session, class_id):
    url = 'https://mybk.hcmut.edu.vn/dkmh/dangKy.action'
    payload = {
        'NLMHId': class_id
    }
    data = session.post(url, data=payload)
    print(data.text)

if __name__ == '__main__':
    username = os.getenv('ACCOUNT')
    password = os.getenv('PASSWORD')

    session = login_to_sso(username, password)

    subject_code = get_subject_code(session, 'AS1003') 
    print(subject_code)
    class_id = get_class_id(session, subject_code)
    print(class_id)
    register_class(session, class_id)
