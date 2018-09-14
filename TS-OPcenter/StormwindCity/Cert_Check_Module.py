import requests, json, time, socket, ssl
import dateutil.parser

class Base_Response(object):
    """
    证书检测类的基类
    """
    def __init__(self,domain):
        self.domain = domain
        self.verifyState = None
        self.verifyInfo = None
        self.server_ip = None
        self.sans = []
        self.matchDomain = None
        self.valid_from = None
        self.valid_to = None
        self.valid_days = None
        self.hash = None
        self.issuer = None
        self.signature_algorithm = None
        self.publickey_algorithm = None
        self.chain_info = []

    def verify(self,valid_to_timestamp):
        # 证书状态：0=有效，1=证书链不完整，2=已过期，3=域名和证书不匹配,4=其他错误
        if len(self.chain_info) >= 3 and valid_to_timestamp > time.time() and self.matchDomain:
            self.verifyState = 0
            self.verifyInfo = '有效：证书状态可信'
        elif valid_to_timestamp <= time.time():
            self.verifyState = 1
            self.verifyInfo = '无效：证书已经过期'
        elif self.matchDomain is False:
            self.verifyState = 2
            self.verifyInfo = '无效：与域名不匹配'
        elif len(self.chain_info) <= 2:
            self.verifyState = 3
            self.verifyInfo = '无效：证书链不完整'

    def ret_response(self):
        """
        返回证书所有信息
        :return:
        """
        return self.__dict__

    def ret_valid(self):
        """
        返回证书有效期的信息
        :return:
        """
        cert_valid = {
            'verifyState':self.verifyState,
            'cert_valid_days':self.valid_days,
            'cert_valid_date':self.valid_to,
                }
        return cert_valid





class PySSL_Check(Base_Response):
    """
    本地OpenSSL工具检测证书的类
    """
    def requests(self):
        """
        通过openssl发送socket请求获取证书信息
        :return:
        """
        try:
            AddressFamily = socket.getaddrinfo(self.domain, 'https')
            self.server_ip = AddressFamily[0][4][0]
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(socket.socket(), server_hostname=self.domain)
            s.settimeout(10)
            s.connect((self.domain, 443))
            cert = s.getpeercert()
            response = {'code':0,'cert':cert,'domain':self.domain}
        except Exception as error:
            response = {'code': 4, 'error': str(error), 'domain': self.domain}
        self.parse(response)

    def parse(self,response):
        """
        解析结果
        :param response:
        :return:
        """
        if response.get('code') == 0:
            # 有效期开始
            notBefore = time.mktime(time.strptime(response['cert']['notBefore'], '%b %d %H:%M:%S %Y %Z'))
            # 有效期结束
            notAfter = time.mktime(time.strptime(response['cert']['notAfter'], '%b %d %H:%M:%S %Y %Z'))
            # 当前时间
            nowDate = time.time()
            # 时间差
            self.valid_days = int((notAfter - nowDate) / 3600 / 24)
            # 时间格式本地化
            self.valid_from = time.strftime("%Y-%m-%d", time.localtime(notBefore))
            self.valid_to = time.strftime("%Y-%m-%d", time.localtime(notAfter))
            # 颁发机构
            self.issuer = response['cert']['issuer'][-1][-1][-1]
            # 证书备用名
            for san in response['cert']['subjectAltName']:
                self.sans.append(san[1])
            self.verifyState = 0
        else:
            #证书状态：0 = 有效，1 = 证书链不完整，2 = 已过期，3 = 域名和证书不匹配, 4 = 其他错误
            self.verifyState = 4
            self.verifyInfo = response['error']



class Myssl_Check(Base_Response):
    """
    通过https://myssl.com/ssl.html(myssl)网站检测
    """
    def requests(self):
        """
        向myssl发送检测请求
        :return:
        """
        url = 'https://myssl.com/api/v1/ssl_status?domain=' + self.domain + '&port=443&c=0'
        try:
            response = requests.get(url,timeout=30)
            response = json.loads(response.text)
        except Exception as e:
            response = {'code':4,'error':str(e),'domain':self.domain}
        self.parse(response)

    def parse(self,response):
        """
        解析请求结果
        :param response:
        :return:
        """
        if response['code'] == 0:
            try:
                certs_info = response['data']['status']['certs']['rsas'][0]
            except IndexError:
                certs_info = response['data']['status']['certs']['eccs'][0]
            leaf_cert_info = certs_info['leaf_cert_info']
            full_chain_info = certs_info['chain']['certs']
            # 服务器IP
            self.server_ip = response['data']['check_host']
            # 证书链
            for chain in full_chain_info:
                if not chain['missing']:
                    self.chain_info.append(chain['common_name'])
            # 证书信息
            self.sans = leaf_cert_info.get('sans')
            self.matchDomain = True if leaf_cert_info.get('cert_status') == 0 else False
            self.valid_from = leaf_cert_info.get('valid_from')[:10]
            self.valid_to = leaf_cert_info.get('valid_to')[:10]
            valid_to = dateutil.parser.parse(leaf_cert_info.get('valid_to')).date()
            valid_to_timestamp = time.mktime(time.strptime(str(valid_to), "%Y-%m-%d"))
            self.valid_days = int((valid_to_timestamp - time.time()) / 24 / 3600)
            self.hash = leaf_cert_info.get('hash')
            self.issuer = leaf_cert_info.get('issuer')
            self.signature_algorithm = leaf_cert_info.get('signature_algorithm')
            self.publickey_algorithm = leaf_cert_info.get('publickey_algorithm')
            self.verify(valid_to_timestamp)
        else:
            #证书状态：0 = 有效，1 = 证书链不完整，2 = 已过期，3 = 域名和证书不匹配, 4 = 其他错误
            self.domain = response.get('domain')
            self.matchDomain = False
            self.verifyState = 4
            self.verifyInfo = response.get('error')



class SSLceshi_Check(Base_Response):
    """
    向sslchaoshi.com发送检测请求
    """
    def requests(self):
        url = 'https://api-tools.sslchaoshi.com/ssltools/sslVerity'
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        }
        data = {
                'hostname':self.domain,
                'port': 443,
        }
        try:
            response = requests.post(url=url, data=data, headers=headers,timeout=30)
            response = json.loads(response.text)
            if response.get('info') is None:
                response['code'] = 0
            else:
                response = {'code': 4, 'error': response.get('info'), 'domain': self.domain}
        except Exception as e:
            response = {'code':4,'error':str(e),'domain':self.domain}
        self.parse(response)

    def parse(self,response):
        """
        解析请求结果
        :param response:
        :return:
        """
        if response['code'] == 0:
            leaf_cert_info =  response.get('cerInfo')
            # 服务器IP
            self.server_ip = response.get('ipList')[0]
            # 证书链
            self.chain_info = response.get('cerChainList')
            # 证书信息
            self.sans = leaf_cert_info.get('subjectAltName')
            self.matchDomain = True if leaf_cert_info.get('matchDomain') else False
            valid_from_timestamp = leaf_cert_info.get('activeTimeStamp')['from']
            valid_to_timestamp = leaf_cert_info.get('activeTimeStamp')['to']
            self.valid_from = time.strftime("%Y-%m-%d", time.localtime(valid_from_timestamp))
            self.valid_to = time.strftime("%Y-%m-%d", time.localtime(valid_to_timestamp))
            self.valid_days = int((valid_to_timestamp - time.time()) / 24 / 3600)
            self.hash = leaf_cert_info.get('fingerPrint')
            self.issuer = leaf_cert_info.get('issuer')
            self.signature_algorithm = leaf_cert_info.get('alogrithm')
            self.publickey_algorithm = leaf_cert_info.get('pub_alogrithm')
            self.verify(valid_to_timestamp)
        else:
            #证书状态：0 = 有效，1 = 证书链不完整，2 = 已过期，3 = 域名和证书不匹配, 4 = 其他错误
            self.domain = response.get('domain')
            self.matchDomain = False
            self.verifyState = 4
            self.verifyInfo = response.get('error')







