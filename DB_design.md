互联网内容检测
=======

数据库设计：
------

>**数据库名： `internet_content_detection `**

需要图片鉴黄的数据加上一下两个字段  

* sexy_image_status   淫秽色情图像，多个逗号分隔
* sexy_image_url      淫秽色情图像地址，多个逗号分隔
* image_pron_status   图片扫描状态

### 互联网舆情监测系统 Op_###
网站表 `Op_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id|||| 网站id |
|name|||| 网站名|
|domain||||域名|
|url||||网址|
|ip||||服务器ip|
|address||||服务器地址|
|video_license||||网络视听许可证|
|public_safety||||公安备案号|
|icp||||ICP号|
|read_status||||读取状态|
|record_time||||记录时间|

urls表 `Op_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

关键词表 `Op_keywords`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|keyword_id||||关键字id|
|keyword||||关键字|
|nature ||||性质 （-2， -1， 0， 1， 2）|

内容信息表 `Op_content_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|content||||内容|
|content_spilt||||内容分词，词语和词语之前用逗号分割|
|author||||作者|
|url||||原文url|
|origin||||来源|
|watched_count||||观看数|
|comment_count||||评论数|
|share_count||||分享数|
|praise_count||||点赞数|
|release_time||||发布时间|
|record_time||||记录时间|
|site_id||||网站id|
|keyword_id|varchar|||关键词id（多个关键词id用逗号分割）|
|nature ||||性质 （-2， -1， 0， 1， 2）|
|classify||||类别（如：热点，网民话题）|
|read_status||||读取状态（0 没读， 1读取）|

---

### 手机APP舆情监测系统 OpApp_ ###

app信息表 `OpApp_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id||||app id|
|name||||标题|
|summary||||简介|
|update_info||||更新信息|
|author||||作者|
|url||||原文url|
|app_url||||app下载的url|
|image_url||||图片url（多个url逗号分割）|
|classify||||分类|
|size||||大小|
|tag||||版本|
|platform||||平台（ios / android）|
|download_count||||下载次数|
|release_time||||发布时间|
|record_time||||记录时间|
|read_status||||读取状态（0 没读， 1读取）|

urls表 `OpApp_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

关键词表 `OpApp_keywords`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|keyword_id|||||
|keyword|||||
|nature ||||性质 （-2， -1， 0， 1， 2）|

内容信息表 `OpApp_content_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|content||||内容|
|content_spilt||||内容分词，词语和词语之前用逗号分割|
|author||||作者|
|url||||原文url|
|origin||||来源|
|watched_count||||观看数|
|comment_count||||评论数|
|share_count||||分享数|
|praise_count||||点赞数|
|release_time||||发布时间|
|record_time||||记录时间|
|site_id||||网站id|
|keyword_id|varchar|||关键词id（多个关键词id用逗号分割）|
|nature ||||性质 （-2， -1， 0， 1， 2）|
|classify||||类别（如：热点，网民话题）|
|read_status||||读取状态（0 没读， 1读取）|

---
### 微博舆情监测系统 OpWB_ ###
网站表 `OpWB_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id|||| 网站id |
|name|||| 网站名|
|domain||||域名|
|url||||网址|
|ip||||服务器ip|
|address||||服务器地址|
|video_license||||网络视听许可证|
|public_safety||||公安备案号|
|icp||||ICP号|
|read_status||||读取状态|
|record_time||||记录时间|

urls表 `OpWB_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

关键词表 `OpWB_keywords`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|keyword_id|||||
|keyword|||||
|nature ||||性质 （-2， -1， 0， 1， 2）|

内容信息表 `OpWB_content_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|content||||内容|
|content_spilt||||内容分词，词语和词语之前用逗号分割|
|author||||作者|
|url||||原文url|
|origin||||来源|
|watched_count||||观看数|
|comment_count||||评论数|
|share_count||||分享数|
|praise_count||||点赞数|
|release_time||||发布时间|
|record_time||||记录时间|
|site_id||||网站id|
|keyword_id|varchar|||关键词id（多个关键词id用逗号分割）|
|nature ||||性质 （-2， -1， 0， 1， 2）|
|classify||||类别（如：热点，网民话题）|
|read_status||||读取状态（0 没读， 1读取）|

---
### 手机APP视听节目监测系统  VAApp_ ###

app信息表 `VAApp_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id||||app id|
|name||||标题|
|summary||||简介|
|update_info||||更新信息|
|author||||作者|
|url||||原文url|
|app_url||||app下载的url|
|image_url||||图片url（多个url逗号分割）|
|classify||||分类|
|size||||大小|
|tag||||版本|
|platform||||平台（ios / android）|
|download_count||||下载次数|
|release_time||||发布时间|
|record_time||||记录时间|
|read_status||||读取状态（0 没读， 1读取）|

urls表 `VAApp_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

敏感信息表 `VAApp_sensitive_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|sensitive_id||||敏感事件id|
|sensitive_name||||敏感事件名|
|keywords||||关键字 （逗号分割）|

内容信息表 `VAApp_content_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|content||||内容|
|author||||作者|
|url||||原文url|
|video_url||||视频url|
|image_url||||图片url（多个url逗号分割）|
|origin||||来源|
|watched_count||||观看数|
|comment_count||||评论数|
|share_count||||分享数|
|praise_count||||点赞数|
|release_time||||发布时间|
|record_time||||记录时间|
|site_id||||网站id|
|sensitive_id|varchar|||敏感信息id（多个敏感信息id用逗号分割）|
|read_status||||读取状态（0 没读， 1读取）|

---
### 互联网音视听节目监测系统 VA_ ###

网站表 `VA_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id|||| 网站id |
|name|||| 网站名|
|domain||||域名|
|url||||网址|
|ip||||服务器ip|
|address||||服务器地址|
|video_license||||网络视听许可证|
|public_safety||||公安备案号|
|icp||||ICP号|
|read_status||||读取状态|
|record_time||||记录时间|

urls表 `VA_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

敏感信息表 `VA_sensitive_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|sensitive_id||||敏感事件id|
|sensitive_name||||敏感事件名|
|keywords||||关键字 （逗号分割）|

内容信息表 `VA_content_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|content||||内容|
|author||||作者|
|url||||原文url|
|video_url||||视频url|
|image_url||||图片url（多个url逗号分割）|
|origin||||来源|
|watched_count||||观看数|
|comment_count||||评论数|
|share_count||||分享数|
|praise_count||||点赞数|
|release_time||||发布时间|
|record_time||||记录时间|
|site_id||||网站id|
|sensitive_id|varchar|||敏感信息id（多个敏感信息id用逗号分割）|
|read_status||||读取状态（0 没读， 1读取）|

---

### 直播平台APP监测系统 LiveApp_ ###

app信息表 `LiveApp_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id||||app id|
|name||||标题|
|summary||||简介|
|update_info||||更新信息|
|author||||作者|
|url||||原文url|
|app_url||||app下载的url|
|image_url||||图片url（多个url逗号分割）|
|classify||||分类|
|size||||大小|
|tag||||版本|
|platform||||平台（ios / android）|
|download_count||||下载次数|
|release_time||||发布时间|
|record_time||||记录时间|
|read_status||||读取状态（0 没读， 1读取）|

urls表 `LiveApp_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

主播信息表 `LiveApp_anchor_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|name||||主播名|
|image_url||||贴图|
|sex||||性别|
|age||||年龄|
|address||||地区|
|fans_count||||粉丝数|
|watched_count||||观众数 |
|room_id||||房间号|
|room_url||||房间连接|
|video_path||||直播视频流路径|
|record_time||||记录时间|
|site_id||||网站id|
|live_view||||直播状态（是否在直播 0 未直播 1 直播中）|
|read_status||||读取状态（0 没读， 1读取）|

---
### 网络出版物监测系统 WP_ ###

网站表 `WP_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id|||| 网站id |
|name|||| 网站名|
|domain||||域名|
|url||||网址|
|ip||||服务器ip|
|address||||服务器地址|
|video_license||||网络视听许可证|
|public_safety||||公安备案号|
|icp||||ICP号|
|read_status||||读取状态|
|record_time||||记录时间|

urls表 `WP_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

敏感信息表 `WP_sensitive_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|sensitive_id||||敏感事件id|
|sensitive_name||||敏感事件名|
|keywords||||关键字 （逗号分割）|

内容信息表 `WP_content_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|url|||原文url|
|article_type||||作品类型|
|episodes||||集数|
|score||||评分|
|subscribe_count||||订阅数|
|author||||作者|
|release_time||||发布时间|
|update_time||||更新时间|
|image_url||||图片url（多个url逗号分割）|
|watched_count||||观看数|
|comment_count||||评论数|
|charge_type||||收费类型|
|is_finished||||是否完结|
|origin||||来源|
|abstract||||简介|
|content||||内容|
|record_time||||记录时间|
|site_id||||网站id|
|sensitive_id|varchar|||敏感信息id（多个敏感信息id用逗号分割）|
|read_status||||读取状态（0 没读， 1读取）|

分集信息表 `WP_content_episode_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|content_id|||||content_id|
|video_url||||视频url|
|image_url||||图片url|
|watched_count||||观看数|
|comment_count||||评论数|
|release_time||||发布时间|
|record_time||||记录时间|
|read_status||||读取状态（0 没读， 1读取）|


---
### 游戏APP监测系统 GameApp_ ###

网站表 `GameApp_site_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|site_id|||| 网站id |
|name|||| 网站名|
|domain||||域名|
|url||||网址|
|ip||||服务器ip|
|address||||服务器地址|
|video_license||||网络视听许可证|
|public_safety||||公安备案号|
|icp||||ICP号|
|read_status||||读取状态|
|record_time||||记录时间|

urls表 `GameApp_urls`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|url||||网址|
|depth|int|||层级|
|status|int|||状态（0 todo, 1 doing, 2 done, 3 exception）|
|remark||||url备注|
|site_id||||网站id|

敏感信息表 `GameApp_sensitive_info`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|sensitive_id||||敏感事件id|
|sensitive_name||||敏感事件名|
|keywords||||关键字 （逗号分割）|

字典表 `GameApp_classify`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|_id||||id|
|classify||||分类|

内容信息表 `GameApp_content_info`(应用宝、安卓市场、百度手机助手、360手机助手)

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|title||||标题|
|summary||||简介|
|update_info||||更新信息|
|socre||||评分|
|author||||作者|
|url||||原文url|
|app_url||||app下载的url|
|image_url||||图片url（多个url逗号分割）|
|classify_id||||分类|
|software_size||||大小|
|tag||||版本|
|platform||||平台（ios / android）|
|download_count||||下载次数|
|release_time||||发布时间|
|record_time||||记录时间|
|site_id||||网站id|
|sensitive_id|varchar|||敏感信息id（多个敏感信息id用逗号分割）|
|read_status||||读取状态（0 没读， 1读取）|


---
### 视频特征库 FeaVideo_ ###

特定网站的特征表 `FeaVideo_site`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|domain||||域名|
|video_fea||||有视频的特征|

正负极特征表 `FeaVideo_judge`
>只判断标题和内容是否符合

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|video_fea||||有视频的特征|
|not_video_fea||||没有视频的特征|

通用的特征表 `FeaVideo_common`
>根据html源代码中是否符合特征来判断

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|video_fea||||有视频的特征|