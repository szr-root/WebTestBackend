from webtestengine.keywords.runner import Runner

# 执行环境数据
env_config = {
    "is_debug": False,
    "browser_type": "chromium",
    "host": "https://www.ketangpai.com",
    "global_variable": {
        "username": "3247119728@qq.com",
        "password": "a546245426"
    }
}
# 测试套件数据
suite = {
    'id': "编号",
    'name': "登录功能测试",
    # 测试套件的公共前置操作
    'setup_step': [
        {
            "desc": "打开浏览器",
            "keywords": "打开浏览器",
            "params": {
                "browser_type": "chromium"
            }
        },
        {
            "desc": "打开网页",
            "keywords": "访问网站URL",
            "params": {
                'url': "/#/login"
            }
        },
        {
            "desc": "等待2秒",
            "keywords": "强制等待时间",
            "params": {
                "timeout": 2000
            }
        },
    ],
    # 用例
    "cases": [
        {
            'id': "编号1",
            'name': "登录成功",
            "skip": False,
            "steps": [
                {
                    "desc": "等待1秒",
                    "keywords": "强制等待时间",
                    "params": {
                        "timeout": 1000
                    }
                },
                {
                    "desc": "输入账号",
                    "keywords": "输入内容",
                    "params": {
                        'locator': '//input[@placeholder="请输入邮箱/手机号/账号"]',
                        'value': "${{username}}"
                    }
                },
                {
                    "desc": "等待1秒",
                    "keywords": "强制等待时间",
                    "params": {
                        "timeout": 1000
                    }
                },
                {
                    "desc": "输入密码",
                    "keywords": "输入内容",
                    "params": {
                        'locator': '//input[@placeholder="请输入密码"]',
                        'value': "${{password}}"
                    }
                },
                {
                    "desc": "点击登录",
                    "keywords": "点击元素",
                    "params": {
                        "locator": '//div[@class="margin-top"]/button'
                    }
                },
                {
                    "desc": "断言是否跳转登录成功后的页面",
                    "keywords": "断言页面url地址",
                    "params": {
                        "expect_results": "https://www.ketangpai.com/#/bindwechat"
                    }
                }

            ]
        }
    ]
}

if __name__ == '__main__':
    runner = Runner(env_config, suite)
    runner.run()
