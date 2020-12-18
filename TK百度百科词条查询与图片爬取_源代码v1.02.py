import requests
from urllib import parse
import re
import bs4
import os
import time
import tkinter as tk
import tkinter.messagebox as mes
import tkinter.filedialog as tkfd
import json
import time


#若访问失败，返回None
def get_response(url,headers=None):
    count=1
    while True:
        if count >10:
            res=None
            break
        try:
            res=requests.get(url,headers=headers)
            if res.status_code == 200:
                break
        except:
            pass
        finally:
            count+=1
    return res

class Window:

    def __init__(self):
        self.headers={
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 QIHU 360SE'
            }   
        self.working=False
        
        self.root=tk.Tk()
        self.root.title('百度百科词条查询与图片抓取')
        self.root.geometry('960x640')
        self.root.resizable(1,1)


        #设置各种frame
        self.framehigh=tk.LabelFrame(self.root,text='详细内容',labelanchor=tk.NW)
        self.framehigh.place(relx=0,rely=0,relwidth=1,relheight=0.7)
        self.framelow=tk.LabelFrame(self.root,text='词条查询',labelanchor=tk.NW)
        self.framelow.place(relx=0,rely=0.7,relwidth=1,relheight=0.1)
        self.framedown=tk.LabelFrame(self.root,text='图片获取',labelanchor=tk.NW)
        self.framedown.place(relx=0,rely=0.8,relwidth=1,relheight=0.2)

        self.framelowleft=tk.Frame(self.framelow)
        self.framelowleft.place(relx=0,rely=0,relwidth=0.85,relheight=1)
        self.framelowright=tk.Frame(self.framelow)
        self.framelowright.place(relx=0.85,rely=0,relwidth=0.15,relheight=1)

        self.framedownleft=tk.Frame(self.framedown)
        self.framedownleft.place(relx=0,rely=0,relwidth=0.85,relheight=1)
        self.framedownright=tk.Frame(self.framedown)
        self.framedownright.place(relx=0.85,rely=0,relwidth=0.15,relheight=1)

        #规划显示信息区
        self.maintext=tk.Text(self.framehigh,state='disabled')
        self.maintext.place(relx=0,rely=0,relwidth=0.98,relheight=1)
        self.scrbar=tk.Scrollbar(self.framehigh)
        self.scrbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.maintext.config(yscrollcommand=self.scrbar.set)
        self.scrbar.config(command=self.maintext.yview)

        #规划词条查询区
        self.tofindname=tk.StringVar()
        self.tofindname.set('')
        self.entry=tk.Entry(self.framelowleft,textvariable=self.tofindname)
        self.entry.place(relx=0.3,rely=0.2,relwidth=0.7)
        self.label=tk.Label(self.framelowleft,text='请输入您想查询的词条:',anchor=tk.E,font=('楷书',11))
        self.label.place(relx=0,rely=0.2,relwidth=0.3)

        #规划图片获取区
        self.imgname=tk.StringVar()
        self.imgname.set('')
        self.imgnumber=tk.IntVar()
        self.imgnumber.set(0)
        self.imgpath=tk.StringVar()
        self.imgpath.set('')

        self.imgentry=tk.Entry(self.framedownleft,textvariable=self.imgname)
        self.imgentry.place(relx=0.3,rely=0.1,relwidth=0.7)
        self.imglabel=tk.Label(self.framedownleft,text='请输入您想获取的图片名:',anchor=tk.E,font=('楷书',11))
        self.imglabel.place(relx=0,rely=0.1,relwidth=0.3)

        self.imgnumentry=tk.Entry(self.framedownleft,textvariable=self.imgnumber)
        self.imgnumentry.place(relx=0.15,rely=0.5,relwidth=0.05)
        self.imgnumlabel1=tk.Label(self.framedownleft,text='您想获取',anchor=tk.E,font=('楷书',11))
        self.imgnumlabel1.place(relx=0,rely=0.5,relwidth=0.15)
        self.imgnumlabel2=tk.Label(self.framedownleft,text='包(约30张)',anchor=tk.W,font=('楷书',11))
        self.imgnumlabel2.place(relx=0.2,rely=0.5,relwidth=0.15)

        self.pathentry=tk.Entry(self.framedownleft,textvariable=self.imgpath)
        self.pathentry.place(relx=0.55,rely=0.5,relwidth=0.45)
        self.pathlabel=tk.Label(self.framedownleft,text='图片保存路径:',anchor=tk.E,font=('楷书',11))
        self.pathlabel.place(relx=0.35,rely=0.5,relwidth=0.2)
        
        #更新信息显示区的内容
        def textupdate(pos,string):
            self.maintext.config(state='normal')
            self.maintext.insert(pos,string)
            self.maintext.update()
            self.maintext.config(state='disabled')
            self.maintext.yview_moveto(1)
        
        def textclear():
            self.maintext.config(state='normal')
            self.maintext.delete(1.0,tk.END)
            self.maintext.config(state='disabled')

        #图片爬取 具体操作函数
        def _getimage(event=None):
            baseurl='https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592\
&is=&fp=result&queryWord={name}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=\
-1&z=&ic=&hd=&latest=&copyright=&word={name}&s=&se=&tab=&width=&height=&f\
ace=0&istype=2&qc=&nc=1&fr=&expermode=&force=&pn={page}&rn=30&gsm=78&1587955897298='

            #路径必须是绝对路径,最后会对路径作出改动以'\'结尾
            def getpath():
                path=self.imgpath.get()
                if not os.path.isabs(path):
                    textupdate(tk.END,'请输入正确的绝对路径\n')
                    return None
                if not os.path.exists(path):
                    textupdate(tk.END,'未找到该目录，准备创建...\n')
                    try:
                        os.makedirs(path)
                        textupdate(tk.END,'新目录创建成功\n')
                    except FileNotFoundError:
                        textupdate(tk.END,'请检查在你的电脑上此路径是否正确\n')
                        path=None
                    except:
                        textupdate(tk.END,'路径错误\n')
                        path=None
                if path!=None and path[-1]!='/':
                    path+='/'  #使路径以/结尾
                return path
            
            #获取所爬包数
            def getpacknum():
                try:
                    num=self.imgnumber.get()
                except:
                    textupdate(tk.END,'请正确输入获取数量(单位为包，多数情况下一包有29张)\n')
                    return None
                if num<=0:
                    textupdate(tk.END,'请正确输入获取数量(单位为包，多数情况下一包有29张)\n')
                    num=None
                return num

            #合成图片所在的url
            def parse_midurl(name):
                #填补baseurl的{name}区域
                name=parse.quote(name)
                midurl=baseurl.format(name=name,page='{page}')
                return midurl
            def parseurl_page(midurl,page):
                #填补baseurl的{page}区域
                return midurl.format(page=page)

            #生成一系列图片的名字前缀
            def parse_name(name):
                
                nowtime=time.localtime()
                for i in range(6):
                    name+=str(nowtime[i])
                return name
                
            #图片爬取 实现
            textclear()
            name=self.imgname.get()
            if name=='':
                textupdate(tk.END,'请输入要获取的图片的名称\n')
            midurl=parse_midurl(name)#获得缺少{page}的url
            packnum=getpacknum()
            path=getpath()
            #判断name,packnum,path的输入是否有误(packnum,path输入错误的提示信息在对应的函数中)
            if packnum==None or path==None or name=='':
                return 
            errpack=[]
            
            packcount=1
            for each in range(0,packnum*30,30):
                textupdate(tk.END,'进行到第【%d】包\n\n'%packcount)
                packurl=parseurl_page(midurl,each)#获得完整的url
                res=get_response(packurl,headers=self.headers)
                if res==None:
                    textupdate(tk.END,'本包访问失败，进行下一包...\n')
                    continue
        #这个范围内有待解决json.loads有时会出错，所以加了try
                try:
                    packdata=json.loads(res.text.replace("\\'","'"))
                except:
                    textupdate(tk.END,'发生错误,由于作者太菜不会处理,跳过一包\n\n\n\n')
                    errpack.append(packcount)
                    packcount+=1
                    continue
        #这个范围内有待解决'''
                if packdata['data'][0]=={}:
                    textupdate(tk.END,'已经没有图片了...\n')
                    break
                piccount=1
                for perpic in packdata['data']:
                    textupdate(tk.END,'正在尝试解析图片...\n')
                    try:
                        picurl=perpic['thumbURL']
                    except:
                        textupdate(tk.END,'空信息,跳过...\n')
                        break
                    picres=get_response(picurl,headers=self.headers)
                    if picres==None:
                        textupdate(tk.END,'访问异常，跳过...\n')
                        continue
                    picimg=picres.content
                    textupdate(tk.END,'正在爬取图片...'+' '+str(each//30+1)+' '+str(piccount)+'\n')
                    with open(path+parse_name(name)+'Pack'+str(each//30)+'No.'+str(piccount)+'.jpg','wb') as f:
                        f.write(picimg)
                    textupdate(tk.END,'爬取完成...\n')
                    piccount+=1
                textupdate(tk.END,'\n\n第【%d】包完成\n'%packcount)
                packcount+=1

            textupdate(tk.END,'爬 取 结 束\n')

            #临时代码
            if len(errpack):
                textupdate(tk.END,'由于载入json文件时发生错误，作者太菜不会处理,以下包数的图片没有抓取\n')
                for i in errpack:
                    textupdate(tk.END,str(i)+' ')
           



        #词条查询 主要操作函数
        def _findmessage(event=None):
            def whenend():
                textupdate(tk.END,'本次查询结束\n')
            
            #name参数是用户输入的词条名称，返回词条对应的百度百科url
            def parse_url(name):
                name=parse.quote(name)
                url='https://baike.baidu.com/item/'+name
                return url

            #整理从百度百科得到的简介内容，如去除去形如“[2]”“[15-17]”的注释以及删除空白、分隔符等，换行保留
            def parse_text(summary):
                tmpstr=''
                string=''
                for i in summary.strings:
                    tmpstr+=i
                tmpstr=re.sub(r'\[\d+\]|\[\d+-\d+\]','',tmpstr)
                tmpstr=tmpstr.replace('\n','THEREISPLACEOFENTERGIAOGIAO')
                for i in tmpstr.split():
                    string+=i
                else:
                    string+='\n\n\n'
                string=string.replace('THEREISPLACEOFENTERGIAOGIAO','\n')
                if string[0] == '\n':
                    string=string.replace('\n','',1).replace('\n\n','\n')
                return string

            #显示该项内容的基本信息
            def print_msg(content,url,soup):
                summary=soup.find('div',class_='lemma-summary')
                textupdate(tk.END,'内容: '+content+'\n')
                textupdate(tk.END,'网址: '+url+'\n')
                textupdate(tk.END,'简介:\n'+'     ')
                string=parse_text(summary)
                if len(string)==string.count('\n'):
                    textupdate(tk.END,'百度百科的简介没写东西，您可以进入网页查看\n')
                textupdate(tk.END,string+'\n')


            #词条查询 实现
            textclear()
            name=self.tofindname.get()
            if name=='':
                textupdate(tk.END,'未输入词条\n')
                return

            url=parse_url(name)#初步得到url
            res=get_response(url,headers=self.headers)

            if res == None:
                textupdate(tk.END,'访问失败\n')
                whenend()
                return 
            if res.url=='https://baike.baidu.com/error.html':#这是百度百科错误页面的url
                textupdate(tk.END,'百度百科没有关于%s的信息，请检查词条是否输入错误\n'%name)
                whenend()
                return 

            html=res.text
            soup=bs4.BeautifulSoup(html,'html.parser')

            if soup.find('li',class_='item')==None:
                #走这一部分一般有两种情况(可能有其他情况未发现)
                #第一种:所查询的词条只有一种解释,详细介绍页面里自然不会提供其他可能性选项，所以找不到对应的<li>标签
                #第二种:并没有访问到详细介绍的页面，而是进入了让用户选链接的页面，查询少量词条时会遇到这种情况
                #若下方if成立为情况一,否则为情况二
                if soup.find('div',class_='lemma-summary'):
                    print_msg(name,res.url,soup)
                else:
                    count=1
                    for each in soup.find_all('div',class_='para'):
                        textupdate(tk.END,'【%d】\n'%count)
                        tmpurl='https://baike.baidu.com'+each.a['href']
                        tmpres=get_response(tmpurl,headers=self.headers)
                        if tmpres == None :
                            textupdate(tk.END,'页面访问失败\n')
                            continue
                        tmpsoup=bs4.BeautifulSoup(tmpres.text,'html.parser')
                        print_msg(each.a.string,tmpurl,tmpsoup)
                        count+=1
                whenend()
                return
            count=1   
            for each in soup.find_all('li',class_='item'):
                textupdate(tk.END,'【%d】\n'%count)
                #each.span所包含的内容对应我们的res得到的页面，走if
                #each.a所包含的内容对应该词条其他的可能性,走else
                if each.span != None:
                    print_msg(each.span.string,res.url,soup)
                else:
                    tmpurl='https://baike.baidu.com'+each.a['href']
                    tmpres=get_response(tmpurl,headers=self.headers)
                    if tmpres == None :
                        textupdate(tk.END,'页面访问失败\n')
                        continue
                    tmpsoup=bs4.BeautifulSoup(tmpres.text,'html.parser')
                    print_msg(each.a.string,tmpurl,tmpsoup)
                count+=1
            whenend()

        #按钮关联函数(包括按钮和菜单)
        def _selectpath(event=None):
            #选择路径函数
            self.imgpath.set(tkfd.askdirectory())

        def _exit():
            #退出窗口
            self.root.quit()

        def _programeinfo():
            #关于程序 本程序信息
            tp=tk.Toplevel()
            tp.title('关于程序')
            label=tk.Label(tp,text='本程序使用python编写,主要供作者学习、练习,\n爬虫程序为最简单的python单线程爬虫',width=60,height=9)
            label.pack()

        def _createrinfo():
            #关于作者 作者信息
            tp=tk.Toplevel()
            tp.title('关于作者')
            label=tk.Label(tp,text='由不愿透露姓名的wldcmzy制作',width=60,height=9)
            label.pack()

        def _answer():
            #答疑按钮关联函数
            tp=tk.Toplevel()
            tp.title('答疑')
            label=tk.Label(tp,text='计算获取图片的包数时会舍去小数点后的部分',width=60,height=9)
            label.pack()
        
        def _update_journal():
            text=''
            #日期以形如2020/5/12的格式，参数为字符串或字符串列表
            def add(version,date,*data):
                nonlocal text
                text+='版本:'+version+'\n更新日期:'+date+'\n更新内容:\n'
                for each in data:
                    text+='· '+each+'\n'
                else:
                    text+='\n\n'
            add('1.0','2020/5/10','从无到有,此程序最初版完成')
            add('1.01','2020/5/12','现在当爬取图片时,若存在多个输入错误,会一次性全部显示,而非显示单个')
            add('1.02','2020/5/16','修正了在一次查询或爬取之后再次进行查询或爬取时内容显示区不会清屏的bug')
            tp=tk.Toplevel()
            tp.geometry('720x360')
            tp.title('更新日志')

            textt=tk.Text(tp)
            textt.insert(tk.END,text)
            textt.place(relx=0,rely=0,relwidth=1,relheight=1)

            scrbar=tk.Scrollbar(tp)
            scrbar.pack(side=tk.RIGHT,fill=tk.Y)

            scrbar.config(command=textt.yview)
            textt.config(yscrollcommand=scrbar.set,state='disabled')

        #菜单
        self.menu=tk.Menu(self.root,tearoff=False)
        self.root.config(menu=self.menu)

        self.menuinfo=tk.Menu(self.menu,tearoff=False)
        self.menuinfo.add_command(label='关于程序',command=_programeinfo)
        self.menuinfo.add_command(label='关于作者',command=_createrinfo)
        
        self.menu.add_command(label='答疑',command=_answer)
        self.menu.add_cascade(label='关于',menu=self.menuinfo)
        self.menu.add_command(label='更新日志',command=_update_journal)
        #self.menu.add_command(label='退出',command=_exit)

        self.entry.bind('<Return>',_findmessage)
        self.imgentry.bind('<Return>',_getimage)
        self.imgnumentry.bind('<Return>',_getimage)
        self.pathentry.bind('<Return>',_getimage)

        #按钮
        self.buttonsearch=tk.Button(self.framelowright,text='查询',command=_findmessage,width=10,height=1)
        self.buttonsearch.place(relx=0.2,rely=0.1)
        
        self.buttongetimg=tk.Button(self.framedownright,text='获取',command=_getimage,width=10,height=1)
        self.buttongetimg.place(relx=0.2,rely=0.05)
        self.buttonpath=tk.Button(self.framedownright,text='选择路径',command=_selectpath,width=10,height=1)
        self.buttonpath.place(relx=0.2,rely=0.45)
        




if __name__ == '__main__':
    
    window=Window()
    tk.mainloop()
