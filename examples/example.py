
# WARNING _______________________________________________
# Use strictly the name of method, that is written       |
# in www.vk.com/dev documentation, otherwise scipt will  |
# collapse. Also be ready to expirience several bugs.    |
#                                                        |
# author - 'Aragroth (Osiris)'                           |
# version - '1.0.0'                                      |
# email - 'aragroth.osiris@yandex.ru'                    |
# _______________________________________________________|

from vk_messages import MessagesAPI
from vk_messages.utils import (cleanhtml, get_random, get_creators,
                                fast_parser, get_attachments)

login, password = 'login', 'password'                                    # be shure to use right
messages = MessagesAPI(login=login, password=password, two_factor=True)  # two_factor auth parametr

peer_id = '123456789' 
history = messages.method('messages.getHistory', offset=1,          # all methods work
                                        user_id=peer_id, count=5)   # as they described in 
print(*[i['text'] for i in history['items']], sep='\n')             # the offical documentation


messages.method('messages.send', user_id=peer_id, message='Hello',     # You can use uploading from
            attachment='photo123456_7891011', random_id=get_random())  # vk_api library on github


attachment_photos = get_attachments(attachment_type='photo', peer_id=peer_id,          # you can use custom
                            offset=1, count=1, cookies_final=messages.get_cookies())   # written methods by
print('\n', len(attachment_photos), sep='\n')                                          # getting auth cookies


authors = get_creators(post='-12345_67890',            # or even get information
                    cookies=messages.get_cookies())    # that is not provided with
print(cleanhtml(authors))                              # offical API


fast_parser(messages, path='parsing/',                       # will parse last conversations
        count_conv=10, messages_deep=400, photos_deep=100)   # and save text and photos of them