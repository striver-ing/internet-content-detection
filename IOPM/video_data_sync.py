import requests

TIME_OUT = 30

def get_json_by_requests(url, params = None, headers = '', data = None, proxies = {}):
    json = {}
    response = None
    try:
        #response = requests.get(url, params = params)
        if data:
            response = requests.post(url, headers = headers, data = data, params = params, timeout = TIME_OUT, proxies = proxies)
        else:
            response = requests.get(url, headers=headers, params = params, timeout=TIME_OUT, proxies = proxies)
        response.encoding = 'utf-8'
        json = response.json()
    except Exception as e:
        print(e)
    finally:
        response and response.close()

    return json


def main():
    url = 'http://192.168.60.38:8002/datasync_al/interface/appDataSync'
    video_infos = [
                {
                    "id": 111,
                    "title": "title",
                    "content": "content",
                    "summary": "summary",
                    "comment_count": 1,
                    "watch_count": 1,
                    "release_time": "2017-07-01 08:00:00",
                    "record_time": "2017-07-01 08:00:00",
                    "site_name": "siteName",
                    "url": "http:www.baidu.com",
                    "actors": "actors",
                    "directors": "directors"
                },
                {
                    "id": 111,
                    "title": "title",
                    "content": "content",
                    "summary": "summary",
                    "comment_count": 1,
                    "watch_count": 1,
                    "release_time": "2017-07-01 08:00:00",
                    "record_time": "2017-07-01 08:00:00",
                    "site_name": "siteName",
                    "url": "http:www.baidu.com",
                    "actors": "actors",
                    "directors": "directors"
                },

                ]

    data = {'data':str(video_infos)}
    print(data)
    result = get_json_by_requests(url, data = data)
    print(result)

if __name__ == '__main__':
    main()