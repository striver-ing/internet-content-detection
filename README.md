# 爬虫框架及数据采集技术文档 #

## 爬虫框架 ##

> 采用Python编写

### 一、需求： ###

互联网爬虫需求量大，网站各式各样。如果每个项目都从零开始编写，繁琐的url管理，网站的解析，信息的筛选，数据的存储将极大的浪费开发时间，并且随着项目的增多，后期管理和维护也很艰难。并且一个项目往往不止对应一个网站，可能需要采集多个网站对应的信息。因此，一款管理这些网站，给开发着提供便捷的框架就必不可少了。本框架需求如下：

1. 使用简单
2. 支持多线
3. 可复用性强

### 二、设计及实现 ###

本框架主要包含3大模块，分别为`base`、`db`、`utils`。

- **base**中主要包含取url的*Collector*，url分发的*ParserControl*，存储数据的base_parser以及管理和启动Controller、ParserControl、parser的*Spider*（parser为具体解析器）。
- **db**中包含*mongodb*、*oracledb*、*mysqldb*的封装，包含增删改查、唯一索引，唯一key的设置。
- **utils**中主要包含*log*的封装，数据导出*export_data*的封装（mongo到oracle/mysql）以及解析网页和常用的方法，集中封装在了*tools*里。
   
架构设计如图2.1所示：

<center>![爬虫架构图](http://i.imgur.com/F9BIB5f.png)</center>
<center>**图2.1**</center>


爬虫架构图解释如下：

1. **main**：添加具体的parser，配置url以及爬取的内容存放的表名，开启程序，伪代码如下：

        def main():
    
            # 程序开始时触发
            def begin_callback():
                log.info('\n********** template begin **********')
        
            # 程序结束时触发
            def end_callback():
                log.info('\n********** template end **********')
        
            # 配置Spider，parser_count 为线程数，为空时Spider从配置文件中读取，parser_params 可携带参数到parser中
            spider = Spider(tab_urls = 'template_urls', tab_site = 'template_site_info', tab_content = 'template_content_info', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})
        
            # 添加parser
            spider.add_parser(xxx_parser)
            spider.add_parser(yyy_parser)
        
            spider.start()

2. **Spider**：启动Collector、ParserControl以及parsers，Collector起1线，ParserControl起多线，线程数如果main没指定，可从配置文件中读取，parser启动添加网站和根url的方法，线程数为1。同时触发main中的begin_callback回调函数。并且设置url表和内容表的唯一key，防止信息重复。还设置了唯一索引，加快数据的读取。伪代码如下：
    
        class Spider(threading.Thread):
            def __init__(self, tab_urls, tab_site, tab_content, parser_count = None, parser_params = {}, begin_callback = None, end_callback = None, content_unique_key = 'url'):
                '''
                @summary:
                ---------
                @param tab_urls:        url表名
                @param tab_site:        网站表名
                @param parser_count:    parser 的线程数，为空时以配置文件为准
                @param parser_params :  解析器所用的參數
                @param begin_callback:  爬虫开始的回调
                @param end_callback:    爬虫结束的回调
                ---------
                @result:
                '''
                # 设置唯一key
                # 设置唯一索引
    
            def add_parser(self, parser):
                # 添加parser

            def __start(self):
                # 启动开始的回调
                if self._begin_callback:
                    self._begin_callback()

                # 开启Collector
                # 开启parser的添加网站和根url的方法
                # 根据线程数个数，开启多个ParserControl

3. **parser**：网站解析器。解析具体的网站，这部分也要开发者根据需要，自定义解析过程。解析工具tools里面已经很全面了，可以直接调用。伪代码如下：

        # 必须定义 网站id, ParserControl根据site_i来分发url
        SITE_ID = 1
        # 必须定义 网站名, ParserControl根据name来添加解析器，名字不在配置文件需要爬取的网站中的则不添加 
        NAME = '淘宝'
        
        # 必须定义 添加网站信息
        def add_site_info():
            pass
        
        # 必须定义 添加根url
        def add_root_url(parser_params = {}):
            pass
        
        # 必须定义 解析网址
        def parser(url_info):
            # 1. 解析界面源代码
            # 2. 取需要的信息
            # 3. 更新根url状态已做完

4. **base_parser**：base_parser里主要定义了一些存放数据的统一接口，例如：

        def add_url(table, site_id, url, depth = 0, remark = '', status = Constance.TODO):
            pass

        def update_url(table, url, status):
            pass
    
        def add_website_info(table, site_id, url, name, domain = '', ip = '', address = '', video_license = '', public_safety = '', icp = ''):
           pass

5. **Collector**：每隔一段时间从数据库中取指定数量的url，存到url环形队列中，待ParserControl读取。支持多个ParserControl同时读取。采用Collector的目的是防止多个线程同时从数据库中取同一个url，采用环形队列是为了防止内存的频繁开销，可以有效的利用资源，并且防止了数组的频繁移动。伪代码如下：

        class Collector(threading.Thread):
            def __init__(self, tab_urls):
                # 1. 初始时将正在做的任务至为未做，好让parser重新做
                # 2. 定义一个环形队列

            def __input_data(self):
                # 1. 取未做的url，连续5次取不到数据库中正在做的url数量为0时结束Collector, 并触发main中的end_callback回调函数
                # 2. 将数据库中对应的url更新为正在做
                # 3. 加锁
                # 4. 存url到环形队列，需要判断还能存放多少，取的url数量不能大于队列剩余空间
                # 5. 解锁
            def get_urls(self, count):
                # 1. 加锁
                # 2. 判断队列可读空间，取的url数量不能大于可读空间
                # 3. 取出指定数量的url
                # 4. 解锁
                # 5. 返回urls

6. **ParserControl**： 每隔一段时间从Collector中取指定数量的url，然后根据url的site_id分配给指定的parser进行解析，伪代码如下：

        class  PaserControl(threading.Thread):
            def __init__(self, collector, tab_urls):
                # 1. 初始化parsers列表
        
            def run(self):
                while True:
                    try:
                        # 1. 判断Collector是否结束，结束跳出
                        # 2. 从Collector中取指定数量的url到urls列表中
                        for url in urls：
                            for parser in parsers：
                                if parser.site_id = url.site_id:
                                      try:
                                        parser.parser(url) # 解析url
                                      except:
                                        # 更新改url异常
                                      break     
        
            def add_parser(self, parser):
                self._parsers.append(parser)

7. **tools**：爬虫工具，封装了数据采集的一些常用的方法，parser可以直接调用，现有的方法有：

        # 装饰器
        def log_function_time(func)
        def run_safe_model(module_name)

        # 解析网页相关
        def get_html_auto_deal_code(url)
        def get_html_by_urllib(url, code = 'utf-8')
        def timeout_handler(response)
        def get_html_by_webdirver(url)
        def get_html_by_requests(url, headers = '', code = 'utf-8')
        def get_json_by_requests(url, params = None, headers = '', data = None)
        def get_urls(html, stop_urls = [])
        def get_full_url(root_url, sub_url)
        def joint_url(url, params)
        def fit_url(urls, identis)
        def get_info(html, regexs, allow_repeat = False, fetch_one = False)
        def get_domain(url)
        def get_tag(html, name = None, attrs = {}, find_all = True)
        def get_text(soup, *args)
        def del_html_tag(content, except_line_break = False)
        def is_have_chinese(content)
        def get_json(json_str)
        def dumps_json(json_)
        def get_json_value(json_object, key)
        def replace_str(source_str, regex, replace_str = '')

        # 文件相关
        def get_conf_value(config_file, section, key)
        def capture(url, save_fn="capture.png")
        def mkdir(path)
        def write_file(filename, content, mode = 'w')
        def download_file(url, base_path, filename = '', call_func = '')
        def get_file_list(path, ignore = [])
        def get_file_list_(path, file_type, ignore, all_file = [])
        def rename_file(old_name, new_name)
        def del_file(path, ignore = [])

        # js相关
        def exec_js(js_code)
        def compile_js(js_func)

        # 日期相关
        def date_to_timestamp(date, time_format = '%Y-%m-%d %H:%M:%S'):
        def timestamp_to_date(timestamp, time_format = '%Y-%m-%d %H:%M:%S'):
        def get_current_timestamp()
        def get_current_date(date_format = '%Y-%m-%d %H:%M:%S'):
        def format_date(date, old_format, new_format = '%Y-%m-%d %H:%M:%S'):
        
        # 加密相关
        def get_md5(source_str)
        def get_base64(secret, message)

8. **ExportDate**： 导数据模块，可将mongo中的数据导入到mysql或者oracle，思想如下：

        # 1. 取mongo中的数据
        # 2. 拼接sql
        # 3. 调用db下相关封装的相关数据库，执行sql
        # 4. 将导过的数据在mongodb里至为已做

采集操作：

1. 编写parser，实现上面parser所述的必须定义的方法及属性
2. 在config.conf的spider_site中配置需要爬取的网站，与parser对应。如下：

        [spider_site]
        # 需要爬取的网站 all为全部爬取
        # spider_site_name = all
        spider_site_name = cctv
        # 不爬取的网站，紧当spider_site_name = all时生效
        except_site_name =

3. 在main中添加parser，并配置spider
4. 运行main，开始采集数据

>本框架有个使用模板template,可以参考，目录结构如下：

    template
     └─parsers
        └─__init__.py
        └─xxx_parser.py
        └─yyy_parser.py
     └─main.py
     └─export_date.py

导数据操作：

    # export.py
    def main():
        # 导出数据
        key_map = {
            'aim_key1' : 'str_source_key1',          # 目标键 = 源键对应的值         类型为str
            'aim_key2' : 'int_source_key2',          # 目标键 = 源键对应的值         类型为int
            'aim_key3' : 'date_source_key3',         # 目标键 = 源键对应的值         类型为date
            'aim_key4' : 'vint_id',                  # 目标键 = 值                   类型为int
            'aim_key5' : 'vstr_name',                # 目标键 = 值                   类型为str
            'aim_key6' : 'sint_select id from xxx'   # 目标键 = 值为sql 查询出的结果 类型为int
            'aim_key7' : 'sstr_select name from xxx' # 目标键 = 值为sql 查询出的结果 类型为str
        }
    
        export_data = ExportData()
        export_data.export_to_oracle(source_table = '', aim_table = '', key_map = key_map, unique_key = 'url')

    # key_map为源表和目标表的键值对应关系，xxx_source_key其中xxx为目标表对应键的类型, source_key为源表中对应的键。vxxx_source_key表示直接传值，如vint_1则直接传整形的1，sxxx_***表示sql语句，如先查询一个值，将此值作为value存在对应的目标键中。
    # unique_key为目标表的唯一key，为空的话不设置

## 数据采集 ##

> 使用Google chrome浏览器

### 舆情类 ###

舆情信息的抓取一般比较简单，步骤如下：

1. 打开带爬取的界面，右键查看源代码
2. 观察源代码中是否有想要的信息，若有则观察上下文的关系
3. 根据上下文的关系写正则，或者用BeautifulSoup直接取信息
4. 若源代码中没有想要的信息，需要抓包。按F12或右键检查，工具里面有个Network，可以看到数据包的传输，观察数据包，想要的数据可能在json里。

采用此策略爬取的网站有：

- CCTV、凤凰、人民、新浪、搜狐、腾讯、网易、新华、百度贴吧、
泸州人民政府公众信息网、江阳区人民政府公众信息网、龙马潭区人民政府公众信息网、纳溪人民政府公众信息网、泸县人民政府公众信息网、合江县人民政府公众信息网、叙永人民政府公众信息网、古蔺人民政府公众信息网、四川医科大学、四川警察学院、泸州职业技术学院、四川化工职业技术学院、泸州高中、泸州天立国际学校 、四川省泸县第二中学、网盘搜、bt磁力链、搜百度盘、豆瓣网、应用宝、360手机助手、百度手机助手、安卓市场、坐享小说、极速漫画、动漫啦漫画



### 视听类 ###

1. 打开带爬取的界面，右键查看源代码
2. 观察源代码中是否有想要的信息，若有则观察上下文的关系
3. 根据上下文的关系写正则，或者用BeautifulSoup直接取信息
4. 若源代码中没有想要的信息，需要抓包。按F12或右键检查，工具里面有个Network，可以看到数据包的传输，观察数据包，想要的数据可能在json里。
5. 视频连接可能需要拼地址，有的参数在页面源代码中，有的在json或js文件中，具体问题具体分析。还有的视频地址是加密的，比如今日头条，需要找到解密的方法，这类方法往往在js文件中。还有的视频地址单单通过网页端是找不到的，比如爱奇艺，这时可以抓取手机端视频下载时的数据包，往往里面就有视频地址，然后分析改数据包的请求参数，可以网页端和手机端结合看看是否能拼出该参数。然后模拟手机发请求，这样就可以得到视频地址。

采用此策略爬取的网站有：

- 土豆、优酷、爱奇艺、腾讯视频、网易、PPTV、第一视频、酷6、响巢看看、泸州视频、泸州汽车网、cctv、新浪、乐视、电影网、时光网、PPS、暴风影音、爆米花网、我友网、视友网、新浪、芒果TV、搜狐、风行网，陌陌、花椒

### 手机端 ###

1. 下载抓包工具，Window端可以使用Fiddler, 然后设置手机端和Fiddler端的代理，手机端需要安装证书，具体设置方法可以参考[http://wenku.baidu.com/link?url=Btte5masFQzTB93bEcTGLMxP-1fuQ1Pxboqvm4JsOohzRGk171Bvth041McxYsqElDEd162NLq9ubuutRZyY8knRfmjU-2xvHslE-vy3ztW](http://wenku.baidu.com/link?url=Btte5masFQzTB93bEcTGLMxP-1fuQ1Pxboqvm4JsOohzRGk171Bvth041McxYsqElDEd162NLq9ubuutRZyY8knRfmjU-2xvHslE-vy3ztW "Fiddler对android应用手机抓包图文教程")
2. 手机端打开app，开始抓包，分析数据包，找到想要的数据。然后看该数据包的请求参数。通常模拟该请求参数发送请求即可返回和手机端一样的数据包，若没有返回，还需要模拟手机端的请求头。返回的数据一般为json数据，然后取需要的信息。

采用此策略爬取的网站有：

- 今日头条、映客、爱奇艺

### 翻页 ###

有页码：

> 通常为浏览器端（web）

1. 切换页面，看浏览器地址栏中地址的变化，找出表示页码的参数及页码和该参数对应的关系，模拟该地址的变化规律，拼出每页的url

上拉加载：

> 分为浏览器端和手机app端

1. 浏览器端：按F12，然后上拉网页，加载更多信息，观察检查工具里的Network，会有某个请求就是翻页的。
2. 手机端：打开需要采集信息的软件，用抓包工具抓包，上拉需要采集信息的栏目，观察抓包工具里的数据包，随着不断的上拉，每一次的数据加载，都会有一次数据请求，找到该请求（可由求情返回的data排查），然后比较每次请求的参数变化，找到变化规律及意义，即可模仿下一次请求，获更多的数据。


        

