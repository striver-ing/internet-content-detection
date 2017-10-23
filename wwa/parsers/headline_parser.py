# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import random
from db.mongodb import MongoDB
import base.constance as Constance
from db.oracledb import OracleDB
from wwa.config.headline_city import *

db = MongoDB()
oracledb = OracleDB()

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '今日头条'

# 解析视频url
PARSE_VIDEO_URL_JSFUNC = '''
function base64decode (e) {
    var t, r, n, o, i, a, u, l = [ - 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1, -1, -1];
    for (a = e.length, i = 0, u = ""; i < a;) {
        do t = l[255 & e.charCodeAt(i++)];
        while (i < a && t == -1);
        if (t == -1) break;
        do r = l[255 & e.charCodeAt(i++)];
        while (i < a && r == -1);
        if (r == -1) break;
        u += String.fromCharCode(t << 2 | (48 & r) >> 4);
        do {
            if (n = 255 & e.charCodeAt(i++), 61 == n) return u;
            n = l[n]
        } while ( i < a && n == - 1 );
        if (n == -1) break;
        u += String.fromCharCode((15 & r) << 4 | (60 & n) >> 2);
        do {
            if (o = 255 & e.charCodeAt(i++), 61 == o) return u;
            o = l[o]
        } while ( i < a && o == - 1 );
        if (o == -1) break;
        u += String.fromCharCode((3 & n) << 6 | o)
    }
    return u
}
'''

ONE_PAGE_TIME_INTERVAL = 3600
FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'wwa_save_path')
NEWS_LOCAL =  1
VIDEO      = 2
STORAGE_ID = 2

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_app_site_info'
    url = 'http://sj.qq.com/myapp/detail.htm?apkName=com.ss.android.article.news'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    base_url = 'http://is.snssdk.com/api/news/feed/v51/'

    params = 泸州

    time_interval = ONE_PAGE_TIME_INTERVAL
    content_released_time = tools.get_current_timestamp() - 86400 * 30 # 一天
    current_timestamp = tools.get_current_timestamp()

    max_behot_time = current_timestamp
    while max_behot_time >= content_released_time:
        max_behot_time -= time_interval

        current_timestamp = current_timestamp + random.randint(60, 300)

        # 泸州的文章
        params['category'] = 'news_local'
        params['last_refresh_sub_entrance_interval'] = current_timestamp# + random.randint(60, 300)
        params['max_behot_time'] = max_behot_time

        url = tools.joint_url(base_url, params)
        base_parser.add_url('WWA_app_urls', SITE_ID, url, remark = NEWS_LOCAL)

        # 视频
        params['category'] = 'video'
        params['last_refresh_sub_entrance_interval'] = current_timestamp# + random.randint(60, 300)
        params['max_behot_time'] = max_behot_time

        url = tools.joint_url(base_url, params)
        base_parser.add_url('WWA_app_urls', SITE_ID, url, remark = VIDEO)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    column_id = remark

    headers = {
        'Host': 'is.snssdk.com',
        'Accept':' */*',
        'X-SS-Cookie': '_ba=BA0.2-20170101-51e32-mV0oh6KwzUmWxXl227kO; install_id=8738029911; ttreq=1$b34d173d3544397b1ca82d19a58a7db80e2aef29; qh[360]=1; alert_coverage=33; _ga=GA1.2.1084363974.1479979043; login_flag=cd47dd57ff2f963719bc324163954696; sessionid=3554607744525de375854663cc7e355b; sid_guard="3554607744525de375854663cc7e355b|1489461314|2592000|Thu\054 13-Apr-2017 03:15:14 GMT"; sid_tt=3554607744525de375854663cc7e355b',
        'tt-request-time': '1489990271848',
        'Cookie':' _ba=BA0.2-20170101-51e32-mV0oh6KwzUmWxXl227kO; install_id=8738029911; ttreq=1$b34d173d3544397b1ca82d19a58a7db80e2aef29; qh[360]=1; alert_coverage=33; _ga=GA1.2.1084363974.1479979043; login_flag=cd47dd57ff2f963719bc324163954696; sessionid=3554607744525de375854663cc7e355b; sid_guard="3554607744525de375854663cc7e355b|1489461314|2592000|Thu\054 13-Apr-2017 03:15:14 GMT"; sid_tt=3554607744525de375854663cc7e355b',
        'User-Agent': 'News/6.0.1 (iPhone; iOS 10.2.1; Scale/3.00)',
        'Accept-Language':' zh-Hans-CN;q=1, en-CN;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection':' keep-alive'
    }

    json = tools.get_json_by_requests(root_url)

    if not json:
        base_parser.update_url('WWA_app_urls', root_url, Constance.EXCEPTION)
        return

    datas = json['data']
    for data in datas:
        data = tools.get_json_value(data, 'content')

        title = tools.get_json_value(data, 'title')

        # 检测数据库中是否存在，若存在则退出
        if db.find('WWA_app_content_info', {'title':title}):
            continue

        abstract = tools.get_json_value(data, 'abstract')
        abstract = abstract and abstract or tools.get_json_value(data, 'content')

        img_url = tools.get_json_value(data, 'image_list.url')
        img_url = img_url and  img_url or tools.get_json_value(data, 'middle_image.url')
        img_url = img_url and  img_url or tools.get_json_value(data, 'large_image_list.url')
        img_url = img_url and img_url.replace('.webp', '.jpg') or img_url

        original_url = tools.get_json_value(data, 'article_url')
        original_url = original_url and original_url or tools.get_json_value(data, 'share_url')

        release_time = tools.get_json_value(data, 'publish_time')
        release_time = release_time and release_time or tools.get_json_value(data, '1481012423')
        release_time = release_time and tools.timestamp_to_date(release_time) or release_time

        video_msg = tools.get_json_value(data, 'video_play_info') #需要处理
        video_main_url = tools.get_json_value(video_msg, 'video_list.video_2.main_url')
        video_main_url = video_main_url and video_main_url or tools.get_json_value(video_msg, 'video_list.video_1.main_url')
        parse_video_url = tools.compile_js(PARSE_VIDEO_URL_JSFUNC)
        video_url = parse_video_url('base64decode', video_main_url)

        html = tools.get_html_auto_deal_code(original_url)
        regexs = [
            'class="article-content">(.*?)<div class="article-actions">',
            '<div class="content">(.*?)<div class="suggestion-list-con"',
            '<!-- 文章内容 -->(.*?)<!-- @end 文章内容 -->',
            'class="yi-content-text">(.*?)<div class="yi-normal"',
            '<p.*?>(.*?)</p>'
        ]

        if video_url:
            content = abstract
        else:
            content = ''.join(tools.get_info(html, regexs))
            content = tools.del_html_tag(content)

        if len(content) < len(abstract):
            content = abstract

        # 敏感事件
        sensitive_id = ''
        sensitive_event_infos = oracledb.find('select t.id, t.keyword1, t.keyword2, t.keyword3 from tab_mvms_sensitive_event t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time')
        for sensitive_event_info in sensitive_event_infos:
            _id = sensitive_event_info[0]
            keyword1 = sensitive_event_info[1].split(',') if sensitive_event_info[1] else []
            keyword2 = sensitive_event_info[2].split(',') if sensitive_event_info[2] else []
            keyword3 = sensitive_event_info[3].split(',') if sensitive_event_info[3] else []

            if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
                sensitive_id = _id
                break

        # 违规事件
        violate_id = ''
        vioation_knowledge_infos = oracledb.find('select t.id, t.keyword1, t.keyword2, t.keyword3 from tab_mvms_violation_knowledge t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time')
        for vioation_knowledge_info in vioation_knowledge_infos:
            _id = vioation_knowledge_info[0]
            keyword1 = vioation_knowledge_info[1].split(',') if vioation_knowledge_info[1] else []
            keyword2 = vioation_knowledge_info[2].split(',') if vioation_knowledge_info[2] else []
            keyword3 = vioation_knowledge_info[3].split(',') if vioation_knowledge_info[3] else []


            if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
                violate_id = _id
                break

        log.debug('''
            title:          %s
            abstract :      %s
            img_url :       %s
            original_url:   %s
            release_time :  %s
            video_main_url: %s
            video_url:      %s
            content :       %s
            column_id:      %d
            sensitive_id:   %d
            violate_id:     %d

            '''
            %(title, abstract, img_url, original_url, release_time, video_main_url, video_url, content, column_id, sensitive_id and sensitive_id or 0, violate_id and violate_id or 0)
            )

        # 如果是视频栏 并且不包含敏感或违法信息 则不下载
        if column_id == VIDEO:
            if not sensitive_id and not violate_id:
                continue

        # 下载
        base_path = FILE_LOCAL_PATH
        is_download = 0

        # 下载图片
        img_name = ''
        if img_url:
            img_name = 'headlines/images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
            is_download = tools.download_file(img_url, base_path, img_name)
            if not is_download:
                img_name = ''

        sexy_image_url = base_path + img_name if img_name else img_url


        # 下载视频
        video_name = ''
        if video_url:
            video_name = 'headlines/videos/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.mp4'
            is_download = tools.download_file(video_url, base_path, video_name)
            if not is_download:
                video_name = ''

        if original_url:
            base_parser.add_wwa_app_content_info('WWA_app_content_info', SITE_ID, title, abstract, img_url, img_name, original_url, release_time, video_url, video_name, content, column_id, is_download, sensitive_id, violate_id, STORAGE_ID, sexy_image_url)


    base_parser.update_url('WWA_app_urls', root_url, Constance.DONE)

if __name__=='__main__':
    # title = '黑边眼镜后的炯炯目光——追思横堀克己先生'
    # content = '横堀先生早年在北京受到邓小平等国家领导人接见时的合影。（横堀先生：第二排右五）《人民中国》杂志社编辑顾问横堀克己先生去年12月因病逝世。3月18日，朝日新闻社、日中未来之会和人民中国杂志社共同主办缅怀横堀先生的追思大会。家人、好友，曾经一同工作的同事约150人与会。下午两点，日本记者俱乐部会场内庄严肃穆，来宾向横堀先生的遗像献花。之后，追思会主办方代表先后发言，人民中国杂志社东京支局代表代读了社长陈文戈从北京本社发来的致辞。与会嘉宾观看幻灯影像回顾了横堀先生的一生。通过会场陈列的刊登有横堀先生执笔文章的《朝日新闻》和《人民中国》杂志，人们再次深切感受到他对中国的深情，对日中友好的不懈努力。追思会前，东京支局记者来到横堀先生家探望雅子夫人。窗明几净、一尘不染的居室依旧如昨，横堀先生的骨灰和遗像安放在客厅。听雅子夫人说起往事，记者几次泪湿眼眶。今天就来和大家一起分享雅子夫人和众人讲述的横堀先生的故事。我和先生克己是中学的同班同学。他曾在被称为皇室子弟学校的学习院读书，但觉得校规严苛，难忍束缚，便转校到了我就读的中学。那年我们是初中二年级。他成绩优秀，而且能在人前毫不避讳地阐述意见，因此转校没多久就当上了班干部。我也是班委会委员，便很自然地和他交往起来。之后我们上了不同的高中，不同的大学，虽然我有些不舍，但那时我还是想，我们的人生就此分道扬镳了吧。然而，一个不可思议的机会让我们再次相遇。不过那时我已经大学毕业，并且有了谈婚论嫁的对象。在克己猛烈的追求之下，我拒绝了先前的婚约，决定嫁给他。在朝日新闻社工作的横堀先生（右）当时克己在读大学四年级，有志成为一名学者，并且已经决定继续读研深造。可他却对我说：“若是没个像样的工作，没法向你的父母交代”。于是他放弃了学者之路，为找工作又留校一年。最后他成功地通过了朝日新闻的录取考试。我们的婚礼在他毕业典礼的前一天举行。他对做我们证婚人的大学教授说：“明天我要去新婚旅行了，无法参加毕业典礼，请老师帮我保存毕业证书吧。”能说出这样的话，克己真是一个不拘泥繁文缛节的人啊。克己本就擅长中国古汉语，又对中国历史抱有浓厚的兴趣。在东京大学读书时他选修的外语就是中文。他还成立了中国研究会，并为宣传普及中国研究，在日本全国的大学之间奔走。这时，与东大同在文京区的日中友好协会进入了他的视野，就这样与《人民中国》杂志相遇了。连同中国研究会的活动一起，克己在街头卖起了《人民中国》。那时候他肯定没想到，以后他会成为编辑这本杂志的人。在朝日新闻社，为了从事与中国有关的报道工作，克己选择了外报部。形象光鲜的记者无不出自政经领域，如此，克己便毫无悬念地与出人头地的事业路线无缘了。尽管如此，这个信念让他加入外报部的志愿毫不动摇，日中实现邦交正常化的1972年，他被派往香港大学留学一年。也是那年，我们的第三个儿子出生了。克己给他取名“友生”，正有日中友好之意。横堀先生在朝日新闻北京支局工作1977年，克己如愿以偿地来到外报部。1981年末起常驻北京。我带着两个孩子也一起去了北京。他作为驻北京支局的记者工作了3年，回国后成为朝日新闻的论说委员。1990年，他作为支局长再次被派往北京，又在那里住了3年。随他生活在异国他乡，我并不感到不适。想来，我其实出生在中国长春，4岁时回到日本，不过当时几乎没有留下什么记忆。可能正是这个缘分，上世纪八九十年代，在尚不发达、生活不便的北京，我也没觉得受了什么苦。我父亲曾是到伪满洲国工作的保险公司职员，常听他说起战后遣返日侨时，他受到许多中国人的厚待和照顾。这使得我无形中也对中国产生了一种憧憬之情。横堀先生（左二）深入中国农村采访机缘之间，从2001年起克己开始了在《人民中国》杂志社的工作。在此之前一直作为日本记者从“外”看中国，如今可以在中国的“里边”观察体会了。对此，克己格外欣喜。是因为在《人民中国》杂志社工作交到许多中国朋友，终于有了融入中国社会的感觉吧。克己采访的宗旨是“恪守信义”，尊重对方才能建立信任。他不会一味报道负面，而是正反两面客观阐述，积极、消极掌握平衡。我想正是这些孜孜不倦的努力，使他在人民中国的工作中集大成，也成为日后回国创立“日中未来之会”的基础。友谊奖奖章和证书。在人民中国杂志社工作期间，横堀先生曾受到时任总理温家宝的接见。到人民中国社工作两年半后，克己突然听到他获得“友谊奖”的消息，着实吃了一惊。友谊奖获得者多为诸如JICA这样的大团体、大企业，颁发给个人的情况少之又少。中国外文局获此殊荣的外国专家，历史上也仅有国际著名记者、作家伊斯雷尔·爱泼斯坦一人。可想而知，得知获奖消息后我们夫妇有多么惊讶。作为外国记者，多次采访过国庆节庆典和招待会，而今作为人民中国的社员，克己成了被邀请的嘉宾。温家宝总理亲自来到跟前祝酒碰杯的情景，令他永生难忘。2010年回到日本后才3年，克己癌症病发，并被确认为晚期。他一边注射抗癌药剂，一边继续组织日中未来之会的活动和担任《人民中国》的编辑顾问。拖着病弱的身躯，他还两次访问中国。一生为促进日中相互理解鞠躬尽瘁，对中国的爱永无尽头。失去了这样的丈夫，我至今沉浸在无尽的悲伤之中，心绪难平。雅子夫人与横堀先生在“友谊奖”颁奖仪式上的合影克己是个自由主义者，也是他这个年代的人里少有的能够肯定主妇价值的人。新婚之际，他对我说：“夫妇关系也是人与人的关系，主妇也是地位平等的。你做自己喜欢的事情就好了，我会尊重你的想法。”他也是这样做的。而我从结婚的那一天起，便认定要一生支持他，只要和他在一起，无论到哪里都愿意。我也是这样做的。病情不断恶化，已知不久于人世的时候，克己轻声对我说：“我们二人一心同体”。这句话时时在我心头萦绕，仿佛克己不曾离去。我决定在我入土之前把他的骨灰一直放在家里，今后，他依然和我在一起。南村志郎：日中未来之会代表我与横堀先生初识于朝日新闻记者时代，那时我们都很忙，好像没有就日中问题展开过长时间的讨论。3年前，我们共同创立了日中未来之会，如何打开日中关系现状，我们能为此做些什么，促膝长谈，忘却了时间。最后，我们都说，日中关系这样下去，我们死不瞑目。此后，我们通过各种交流机会，向中方阐述想法，讨论互动，终于仿佛看到前方微弱的曙光。2015年11月，北京、上海、广州之旅令我难忘。那时候横堀先生身体虚弱，伴随着剧痛，与病魔苦斗着走完了那次旅程。他对中国的强烈信念，以及支持他的夫人，这一路我学到了很多。我们必将继承横堀先生的遗志，未来之会全体成员一同为两国关系改善而继续努力。这是我对他的约定。亘理信雄：朝日新闻、外报OB会干事长说起横堀先生，大家脑海中便会浮现出那黑边眼镜里透出的如炬目光。他是国际报道的大前辈。我1985年来到外报部时，横堀先生正在担任主编，我的第一篇稿子便是他指教的。我不懂汉语，横堀先生就指点我说：“不恶补一下中文吗？”由此我感到，为了拓宽对华报道的视野，平日里他是多么努力啊。横堀先生离开朝日新闻后，通过在《人民中国》杂志社的工作和日中未来之会的活动，一生从事与中国有关的事业。敏锐的视角，时而辛辣的语气，一谈起中国，总会忘记时间。而对于后辈，他充满人情味儿，让我们感到温暖。今天，来自朝日新闻各个部门的老同事汇聚于此，追思横堀先生。我想他在天堂，黑边眼镜后边的炯炯目光，一定在注视着我们。苏海河：经济日报记者我与横堀先生交往将近30年，感觉他就像一位老师。横堀先生肺部疾患已有几年。记得两年前他出院后体力稍有恢复，又去了一趟北京，约我见面。我深深地拥抱了他，他向我描述了与医生打交道的一些场景。有一次横堀先生去医院，家属为了让他节省体力，用轮椅推着他去的。结果医生见此状况，怕抗癌剂再给病人添负担，便建议保守治疗。横堀先生嗖地一下站了起来说：“我能走，我体力没问题”，医生看到这一情况才同意继续治疗。讲述这一故事时，横堀先生发出了爽朗的笑声。先生仙逝之后，他为《风雨东京路》撰写的文章在《人民中国》《光明日报》、中国青年网、驻日记者微信群等报纸、杂志、网络及微信群上转发，大家都是想以此纪念横堀先生。在我脑海保留的永远是先生的笑容。为横堀先生祈冥福。陈文戈：人民中国杂志社社长横堀克己先生是我社原编委，也是中国外文局和我社终身顾问。2001年，他来到我社担任外国专家，多次和我社采访团队深入中国基层采访，并影响带动年轻记者扎实报道。2003年非典肆虐北京，他不顾日本政府劝日侨回国的呼吁，也婉拒了中国外文局劝其回国的照顾性安排，和中国同事一道坚守岗位。就这样，在夫人雅子的陪伴与照料下，横堀克己先生在我社一干就是整整九年，直到2010年二人才一起回到日本。他满腔热情地向日本读者介绍中国的改革开放，主张深入推动中日友好，因而遭到了日本右翼刊物的诋毁，而他却完全不为之所动。一个将生命献给中日人民友好事业的人永远地离开了我们，但横堀克己先生的精神必将永存。长远来看，中日关系必将能够经受住风雨的考验，最终走向转圜。横堀雅子文、图片：横堀雅子翻译：于文中日民众相互了解的桥梁和纽带'
    # # 敏感事件
    # sensitive_id = ''
    # sensitive_event_infos = oracledb.find('select * from tab_mvms_sensitive_event')
    # for sensitive_event_info in sensitive_event_infos:
    #     _id = sensitive_event_info[0]
    #     keyword1 = sensitive_event_info[3].split(',') if sensitive_event_info[3] else []
    #     keyword2 = sensitive_event_info[4].split(',') if sensitive_event_info[4] else []
    #     keyword3 = sensitive_event_info[5].split(',') if sensitive_event_info[5] else []

    #     # print(keyword1)
    #     # print(keyword2)
    #     # print(keyword3)

    #     if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
    #         sensitive_id = _id
    #         print(_id)
    #         print(keyword1)
    #         print(keyword2)
    #         print(keyword3)

    # # 违规事件
    # violate_id = ''
    # vioation_knowledge_infos = oracledb.find('select * from tab_mvms_violation_knowledge')
    # for vioation_knowledge_info in vioation_knowledge_infos:
    #     _id = vioation_knowledge_info[0]
    #     keyword1 = vioation_knowledge_info[2].split(',') if vioation_knowledge_info[2] else []
    #     keyword2 = vioation_knowledge_info[3].split(',') if vioation_knowledge_info[3] else []
    #     keyword3 = vioation_knowledge_info[4].split(',') if vioation_knowledge_info[4] else []

    #     if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
    #         print(_id)
    #         print(keyword1)
    #         print(keyword2)
    #         print(keyword3)
    #         violate_id = _id

    # print(sensitive_id)
    # print(violate_id)
    pass

