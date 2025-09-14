import cloudscraper, json, os

# 环境变量配置
url = os.environ.get('URL')
config = os.environ.get('CONFIG')
SCKEY = os.environ.get('SCKEY')

login_url = f'{url}/auth/login'
check_url = f'{url}/user/checkin'

def sign(order, user, pwd):
    scraper = cloudscraper.create_scraper()
    headers = {
        'origin': url,
        'user-agent': scraper.headers['User-Agent']
    }
    data = {
        'email': user,
        'passwd': pwd,
        'code': ''
    }

    try:
        print(f'===账号{order}进行登录...===')
        print(f'账号：{user}')
        res = scraper.post(login_url, headers=headers, data=data).text

        # 判断是否被 Cloudflare 拦截
        if '<title>Just a moment...</title>' in res:
            raise Exception('Cloudflare 拦截，登录失败')

        response = json.loads(res)
        print(response['msg'])

        # 进行签到
        res2 = scraper.post(check_url, headers=headers).text
        result = json.loads(res2)
        print(result['msg'])
        content = result['msg']

        # 推送结果
        if SCKEY:
            push_url = f'https://sctapi.ftqq.com/{SCKEY}.send?title=机场签到&desp={content}'
            cloudscraper.create_scraper().post(push_url)
            print('推送成功')

    except Exception as ex:
        content = '签到失败'
        print(content)
        print(f'出现如下异常: {ex}')
        if SCKEY:
            push_url = f'https://sctapi.ftqq.com/{SCKEY}.send?title=机场签到&desp={content}'
            cloudscraper.create_scraper().post(push_url)
            print('推送成功')

    print(f'===账号{order}签到结束===\n')

if __name__ == '__main__':
    configs = config.splitlines()
    if len(configs) % 2 != 0 or len(configs) == 0:
        print('配置文件格式错误')
        exit()

    for i in range(len(configs) // 2):
        user = configs[i * 2]
        pwd = configs[i * 2 + 1]
        sign(i, user, pwd)
