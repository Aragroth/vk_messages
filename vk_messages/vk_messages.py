import pickle, requests, re, json, os, time
from urllib.parse import quote
from bs4 import BeautifulSoup
from .utils import cleanhtml

class Exception_MessagesAPI(Exception):
    '''
    Warning:
    Be carefull, this script may not
    explain and figure out all Exceptions
    '''
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = f'MessagesAPIexception[{errors}]'

class MessagesAPI():
    '''
    Warning:
    Look carefull, selecting wrong authorization
    (two_factor or non-two_factor) will collapse script.
    when selecting this script will not
    explain and figure out all Exceptions
    '''
    def __init__(self, login, password, two_factor=False, cookies_save_path=''):
        self.login = login
        self.password = str(password.encode('UTF-8')).replace('\\x', '%')[2:-1]
        self.two_factor = two_factor

        if len(cookies_save_path)!= 0 and cookies_save_path[-1] not in ["/", "\\", '']:
            raise Exception_MessagesAPI('Save path must end with one of this symbols: "/", "\\", or be empty', 'InvalidPath')
        
        self.cookies_save_path = cookies_save_path
        self.main_session = requests.Session()

        if os.path.exists(f'{self.cookies_save_path}cookies_vk_auth_{self.login}.pickle'):
            with open(f'{self.cookies_save_path}cookies_vk_auth_{self.login}.pickle', 'rb') as handle:
                self.cookies_final = pickle.load(handle)
                response = self.main_session.get(f'https://vk.com/', cookies=self.cookies_final)
                if 'Войти через Facebook' not in response.text:
                    return None
                    
        response = self.main_session.get(f'https://vk.com/')
        
        self.ip_h =  re.findall(r'ip_h=(\S*)&lg', str(response.text))[0]
        self.lg_h =  re.findall(r'lg_h=(\S*)&r', str(response.text))[0]
        
        if two_factor == True:
            self.two_factor_auth()
        else:
            self.single_factor_auth()
        
        with open(f'{self.cookies_save_path}cookies_vk_auth_{self.login}.pickle', 'wb') as handle:
            pickle.dump(self.cookies_final, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def single_factor_auth(self):
        self.main_session.post(f'https://login.vk.com/?act=login',
                    data=f'act=login&role=al_frame&expire=&recaptcha=&captcha_sid=&captcha_key=&_origin=https%3A%2F%2Fvk.com' +\
                         f'&ip_h={self.ip_h}&lg_h={self.lg_h}&ul=&email={self.login}&pass={self.password}',
                         allow_redirects=False, cookies=self.main_session.cookies.get_dict())
        q_hash = None
        for i in self.main_session.cookies.get_dict():
            if 'remixq_' in i:
                q_hash = i.split('remixq_')[1]
                break

        if q_hash == None:
            raise Exception_MessagesAPI('Invalid login data or wrong auth method', 'LoginError')
            
        self.main_session.get(f'https://vk.com/login.php?act=slogin&to=&s=1&__q_hash={q_hash}',
                                                        cookies=self.main_session.cookies.get_dict() )
        self.main_session.get(f'https://vk.com/feed',
                                    cookies=self.main_session.cookies.get_dict())

        self.cookies_final = self.main_session.cookies.get_dict()

        

    def two_factor_auth(self):
        self.main_session.post(f'https://login.vk.com/?act=login',
                        data=f"act=login&role=al_frame&expire=&recaptcha=&captcha_sid=&captcha_key=&_origin=https%3A%2F%2Fvk.com" +\
                             f"&ip_h={self.ip_h}&lg_h={self.lg_h}&ul=&email={self.login}&pass={self.password}",
                             cookies=self.main_session.cookies.get_dict())

        q_hash = None
        for i in self.main_session.cookies.get_dict():
            if 'remixq_' in i:
                q_hash = i.split('remixq_')[1]
                break
        
        self.main_session.get(f'https://vk.com/login.php?act=slogin&to=&s=1&__q_hash={q_hash}',
                                                        cookies=self.main_session.cookies.get_dict())
        response = self.main_session.get(f'https://vk.com/login?act=authcheck',
                                                        cookies=self.main_session.cookies.get_dict())

        hash_url = re.findall(r"Authcheck\.init\('([a-z_0-9]+)'", str(response.text))
        if hash_url == []:
            raise Exception_MessagesAPI('Invalid login data or wrong auth method', 'LoginError')
        hash_url = hash_url[0]

        code = input('Enter verification code:  ')

        response = self.main_session.post(f'https://vk.com/al_login.php',
                        data=f'act=a_authcheck_code&al=1&code={code}&hash={hash_url}&remember=1',
                            cookies=self.main_session.cookies.get_dict())
        
        response_json = json.loads(response.text[4:])['payload']
        if 'Неверный код' in response_json[1][0]:
            raise Exception_MessagesAPI('Wrong verification code', 'VerificationError')

        response = self.main_session.get(f'https://vk.com/login.php?act=slogin&to=&s=1&__q_hash={q_hash}&fast=1',
                                        cookies=self.main_session.cookies.get_dict())

        self.main_session.get(f'https://vk.com/feed',
                                        cookies=self.main_session.cookies.get_dict())

        self.cookies_final = self.main_session.cookies.get_dict()

    def method(self, name, **kwargs):
        if not hasattr(self, 'cookies_final'):
            raise Exception_MessagesAPI('No cookies found. Auth first.', 'AuthError')

        session = requests.Session()

        response = session.get(f'https://vk.com/dev/{name}', cookies=self.cookies_final)
        hash_data =  re.findall(r'data-hash="(\S*)"', response.text)

        soup = BeautifulSoup(response.text, features="html.parser")
        params = soup.findAll("div", {"class": "dev_const_param_name"})
        params = [cleanhtml(str(i)) for i in params]

        if hash_data == []:
            raise  Exception_MessagesAPI('Invalid method or not logined', 'Cannot_use_this_method')
        hash_data = hash_data[0]

        payload, checker = '', 0
        for param in params:
            if param in kwargs:
                checker += 1
                payload += '&{}={}'.format('param_' + \
                 param, quote(str(kwargs[param]) if type(kwargs[param]) != bool else str(int(kwargs[param]))))
        
        if checker != len(kwargs):
            raise Exception_MessagesAPI('Some of the parametrs invalid', 'InvalidParameters')

        response = session.post(f'https://vk.com/dev',
            data=f'act=a_run_method&al=1&hash={quote(hash_data)}&method={name}{payload}&param_v=5.103', cookies=self.cookies_final)

        response_json = json.loads(response.text[4:])['payload']

        if 'error' in json.loads(response_json[1][0]).keys():
            raise Exception_MessagesAPI(json.loads(response_json[1][0])['error']['error_msg'],
                              json.loads(response_json[1][0])['error']['error_code'])
        
        return json.loads(response_json[1][0])['response']
    
    def get_cookies(self):
        return self.cookies_final
    
