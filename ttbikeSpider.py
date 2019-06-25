import requests,json,os,sys,time,datetime,random
#import base64
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import numpy as np
from codePlatform import codePlatform as CP
                
class ttbikeSpider(CP):
    _session=requests.session()
    _captcha_status=False #是否成功获取图片验证码
    _SMS_status=False #是否成功获取短信验证码
    _login_status=False #是否成功登录
    _headers={"Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "br, gzip, deflate",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Length": "131",
        "Content-Type": "text/plain;charset=UTF-8",
        "Host": "api.ttbike.com.cn",
        "Origin": "http://m.ttbike.com.cn",
        "Referer": "http://m.ttbike.com.cn/ebike-h5/latest/index.html",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 MQQBrowser/8.8.2 Mobile/16A5345f Safari/604.1 MttCustomUA/2 QBWebViewType/1 WKType/1"
        }
    def __init__(self,token,path=os.getcwd(),city="南京市",cityCode="025",adCode="320100",nums=20,timeout=6):
        CP.__init__(self,path=path,token=token)
        self.path=path
        self.city=city
        self.cityCode=cityCode
        self.adCode=adCode
        self.nums=nums
        self.timeout=timeout


    def _getCaptcha(self,phone):
        get_captcha_url="https://api.ttbike.com.cn/auth?user.account.sendCodeV2"
        get_captcha_data={"version":"4.2.3","from":"h5",
            "systemCode":63,"platform":6,
            "action":"user.account.sendCodeV2",
            "mobile":phone,
            "capText":""
            }
        r=self._session.post(get_captcha_url,headers=self._headers,data=json.dumps(get_captcha_data),timeout=self.timeout)
        if "imageCaptcha" in r.text:#获取短信验证码前需要验证图片验证码，如果response包含验证码字段，则正确，否则异常
            img=json.loads(r.text)["data"]["imageCaptcha"]
            captcha_path=os.path.join(self.path,"captcha.png")
            with open(captcha_path,'wb') as tempout:
                tempout.write(base64.decodebytes(bytes(img[22:],"utf-8")))#将base64图片验证码解码保存
            self._captcha_status=True
        else:
            print('图片验证码获取失败, 原因:',r.text)

    def _sendSMSCode2(self,phone):
        if self._captcha_status:#如果已经获取过验证码
            get_SMSCode_url="https://api.ttbike.com.cn/auth?user.account.sendCodeV2"
            get_SMSCode_data={"version":"4.2.3","from":"h5",
                "systemCode":63,"platform":6,
                "action":"user.account.sendCodeV2",
                "mobile":phone,
                "capText":""
                }
            captcha_path=os.path.join(self.path,"captcha.png")
            captcha = mpimg.imread(captcha_path) # 使用mpimg读取验证码
            plt.imshow(captcha) # 在Ipython或JupyterNoetebook显示图片，便于人工输入；如无显示，请手动打开captcha.png进行输入
            plt.axis('off')
            plt.show()
            fail_count=0
            while fail_count<5:
                code=input('请输入图片验证码:')
                get_SMSCode_data["capText"]=code
                r=self._session.post(get_SMSCode_url,headers=self._headers,data=json.dumps(get_SMSCode_data),timeout=self.timeout)
                if 'true' in r.text:
                    self._SMS_status=True
                    return
                else:
                    fail_count+=1
                    print('第%s次获取短信验证码失败，原因:'%fail_count,r.text)
            print('获取短信验证码失败次数达5次，终止程序')
        else:
            raise Exception('请先获取图片验证码')

    def _sendSMSCode(self,phone):
        get_SMSCode_url="https://api.ttbike.com.cn/auth?user.account.sendCodeV2"
        get_SMSCode_data={"version":"4.2.3","from":"h5",
            "systemCode":63,"platform":6,
            "action":"user.account.sendCodeV2",
            "mobile":phone,
            "capText":""
            }
        r=self._session.post(get_SMSCode_url,headers=self._headers,data=json.dumps(get_SMSCode_data),timeout=self.timeout)
        if 'true' in r.text:
            self._SMS_status=True
            print('发送验证码短信成功，请查收')
            return
        else:
            print('短信发送失败，原因：',r.text)

    def _getToken(self,phone,SMSCode):
        if self._SMS_status:
            login_url='https://api.ttbike.com.cn/auth?user.account.login'
            login_data={"version":"4.2.3",
                "from":"h5",
                "systemCode":63,
                "platform":1,
                "action":"user.account.login",
                "mobile":phone,
                "code":SMSCode,
                "picCode":{"cityCode":self.cityCode,
                    "city":self.city,
                    "adCode":self.adCode
                    }
                }
            r=self._session.post(login_url,headers=self._headers,data=json.dumps(login_data),timeout=self.timeout)
            if "token" in r.text:
                token=json.loads(r.text)["data"]["token"]
                self._login_status=True
                return [0,token]
            else:
                return [-1,r.text]
        else:
            raise Exception('请先获取短信验证码')
 
    def _getBikes(self,lng,lat,token):
        '''
        功能：获取某一经纬度周边500米的所有单车信息
        1.传入经纬度和token值
        2.如果顺利，返回经纬度周围500米的所有单车信息，否则显示异常信息
        '''
        get_bike_url='https://api.ttbike.com.cn/api?user.ride.nearBikes'
        get_bike_data={"version":"4.2.3",
            "from":"h5",
            "systemCode":63,
            "platform":1,
            "action":"user.ride.nearBikes",
            "lat":lat,
            "lng":lng,
            "cityCode":self.cityCode,
            "currentLng":lng,
            "currentLat":lat,
            "adCode":self.adCode,
            "token":token
            }
        r=requests.post(get_bike_url,headers=self._headers,data=json.dumps(get_bike_data),timeout=20)#此处超时最好设置大一点
        if 'bikeNo' in r.text:
            return json.loads(r.text)["data"]
        else:
            print("\n获取单车信息失败，原因：",r.text)
            return None

    def _writeFile(self,all_bikes,time_stamp):#默认使用csv存储
        duplicated_bikes=[]
        for bike in all_bikes:
            if bike not in duplicated_bikes:
                duplicated_bikes.append(bike)
        all_bikes_path=os.path.join(self.path,"all_bikes.csv")
        with open(all_bikes_path,'a+') as f:
            for bike in duplicated_bikes:
                items=[time_stamp]+list(dict(bike).values())
                items=[str(i) for i in items]
                f.write((','.join(items)))
                f.write('\n')
            print('\n%s时刻信息写入成功'%time_stamp)
    
    def _getNewToken(self):
        self._SMS_status=False #是否成功获取短信验证码
        self._login_status=False #是否成功登录
        phone=self._getPhone()
        self._sendSMSCode(phone)
        SMS_info=self._autogetSMSCode(phone)
        if SMS_info[0]==0:
            SMSCode=SMS_info[1]
            token_info=self._getToken(phone,SMSCode)
            if token_info[0]==0:
                print("获取token成功：",token_info[1])
                return token_info[1]
                
    def createTokenPool(self):
        token_pool_path=os.path.join(self.path,'token_pool.txt')
        if os.path.exists(token_pool_path):
            mode='r'
        else:
            mode='w+'
        with open(token_pool_path,mode,encoding="utf-8") as f:
            token_list=list(set([i[:-1] for i in f.readlines()]))
        count_tokens=len(token_list)
        while count_tokens<self.nums:
            print('----------------------------------')
            print('当前token池数量%s'%count_tokens)
            token=self._getNewToken()
            if token:
                self._addToken(token)
                count_tokens+=1
        print('----------------------------------')
        print('token池预设值:%s，当前值:%s'%(self.nums,count_tokens))

    def run(self,lng1,lat1,lng2,lat2):
        self.createTokenPool()
        token_pool_path=os.path.join(self.path,'token_pool.txt')
        with open(token_pool_path,'r',encoding="utf-8") as f:
            token_list=list(set([i[:-1] for i in f.readlines()]))
        while (True):
            try:
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")#当前时间戳
                nexttime=(datetime.datetime.now()+datetime.timedelta(minutes=1))#下次抓取开始时间（一分钟抓一次）
                print(timestamp)
                all_bikes=[]
                lng_list=np.arange(lng1,lng2,0.004)#经纬度0.004约为400米
                lat_list=np.arange(lat1,lat2,0.004)
                print('一共',len(lng_list)*len(lat_list),'个点')
                count_points=0
                for lng in lng_list:
                    for lat in lat_list:
                        try:
                            token=token_list[count_points%len(token_list)]
                            print('Token %s正在加载第%s个点:%s---%s'%(token,count_points,lng,lat),end='\r')
                            bikes=self._getBikes(lng,lat,token)
                            all_bikes= all_bikes+bikes
                            count_points+=1
                            time.sleep(1)
                        except TypeError:
                            print('第%s个点出错，删除过期token'%count_points)
                            token_list.remove(token)
                            self._delToken(token)#从token池文件中删除
                            token=token[random.randint(0,len(token_list))]
                            bikes=self._getBikes(lng,lat,token)
                            all_bikes= all_bikes+bikes
                self._writeFile(all_bikes,timestamp)
                self.createTokenPool()#检查token池数量，如果低于预设值，则自动更新
                resttime=(nexttime-datetime.datetime.now()).seconds#休眠时间=2分钟-本次抓取所用时间
                if resttime>0:
                    print('休息%s秒后继续抓取...'%resttime)
                    time.sleep(resttime)
            except KeyboardInterrupt:
                break 
                      
    def test(self):
        phone=input('请输入手机号：')
        #self._getCaptcha(phone)
        self._sendSMSCode(phone)
        SMSCode=input('请输入短信验证码')
        token_info=self._getToken(phone,SMSCode)
        if token_info[0]==0:
            token=token_info[1]
            points=input('请输入经纬度,例如118.9579540000,32.1198180000:')
            bikes=self._getBikes(points.split(',')[0],points.split(',')[1],token)
            if bikes:
                return bikes
            else:
                print("出错了")
      