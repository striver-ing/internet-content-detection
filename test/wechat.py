from pprint import pprint

from wechatsogou import *
wechats = WechatSogouApi()

# name = '南京航空航天大学'
# wechat_infos = wechats.search_gzh_info(name)

# pprint(wechat_infos)

url = 'https://mp.weixin.qq.com/profile?src=3&timestamp=1500880280&ver=1&signature=79RSCnH3b55dNreb4AOf1wO3UBnJ2PiaXiw7GKITr*PQKbXEngwWKUoGpT1n*p3FegxxnkteOsS*K3wrsXWssw=='
article_content = wechats.get_gzh_message(url=url)
pprint(article_content)


# url = 'http://mp.weixin.qq.com/s?timestamp=1500606215&src=3&ver=1&signature=5pzvoZMu2myu8anE2PNU8XMsQIhEiQIuGIkLmeg3*2Vu92aD7okwwBv6CmdYaPkcKPcY1N4PvXvLNX9vrCaV1CBUNsyvJOW*loRcBSqT3DUwNiSrLFRaeRhk4n6sDEoXAXVMrSd-V4XXbUVYUwt*1Mmu2Ma*hzGTMfn*3m8gVyo='
# article_comment = wechats.deal_article_comment(url=url)
# print(article_comment)

# article_info = wechats.deal_article('http://mp.weixin.qq.com/profile?src=3&timestamp=1500605105&ver=1&signature=S-7U131D3eQERC8yJGVAg2edySXn*qGVi5uE8QyQU034di*2mS6vGJVnQBRB0It9oL02Iz880E40*WsqJBAE7A==')
# print(article_info)