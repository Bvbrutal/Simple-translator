from urllib import request, parse
import ssl
import random

# 常用User-Agent列表
ua_list = [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
]


# 加载一个页面
def loadPage(url, word):
    # 在ua_list列表中随机选择一个UserAgent
    userAgent = random.choice(ua_list)
    headers = {
        'User-Agent': userAgent
    }
    # 发起一个请求
    req = request.Request(url, headers=headers)
    # 创建未经过验证的上下文的代码
    context = ssl._create_unverified_context()
    data = {
        'i': word,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': '16002154063071',
        'sign': '37d97277cb051e71959e772b91309b2b',
        'lts': '1600215406307',
        'bv': '7e14dfdb6b3686cc5af5e5294aaded19',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTlME'
    }
    data = parse.urlencode(data).encode('utf-8')
    # 打开响应的对象
    response = request.urlopen(req, context=context, data=data)
    # 获取响应的内容
    html = response.read()
    # 对获取到的unicode编码进行解码
    content = html.decode('utf-8')

    return content


import json


def fanyi(word):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
    content = loadPage(url, word)
    jsondicts = json.loads(content)
    return jsondicts['translateResult'][0][0]['tgt']


if __name__ == '__main__':
    word = input('请输入要翻译的单词：')
    result = fanyi(word)
    print('翻译的结果为：', result)