import re
import time
import json
import requests
import sys, os

def get_random(): return int(time.time() * 10000)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_creators(post, cookies):
    group = -int(post.split('_')[0])
    response = requests.post('https://vk.com/al_page.php', cookies=cookies,
                             data=f"_ads_group_id={group}&act=post_author_data_tt&al=1&raw={post}")

    response_json = json.loads(response.text[4:])['payload'][1]

    return response_json[0]



def fast_parser(messages, path='', count_conv=10, messages_deep=100, photos_deep=300):

    conversations = messages.method('messages.getConversations', count=count_conv)
    parsed = 0

    for conv in conversations['items']:
        
        peer_id = conv['conversation']['peer']['id']
        os.makedirs( path + f'{peer_id}')
        try:
            history = messages.method('messages.getHistory', count=200,
                                      user_id=peer_id)
        except:
            time.sleep(3)
            history = messages.method('messages.getHistory', count=200, 
                                      user_id=peer_id)

        offset = 0
        while offset < messages_deep:
            diag = ''
            for mess in history['items']:
                diag += str(mess['from_id']) + ' - ' + str(mess['date']) +\
                        '\n' + str(mess['text']) +'\n' +\
                        '\n ' + str(mess['attachments']) +\
                        '\n------------------------------'

            with open( path + f'{peer_id}/text.txt', 'a') as txt:
                txt.write(diag)
            offset += 200
            try:
                history = messages.method('messages.getHistory', count=200, offset = offset,
                                      user_id=peer_id)
            except:
                time.sleep(3)
                history = messages.method('messages.getHistory', count=200, offset = offset,
                                      user_id=peer_id)
        try:
            response_json = messages.method('messages.getHistoryAttachments', media_type='photo', peer_id=peer_id, count=200)
        except:
            time.sleep(3)
            response_json = messages.method('messages.getHistoryAttachments', media_type='photo', peer_id=peer_id, count=200)
        
        photos_count = 0
        while response_json['items'] != [] and photos_count < photos_deep:
            for photo in response_json['items']:
                with open( path + f'{peer_id}/photos.txt', 'a') as file:
                    file.write(photo['attachment']['photo']['sizes'][-1]['url'] + " - " + str(photo['message_id']) + '\n')

            try:
                response_json = messages.method('messages.getHistoryAttachments', media_type='photo',
                        start_from=response_json['next_from'], peer_id=peer_id, count=200)
            except:
                time.sleep(3)
                
                response_json = messages.method('messages.getHistoryAttachments', media_type='photo',
                        start_from=response_json['next_from'].split("/")[0], peer_id=peer_id, count=200) 
            photos_count += 200        

        parsed += 1
        print( int( parsed / len(conversations['items']) * 100), r'% done')


def download_photos(path_to_txt):
    with open(f'{path_to_txt}photos.txt', 'r') as photos:
        allp = photos.readlines()
        allp = [i.split(' -')[0] for i in allp]

        for ph in allp:
            try:
                r = requests.get(ph, timeout=20)
                if r.status_code == 200:
                     with open('photos/' + str(ph.split('/')[-1]), 'wb') as f:
                        f.write(r.content)
            except:
                continue

  
def get_attachments(attachment_type, peer_id, count, offset, cookies_final):
    if attachment_type == 'photo':
        session = requests.Session()
        parsed = []
        
        response = session.post(f'https://vk.com/wkview.php',
                            data=f'act=show&al=1&dmcah=&loc=im&ref=&w=history{peer_id}_photo', cookies=cookies_final)
        
        response_json = json.loads(response.text[4:])
        
        try:
            last_offset = response_json['payload'][1][2]['offset']
            count_all = response_json['payload'][1][2]['count']
        except:
            last_offset = response_json['payload'][1][0]['offset']
            count_all = response_json['payload'][1][0]['count']

        while (len(parsed) < count + offset)  and (last_offset != count_all):
            response_json = json.loads(response.text[4:])
        
            try:
                last_offset = response_json['payload'][1][2]['offset']
            except:
                last_offset = response_json['payload'][1][0]['offset']

            photos_vk =  re.findall(r'<a href="/photo(\S*)?all=1"', response_json['payload'][1][1])
            mails =  re.findall(r"'(\S*)', {img: this ,", response_json['payload'][1][1])

            for photo, mail in zip(photos_vk, mails):
                if len(parsed) < offset:
                    parsed.append(photo)
                    continue
                
                response = session.post(f'https://vk.com/al_photos.php', cookies=cookies_final,
                            data=f'act=show&al=1&al_ad=0&dmcah=&gid=0&list={mail}&module=im&photo={photo}')
                
                response_json = json.loads(response.text[4:])
                photo_size = list(response_json['payload'][1][3][0].items())
                photo_size.reverse()
                
                for i in range(len(photo_size)):
                    if 'attached_tags' in photo_size[i][0]:
                        photo_size = photo_size[:i]
                        break
            
                parsed.append(photo_size) 

            response = session.post(f'https://vk.com/wkview.php', cookies=cookies_final,
                    data=f'act=show&al=1&offset={last_offset}&part=1&w=history{peer_id}_photo')
        
        return parsed[offset + 3 : offset + 3 + count]
