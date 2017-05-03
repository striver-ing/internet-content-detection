# encoding=utf8

import sys
sys.path.append("..")

import re
import json
import configparser #读配置文件的
import codecs
import uuid
import urllib.parse
from urllib.parse import quote
from utils.log import log
from tld import get_tld
from urllib import request
from urllib.parse import urljoin
from selenium import webdriver
import requests
import time
from bs4 import BeautifulSoup
from threading import Timer
import functools
import datetime
import time
import os
import execjs   # pip install PyExecJS
import hashlib
from pprint import pprint

TIME_OUT = 30
TIMER_TIME = 5

# 装饰器
def log_function_time(func):
    try:
        @functools.wraps(func)  #将函数的原来属性付给新函数
        def calculate_time(*args, **kw):
            began_time = time.time()
            callfunc = func(*args, **kw)
            end_time = time.time()
            log.debug(func.__name__ + " run time  = " + str(end_time - began_time))
            return callfunc
        return calculate_time
    except:
        log.debug('求取时间无效 因为函数参数不符')
        return func

def run_safe_model(module_name):
    def inner_run_safe_model(func):
        try:
            @functools.wraps(func)  #将函数的原来属性付给新函数
            def run_func(*args, **kw):
                callfunc = ''
                try:
                    callfunc = func(*args, **kw)
                except Exception as e:
                    log.error(module_name + ": " + func.__name__ + " - " + str(e))
                return callfunc
            return run_func
        except Exception as e:
            log.error(module_name + ": " + func.__name__ + " - " + str(e))
            return func
    return inner_run_safe_model
#######################################################
def get_html_auto_deal_code(url):
    html = None
    try:
        page = request.urlopen(quote(url,safe='/:?=&'), timeout = 3)
        html = page.read()

        html_code_utf8 = html.decode('utf-8','ignore')
        html_code_gb2312 = html.decode('gb2312','ignore')

        html = len(html_code_gb2312) > len(html_code_utf8) and html_code_gb2312 or html_code_utf8
        page.close()

    except Exception as e:
        log.error(e)
    return html

# import chardet
@log_function_time
def get_html_by_urllib(url, code = 'utf-8'):
    html = None
    if not url.endswith('.exe') and not url.endswith('.EXE'):
        page = None
        is_timeout = False
        try:
            def timeout_handler(response):
                is_timeout = True
                if response:
                    response.close()

            page = request.urlopen(quote(url,safe='/:?=&'), timeout = TIME_OUT)
            # 设置定时器 防止在read时卡死
            t = Timer(TIMER_TIME, timeout_handler, [page])
            t.start()
            # charset = chardet.detect(page.read())['encoding']
            html = page.read().decode(code,'ignore')
            t.cancel()

        except Exception as e:
            log.error(e)
        finally:
            # page and page.close()
            if page and not is_timeout:
                page.close()

    return html and len(html) < 1024 * 1024 and html or None


@log_function_time
def get_html_by_webdirver(url):
    html = None
    try:
        driver = webdriver.PhantomJS()
        driver.get(url)
        # time.sleep(10)
        html = driver.page_source
        driver.close()
    except Exception as e:
        log.error(e)
    return html and len(html) < 1024 * 1024 and html or None

@log_function_time
def get_html_by_requests(url, headers = '', code = 'utf-8'):
    html = None
    if not url.endswith('.exe') and not url.endswith('.EXE'):
        r = None
        try:
            if headers:
                r = requests.get(url, headers = headers, timeout = TIME_OUT)
            else:
                r = requests.get(url, timeout = TIME_OUT)

            if code:
                r.encoding = code
            html = r.text

        except Exception as e:
            log.error(e)
        finally:
            r and r.close()

    return html and len(html) < 1024 * 1024 and html or None, r


def get_json_by_requests(url, params = None, headers = '', data = None):
    json = {}
    response = None
    try:
        #response = requests.get(url, params = params)
        if data:
            response = requests.post(url, headers = headers, data = data, params = params, timeout = TIME_OUT)
        else:
            response = requests.get(url, headers=headers, params = params, timeout=TIME_OUT)
        response.encoding = 'utf-8'
        json = response.json()
    except Exception as e:
        log.error(e)
    finally:
        response and response.close()

    return json

def get_urls(html, stop_urls = []):
    urls = re.compile('<a.*?href="(.*?)"').findall(str(html))
    urls = sorted(set(urls), key = urls.index)

    if stop_urls:
        stop_urls = isinstance(stop_urls, str) and [stop_urls] or stop_urls
        use_urls = []
        for url in urls:
            for stop_url in stop_urls:
                if stop_url not in url:
                    use_urls.append(url)

        urls = use_urls

    return urls


def get_full_url(root_url, sub_url):
    '''
    @summary: 得到完整的ur
    ---------
    @param root_url: 根url （网页的url）
    @param sub_url:  子url （带有相对路径的 可以拼接成完整的）
    ---------
    @result: 返回完整的url
    '''

    # if sub_url.begin
    return urljoin(root_url, sub_url)

def joint_url(url, params):
    param_str = "?"
    for key, value in params.items():
        value = isinstance(value, str) and value or str(value)
        param_str += key + "=" + value + "&"

    return url + param_str[:-1]

def fit_url(urls, identis):
    identis = isinstance(identis, str) and [identis] or identis
    fit_urls = []
    for link in urls:
        for identi in identis:
            if identi in link:
                fit_urls.append(link)
    return list(set(fit_urls))

def unquote_url(url):
    '''
    @summary: 将url解码
    ---------
    @param url:
    ---------
    @result:
    '''

    return urllib.parse.unquote(url)

def quote_url(url):
    '''
    @summary: 将url编码 编码意思http://www.w3school.com.cn/tags/html_ref_urlencode.html
    ---------
    @param url:
    ---------
    @result:
    '''

    return urllib.parse.quote(url)

_regexs = {}
# @log_function_time
def get_info(html, regexs, allow_repeat = False, fetch_one = False):
    regexs = isinstance(regexs, str) and [regexs] or regexs

    infos = []
    for regex in regexs:
        if regex == '':
                continue

        if regex not in _regexs.keys():
            _regexs[regex] = re.compile(regex, re.S)

        if fetch_one:
                infos = _regexs[regex].search(html)
                if infos:
                    infos = infos.groups()
                else:
                    return ''
        else:
            infos = _regexs[regex].findall(str(html))

        # infos = re.findall(regex,str(html),re.S)
        # infos = re.compile(regexs, re.S).findall(str(html))
        if len(infos) > 0:
            break

    if fetch_one:
        return infos if len(infos) > 1 else infos[0]
    else:
        return allow_repeat and infos or sorted(set(infos),key = infos.index)

def get_domain(url):
    domain = ''
    try:
        domain = get_tld(url)
    except Exception as e:
        log.debug(e)
    return domain

def get_tag(html, name = None, attrs = {}, find_all = True):
    try:
        if html:
            soup = BeautifulSoup(html, "html.parser") if isinstance(html, str) else html
            result = soup.find_all(name, attrs) if find_all else soup.find(name, attrs)
            return result if result else []
        else:
            return []
    except Exception as e:
        log.error(e)
        return []

def get_text(soup, *args):
    try:
        return soup.get_text()
    except Exception as e:
        log.error(e)
        return ''

def del_html_tag(content, except_line_break = False):
    content = replace_str(content, '<script(.|\n)*?</script>')
    content = replace_str(content, '<style(.|\n)*?</style>')
    content = replace_str(content, '<!--(.|\n)*?-->')
    content = replace_str(content, '&.*?;')
    if except_line_break:
        content = content.replace('</p>', '/p')
        content = replace_str(content, '<[^p].*?>')
        content = content.replace('/p', '</p>')
        content = replace_str(content, '[ \f\r\t\v]')

    else:
        # content = replace_str(content, '<script(.|\n)*?</script>')
        # content = replace_str(content, '<style(.|\n)*?</style>')
        # content = replace_str(content, '<!--(.|\n)*?-->')
        content = replace_str(content, '<(.|\n)*?>')
        # content = replace_str(content, '&.*?;')
        content = replace_str(content, '\s')

    return content

def is_have_chinese(content):
    regex = '[\u4e00-\u9fa5]+'
    chinese_word = get_info(content, regex)
    return chinese_word and True or False

##################################################
def get_json(json_str):
    '''
    @summary: 取json对象
    ---------
    @param json_str: json格式的字符串
    ---------
    @result: 返回json对象
    '''

    return json.loads(json_str) if json_str else {}

def dumps_json(json_):
    '''
    @summary: 格式化json 用于打印
    ---------
    @param json_: json格式的字符串或json对象
    ---------
    @result: 格式化后的字符串
    '''
    try:
        if isinstance(json_, str):
            json_ = get_json(json_)

        json_ = json.dumps(json_, ensure_ascii=False, indent=4, skipkeys = True)

    except Exception as e:
        log.error(e)
        json_ = str(json_)

    return json_

def print(object):
    pprint(object)

def get_json_value(json_object, key):
    '''
    @summary:
    ---------
    @param json_object: json对象或json格式的字符串
    @param key: 建值 如果在多个层级目录下 可写 key1.key2  如{'key1':{'key2':3}}
    ---------
    @result: 返回对应的值，如果没有，返回''
    '''
    current_key = ''
    value = ''
    try:
        json_object = isinstance(json_object, str) and get_json(json_object) or json_object

        current_key = key.split('.')[0]
        value      = json_object[current_key]

        key        = key[key.find('.') + 1:]
    except Exception as e:
            return value

    if key == current_key:
        return value
    else:
        return get_json_value(value, key)

##################################################
def replace_str(source_str, regex, replace_str = ''):
    '''
    @summary: 替换字符串
    ---------
    @param source_str: 原字符串
    @param regex: 正则
    @param replace_str: 用什么来替换 默认为''
    ---------
    @result: 返回替换后的字符串
    '''
    str_info = re.compile(regex)
    return str_info.sub(replace_str, source_str)

##################################################
def get_conf_value(config_file, section, key):
    cp = configparser.ConfigParser(allow_no_value = True)
    with codecs.open(config_file, 'r', encoding='utf-8') as f:
        cp.read_file(f)
    return cp.get(section, key)

################################################
def capture(url, save_fn="capture.png"):
    directory = os.path.dirname(save_fn)
    mkdir(directory)

    browser = webdriver.PhantomJS()
    browser.set_window_size(1200, 900)
    browser.get(url) # Load page
    browser.execute_script("""
            (function () {
              var y = 0;
              var step = 100;
              window.scroll(0, 0);

              function f() {
                if (y < document.body.scroll_height) {
                  y += step;
                  window.scroll(0, y);
                  set_timeout(f, 50);
                } else {
                  window.scroll(0, 0);
                  document.title += "scroll-done";
                }
              }

              set_timeout(f, 1000);
            })();
        """)

    for i in range(30):
        if "scroll-done" in browser.title:
            break
        time.sleep(1)

    browser.save_screenshot(save_fn)
    browser.close()

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        pass

def write_file(filename, content, mode = 'w'):
    '''
    @summary: 写文件
    ---------
    @param filename: 文件名（有路径）
    @param content: 内容
    @param mode: 模式 w/w+ (覆盖/追加)
    ---------
    @result:
    '''

    directory = os.path.dirname(filename)
    mkdir(directory)
    with open(filename, mode, encoding = 'utf-8') as file:
        file.writelines(content)

def read_file(filename, readlines = False):
    '''
    @summary: 读文件
    ---------
    @param filename: 文件名（有路径）
    @param readlines: 按行读取 （默认False）
    ---------
    @result: 按行读取返回List，否则返回字符串
    '''

    content = ''
    with open(filename, 'r', encoding = 'utf-8') as file:
        content = file.readlines() if readlines else file.read()

    return content


def download_file(url, base_path, filename = '', call_func = ''):
    file_path = base_path + filename
    directory = os.path.dirname(file_path)
    mkdir(directory)

    if url:
        try:
            log.debug('''
                         正在下载 %s
                         存储路径 %s
                      '''
                         %(url, file_path))

            request.urlretrieve(url, file_path)

            log.debug('''
                         下载完毕 %s
                         文件路径 %s
                      '''
                         %(url, file_path)
                     )

            call_func and call_func()
            return 1
        except Exception as e:
            log.error(e)
            return 0
    else:
        return 0

def get_file_list(path, ignore = []):
    templist = path.split("*")
    path = templist[0]
    file_type = templist[1] if len(templist) >= 2 else ''

    # 递归遍历文件
    def get_file_list_(path, file_type, ignore, all_file = []):
        file_list =  os.listdir(path)

        for file_name in file_list:
            if file_name in ignore:
                continue

            file_path = os.path.join(path, file_name)
            if os.path.isdir(file_path):
                get_file_list_(file_path, file_type, ignore, all_file)
            else:
                if not file_type or file_name.endswith(file_type):
                    all_file.append(file_path)

        return all_file

    return get_file_list_(path, file_type, ignore) if os.path.isdir(path) else [path]

def rename_file(old_name, new_name):
    os.rename(old_name, new_name)

def del_file(path, ignore = []):
    files = get_file_list(path, ignore)
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
           log.error('''
                删除出错: %s
                Exception : %s
                '''%(file, str(e))
             )
        else:
            log.debug(file + " 删除成功")
        finally:
            pass

#############################################

def exec_js(js_code):
    '''
    @summary: 执行js代码
    ---------
    @param js_code: js代码
    ---------
    @result: 返回执行结果
    '''

    return execjs.eval(js_code)

def compile_js(js_func):
    '''
    @summary: 编译js函数
    ---------
    @param js_func:js函数
    ---------
    @result: 返回函数对象 调用 fun('js_funName', param1,param2)
    '''

    ctx = execjs.compile(js_func)
    return ctx.call

###############################################

def date_to_timestamp(date, time_format = '%Y-%m-%d %H:%M:%S'):
    '''
    @summary:
    ---------
    @param date:将"2011-09-28 10:00:00"时间格式转化为时间戳
    @param format:时间格式
    ---------
    @result: 返回时间戳
    '''

    timestamp = time.mktime(time.strptime(date, time_format))
    return int(timestamp)

def timestamp_to_date(timestamp, time_format = '%Y-%m-%d %H:%M:%S'):
    '''
    @summary:
    ---------
    @param timestamp: 将时间戳转化为日期
    @param format: 日期格式
    ---------
    @result: 返回日期
    '''

    date = time.localtime(timestamp)
    return time.strftime(time_format, date)

def get_current_timestamp():
    return int(time.time())

def get_current_date(date_format = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(date_format)
    # return time.strftime(date_format, time.localtime(time.time()))

def format_date(date, old_format = '', new_format = '%Y-%m-%d %H:%M:%S'):
    '''
    @summary: 格式化日期格式
    ---------
    @param date: 日期 eg：2017年4月17日 3时27分12秒
    @param old_format: 原来的日期格式 如 '%Y年%m月%d日 %H时%M分%S秒'
    @param new_format: 输出的日期格式
    ---------
    @result: 格式化后的日期，类型为字符串 如2017-4-17 3:27:12
    '''

    if not old_format:
        if '年' in date:
            old_format += '%Y年'
        if '月' in date:
            old_format += '%m月'
        if '日' in date:
            old_format += '%d日'
        if '时' in date:
            old_format += ' %H时'
        if '分' in date:
            old_format += '%M分'
        if '秒' in date:
            old_format += '%S秒'

    #print(old_format)
    try:
        date_obj = datetime.datetime.strptime(date, old_format)
        date_str = datetime.datetime.strftime(date_obj, new_format)
    except Exception as e:
        log.error('日期格式化出错，old_format = %s 不符合 %s 格式'%(old_format, date))
        date_str = date
    return date_str

################################################
def get_md5(source_str):
    m = hashlib.md5()
    m.update(source_str.encode('utf-8'))
    return m.hexdigest()

def get_base64(secret, message):
    '''
    @summary: 数字证书签名算法是："HMAC-SHA256"
              参考：https://www.jokecamp.com/blog/examples-of-creating-base64-hashes-using-hmac-sha256-in-different-languages/
    ---------
    @param secret: 秘钥
    @param message: 消息
    ---------
    @result: 签名输出类型是："base64"
    '''

    import hashlib
    import hmac
    import base64

    message = bytes(message, 'utf-8')
    secret = bytes(secret, 'utf-8')

    signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    return signature

##################################################

def cut_string(text, length):
    text_list = re.findall('.{%d}'%length, text, re.S)
    leave_text = text[len(text_list) * length:]
    if leave_text:
        text_list.append(leave_text)

    return text_list