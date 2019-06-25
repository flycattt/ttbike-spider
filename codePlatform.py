import time,requests,os

class codePlatform():
    def __init__(self,path,token):
        self.path=path
        self.token=token
    
    def _getPhone(self):
        '''
        功能：利用某接码平台，获取手机号
        1.利用某接码平台的API，获取手机号用于哈啰单车登陆，其中token为接码平台用户token
        2.如果顺利，返回获取的手机号，否则显示异常信息
        '''
        get_phone_url="http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token=%s&itemid=25342"%self.token
        r=requests.get(get_phone_url)  
        if "success" in r.text:
            phone=r.text.split('|')[-1]
            print("获取手机号成功:",phone)
            return phone
        else:
            raise Exception('获手机号取失败：',r.text)
    
    def _autogetSMSCode(self,phone):
        '''
        功能：获取指定手机号收到的短信
        1.获取某手机号接收到的短信
        2.如果顺利，提取短信中的验证码并返回，否则显示异常信息
        '''
        code=""
        fail_count=0
        get_SMS_url="http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token=%s&itemid=25342&release=1&mobile=%s"%(self.token,phone)
        while code=="":
            r=requests.get(get_SMS_url)
            r.encoding=r.apparent_encoding
            if "success" in r.text:
                code=r.text.split(':')[-1].split(',')[0].strip()
                print("获取验证码成功：",code)
                return [0,code]
            elif fail_count<12:
                fail_count+=1
                print('%s尝试第%s次获取验证码...'%(phone,fail_count))
                time.sleep(5)
            else:
                print('%s获取短信验证码失败，原因%s'%(phone,r.text))
                return [-1,r.text]
    
    def _addToken(self,token):
        token_pool_path=os.path.join(self.path,'token_pool.txt')
        with open(token_pool_path,'a+',encoding="utf-8") as f:
            f.write(token+'\n')
            
    def _delToken(self,token):
        token_pool_path=os.path.join(self.path,'token_pool.txt')
        with open(token_pool_path,'r',encoding="utf-8") as f:
            token_list=list(set([i[:-1] for i in f.readlines()]))
        if token in token_list:
            token_list.remove(token)
            with open(token_pool_path,'w',encoding="utf-8") as f:
                f.write('\n'.join(token_list)) 