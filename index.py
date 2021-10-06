#!(Write your python directory here)
#coding:utf-8

print("content-type:text/html")
print("")

import re,random,os,time,configparser,cgi

"""提取表单的信息
版本信息：v1.01.0717
"""
form = cgi.FieldStorage() # 创建 FieldStorage 的实例化
sal_initial = selected_age_level = form.getvalue('s')#获取?s=""数据，判断用户选择的年龄等级#sal_inintial用于保留最初的选择。
link = form.getvalue('link')#获取?link=""如果有确定的链接，则强制打开指定图片
token = form.getvalue('t')#获取令牌
mode = form.getvalue('mode')#用于网站特殊模式判定。包括：初始化中（initializing）、反馈（activatedfeedback）、发送令牌（gettingtoken)、审核上架模式（examine)


"""初始化程序
描述：第一阶段指在程序首先检查相关配置，如果缺少配置信息，则终止程序并开启初始化的第一阶段。
第二阶段指保存从“初始化页面”返回的表单数据。
额外获取的表单信息：url、title、classify、frompixiv、mode
版本信息：v1.2.1006
"""
config = configparser.ConfigParser()

if not os.path.exists(r"imgs"):#自动创建imgs文件夹
    os.mkdir(r"imgs")

if not os.path.exists(r"undocumented-imgs"):
    os.mkdir(r"undocumented-imgs")

try:#首先尝试正常获取配置信息，如果不正常则启动初始化。
    config.read("config.ini")#读取配置文件
    url = config.get('webinfo','url')#获取网站的url
    title = config.get('webinfo','title')#获取网站的标题
    
    #本地文件是否是Pixiv的图片
    if config.get('webinfo','frompixiv') == "True":
        FromPixiv = True
    else:
        FromPixiv = False

    #是否启用年龄等级系统；若关闭，则展示所有图片。
    if config.get('webinfo','classify') == "True":
        Classify = True
        if not os.path.exists(r"imgs\15+"):#如果没有这些文件夹，就创建
            os.mkdir(r"imgs\15+")
        if not os.path.exists(r"imgs\17+"):
            os.mkdir(r"imgs\17+")
        if not os.path.exists(r"imgs\18+"):
            os.mkdir(r"imgs\18+")
    else:
        Classify = False
    
    #是否默认启用压缩图片；启用后将优先检索Compression文件夹（图片压缩后会保存的目录）。
    if config.get('webinfo','compression') == "True":
        Compression = True
    else:
        Compression = False

    #是否启用令牌系统，分为三个等级：High、Normal、None。High等级限制所有查看，Normal等级只限制17+18+
    token_salt = int(config.get('tokensys','tokensalt'))

    if config.get('tokensys','tokenenable') == "High":
        token_enable = "High"
    elif config.get('tokensys','tokenenable') == "Normal":
        token_enable = "Normal"
    else:
        token_enable = "None"

except:#如果在获取配置信息时出错，程序将自动开启初始化模式。
    if mode == "initializing":#第一阶段（见后）之后，网页被刷新，出现初始化的第二阶段：更新配置文件
        url = form.getvalue('url')
        title = form.getvalue('title')
        classify = form.getvalue('classify')#注意该变量是小写，与Classify不同
        fromPixiv = form.getvalue('frompixiv')#同上与Frompixiv不同
        compression = form.getvalue('compression')#同
        tokenenable = form.getvalue('tokenenable')
        tokensalt = form.getvalue('tokensalt')

        if not os.path.exists('config.ini'):#判断是否存在配置文件，若不存在则生成一个新的配置文件   
            cfile = open('config.ini','w')
            cfile.close()
        else:
            config.read('config.ini')

        if not config.has_section('webinfo'):#判断是否存在webinfo条目，若不存在则生成一个新的
            config.add_section('webinfo')
            
        config.set('webinfo','url',url)
        config.set('webinfo','title',title)
        config.set('webinfo','classify',classify)
        config.set('webinfo','frompixiv',fromPixiv)
        config.set('webinfo','compression',compression)

        if not config.has_section('tokensys'):#判断是否存在tokensys条目，若不存在则生成一个新的
            config.add_section('tokensys')
        config.set('tokensys','tokenenable',tokenenable)

        if not tokensalt:
            tokensalt = str(random.randint(100000000,999999999))#九位数，若未设置则随机取。
        config.set('tokensys','tokensalt',tokensalt)

        if not config.has_section('smtp'):#判断是否存在smtp条目，若不存在则生成一个新的
            config.add_section('smtp')
            config.set('smtp','host','mail.sample.com')
            config.set('smtp','user','name@sample.com')
            config.set('smtp','password','password1234')
            config.set('smtp','receiver','123456789@qq.com')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        
        webinfo_html = """设置完成，以后请直接修改config.ini文件。另外，已在该配置文件中预设了smtp的设置，如果需要开启反馈功能，请修改里面的相关设置。点击按钮正式启动。
<center><input type="button" name="Submit2" value="返回" title="返回控制页面" onclick="location.href='.'"/> </center> """

    else:
        webinfo_html = """<html>
    <head>
    <meta charset="gb2312">
    <title>初始化中</title>
    </head>

    <body>
        <form action="." method="post" accept-charset="UTF-8">
        <input type="hidden" name="mode" value="initializing">
        <label for="url">网站的地址：</label><input type="text" name="url" placeholder="在此输入网站的地址">（提示：直接复制地址栏的内容到此处）<br>
        <label for="title">网站的标题：</label><input type="text" name="title" placeholder="在此输入你的网站标题"><br>
        是否启用分级模式：<input type="radio" name="classify" value="True" id="classify_0">是<input type="radio" name="classify" value="False" id="classify_1" checked>否<br>
        图片是否来自P站：<input type="radio" name="frompixiv" value="True" id="frompixiv_0">是<input type="radio" name="frompixiv" value="False" id="frompixiv_1" checked>否<br>
        是否压缩大图片（不会删除原图片）（需要安装额外的PIL模块库！）：<input type="radio" name="compression" value="True" id="compression_0">是<input type="radio" name="compression" value="False" id="compression_1" checked>否<br>
        图片需要令牌访问：<input type="radio" name="tokenenable" value="High" id="tokenenable_0">是<input type="radio" name="tokenenable" value="Normal" id="tokenenable_1" checked>仅高等级<input type="radio" name="tokenenable" value="None" id="tokenenable_2" checked>否<br>
        令牌特征值：<input type="text" name="tokensalt" value="%s">(特征值是随机的，用来避免多个网站共用相同令牌。非必要无需修改。)<br>
    <input type="submit"></form>
    </body>
    </html>"""%(str(random.randint(100000000,999999999)))#对html的补充说明：表单传递时增加了一段accept-charset="UTF-8"，这是用来保障post正确传输中文数据用的。

        print(webinfo_html)
        os.close()#到这里结束程序

if not url.endswith("/"):#若url末尾没有以下划线结尾：
    url += "/"#则追加一个下划线，以防后面的链接出错

if token == None:
    token = ""



"""图片审核上架程序
版本信息：v2.0.0905
图片审核上架程序用于审核未上架的图片。
通过mode识别，并且包含有几个status
"""
def Fname(i):# 识别完整文件名
    return re.findall(r'[^\\/=:. ]+\.[^\\/=:. ]+',i)[-1]#正则表达式

def dirpath(lpath,flist,Classify):#生成图片遍历表 #flist表示一个空的列表
    list = os.listdir(lpath)#找到每一个图片文件并生成列表
    for f in list:
        if os.path.isdir(os.path.join(lpath,f)): #根据是否为分级决定文件夹的剔除或递归，（如果不是则递归）
            if not Classify:
                flist += dirpath(os.path.join(lpath,f),[],False)
            continue
        else:
            f = lpath + "\\" + f
            flist.append(f)#将找到的每一个图片文件加入遍历表
    return flist

def ImgList(html_name,flist,Classify):#更新图片遍历表文件、生成图片列表
    for html in html_name:
        if not Classify:
            html = 'PictureFiles.html'
            
        if os.path.exists(html) == False or time.time()-os.stat(html).st_mtime>30:#图片遍历表的有效期为30s，超过后自动重写
            if html == 'PictureFiles_13.html' or not Classify:#共有四个图片遍历表
                directory = r'imgs'
            elif html == 'PictureFiles_15.html':
                directory = r'imgs\15+'
            elif html == 'PictureFiles_17.html':
                directory = r'imgs\17+'
            elif html == 'PictureFiles_18.html':
                directory = r'imgs\18+'

            with open(html,'w') as f:#图片遍历表写入及更新
                for i in dirpath(directory, [],Classify):
                    f.write(i+'\r')

        with open(html, "r") as f:#打开图片遍历表
            data = re.findall(r'\S+', f.read())# 找到并提取所有的图片文件和所在目录
            flist.extend(data)#生成图片列表
    return flist

def admin_token_spawner():
    global token_salt
    import hashlib
    md5 = hashlib.md5()
    md5.update(str(token_salt).encode('utf-8'))
    return str(md5.hexdigest())#管理员令牌

if mode == "examine":
    admin_token = admin_token_spawner()
    import logging,shutil

    def movefile(srcfile,dstfile):
        if os.path.isfile(srcfile):
            fpath,fname=os.path.split(dstfile)    #分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)                #创建路径
            shutil.move(srcfile,dstfile)          #移动文件

    def get_size(file):
    # 获取文件大小:KB
        size = os.path.getsize(file)
        return size / 1024

    #日志系统初始化
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler("examined-handle-info.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    status = form.getvalue('r')#判断是操作模式还是执行模式
    pic_path = form.getvalue('pic_path')
    pic_name = form.getvalue('pic_name')

    html_name = ['PictureFiles_13.html','PictureFiles_15.html','PictureFiles_17.html','PictureFiles_18.html']

    if token != admin_token:#身份验证:
        html="""
        <html>
        <head>
            <meta charset="gb2312">
            <meta content="width=device-width,user-scalable=no" name="viewport">
            <meta http-equiv="refresh" content="0;url=.">
            <title>非法访问</title>
        </head>
        <body>
            <script type="text/javascript">  
            function shut(){  
                window.opener=null;  
                window.open('','_self');  
                window.close();  
            }  
            </script>  
            </head>  
            <body>  
            <br><br><br>
            <center>正在跳转中……</center>
        </body>
        </html>
        """
    elif status == "Activated":#此status执行图片上传功能
        #根据输入信息生成图片移动的目标文件夹
        if selected_age_level == "13":
            storedPath = r"imgs/"
        elif selected_age_level == "15":
            storedPath = r"imgs/15+/"
        elif selected_age_level == "17":
            storedPath = r"imgs/17+/"
        elif selected_age_level == "18":
            storedPath = r"imgs/18+/"
        elif selected_age_level == "deleted":
            storedPath = r"undocumented-imgs/deleted-imgs/"
        else:
            storedPath = r"undocumented-imgs/"
            
        targetPath = storedPath+pic_name
        movefile(pic_path,targetPath)#移动
        
        if selected_age_level == "deleted":
            logger.info("删除 %s -> %s"%(pic_path,targetPath))#写入日志
        elif pic_name != pic_path:
            logger.info("上架 %s -> %s"%(pic_path,targetPath))#写入日志
            try:
                srcFile = re.findall(r'\S+_\d+.\S+',targetPath)[0]
                
                #本地文件是否是Pixiv的图片
                if FromPixiv == True:
                    pixivprogram = """dstFile = srcFile.replace("_","_p")"""#自动为p站图片后缀增加p，如XXXXXX_1.jpg ==>XXXXXX_p1.jpg
                else:
                    pixivprogram = "pass"

                dstFile = srcFile.replace(" ","-")#自动将文件中的空格替换成横线
                exec(pixivprogram)#执行特殊命令
                try:
                    os.rename(srcFile,dstFile)
                    logger.info("改名 %s -> %s"%(srcFile,dstFile))#写入日志
                except:
                    targetPath = "undocumented-imgs\\deleted-imgs\\" + Fname(srcFile)#将图片删除
                    movefile(srcFile,targetPath)
                    logger.info("删除 %s -> %s"%(srcFile,targetPath))#写入日志
            except:
                pass
        
        html="""
        <html>
        <head>
            <meta charset="gb2312">
            <meta content="width=device-width,user-scalable=no" name="viewport">
            <meta http-equiv="refresh" content="0;url=?mode=examine&t=%s">
            <title>执行中</title>
        </head>
        <body>
            <script type="text/javascript">  
            function shut(){  
                window.opener=null;  
                window.open('','_self');  
                window.close();  
            }  
            </script>  
            </head>  
            <body>  
            <br><br><br>
            <center>提交成功！</center>
            <center><input type="button" name="Submit2" value="返回" title="返回控制页面" onclick="location.href='?mode=examine'"/>  
            </center>  
        </body>
        </html>
        """%(admin_token)

    elif status == "Undercarriage":#此status 当接收到下架指令则进行下架操作，将图片撤回到未公开列表
        image = ImgList(html_name,[],False)
        for i in ['imgs\\','imgs\\15+\\','imgs\\17+\\','imgs\\18+\\']:#如果提取成功，则尝试进行搜索
            i += pic_name
            if (i in image):#如果提取并搜索成功
                pic_path = i
                targetPath = "undocumented-imgs\\" + pic_name#将图片撤回
                movefile(pic_path,targetPath)
                logger.info("撤回 %s -> %s"%(pic_path,targetPath))
                
                cache_pic = "compressed-"+pic_path
                try:
                    os.remove(cache_pic)#压缩图片都在compressedimgs文件夹中,尝试清除缓存图片
                    logger.info("清除 %s"%(cache_pic))
                except:
                    pass
                break
            else:
                pass
        
        html="""<html>
<head>
    <meta charset="gb2312">
    <meta content="width=device-width,user-scalable=no" name="viewport">
    <title>执行中</title>
</head>
<body>
    <script type="text/javascript">  
    function shut(){  
        window.opener=null;  
        window.open('','_self');  
        window.close();  
    }  
    </script>  
    </head>  
    <body>  
    <br><br><br>
    <center>提交成功！</center>
    <center><input type="button" name="Submit2" value="关闭页面" title="关闭" onclick="shut()"/>  
    </center>  
</body>
</html>"""

    elif status == "FileCheck": #此status检查有无重复文件
        def compare(path1, path2):
            dict1 = dirpath(path1,[],True)
            dict2 = dirpath(path2,[],True)
            for key in dict1:
                if key in dict2:
                    print(key)

        path1 = r'imgs'
        path2 = r'imgs\15+'
        path3 = r'imgs\17+'
        path4 = r'imgs\18+'
    
        print("在13+和15+中同时找到了以下图片：")
        compare(path1, path2)
        print("<br>在15+和17+中同时找到了以下图片：")
        compare(path2, path3)
        print("<br>在17+和18+中同时找到了以下图片：")
        compare(path3, path4)
    
        html = """<br>搜索完成。<a href="?mode=examine&t=%s">返回</a>"""%(admin_token)

    elif status == "compressingimages":#此status压缩图片
        from PIL import Image
        for i in ImgList(html_name,[],False):
            #print("正在批量处理图片，",i)
            size = get_size(i)
            if size > 200:#如果图片大于200kb
                outfile = "compressed-"+i#保存到compressedimgs文件夹中
                if not os.path.exists(outfile):
                    print(os.path.split(outfile)[0])
                    if not os.path.exists(os.path.split(outfile)[0]):
                        os.makedirs(os.path.split(outfile)[0])
                    #先修改图片尺寸
                    target_ySize = 850#目标图片高度
                    im = Image.open(i)#打开图片
                    x, y = im.size#获取图片原始长高
                    target_xSize = int(x * target_ySize / y)#计算修改后图片的长度
                    out = im.resize((target_xSize, target_ySize), Image.ANTIALIAS)
                    out.save(outfile)
                    #接着压缩到指定大小
                    quality = 70#初始压缩比率
                    while size > 200:
                        im = Image.open(outfile)
                        im.save(outfile, quality=quality)
                        if quality - 10 < 0:
                            break
                        quality -= 10
                        size = get_size(outfile)
                i = outfile#修改图片路径
        html = """完成 <a href="?mode=examine&t=%s">返回</a>"""%(admin_token)
 
    else:#否则展示完整网页
        otherPicture = ""
        try:
            filelist = dirpath(r'undocumented-imgs', [],True)
            name = filelist[0]
            showPicture = """<a>文件名：%s</a><br><img src="%s" height="840"alt=""/><br>"""%(Fname(name),name)
            if FromPixiv == True:
                picture_root = re.findall(r'\d{3,}', name)[0]#获取图片id#Pixiv专用
                SameIDlist = []
                for i in filelist:
                    try:
                        re.findall(picture_root,i)[0]
                        showPicturecode = """<a>%s</a><br><img src="%s" width="540" alt=""/><br>"""%(i,i)
                        SameIDlist.append(showPicturecode)
                    except:
                        break
                
                for i in ImgList(html_name,[],False):
                    try:
                        re.findall(picture_root,i)[0]#尝试查找相同的id文件
                    except:
                        continue
                    else:
                        otherPicture += "<a><strong>在上架图片中找到了相同id的文件！</strong></a><br>"
                        break

                if int(len(SameIDlist)) > 1:
                    otherPicture += "<a>等待审核的图片中找到了相同id的文件</a><br>"
                    for i in SameIDlist:
                        otherPicture += i
                else:
                    pass
        except:
            showPicture = name = "文件已处理完毕.attention"
            otherPicture = ""
        
        html = """
        <html>
        <head>
        <meta charset="gb2312">
        <title>图片上架程序</title>
        <link rel="icon" href="./set.png">
        </head>
            
        <body>
        <table width="100%%" border="1">
            <tbody>
                <tr>
                <td valign="top">
                <table width="320" border="0">
                <tbody>
                    <tr>
                        <td>%s</td>
                    </tr>
                    <tr>
                        <td width="320" valign="top">
                        <form name="form1" method="get" action="" accept-charset="UTF-8">
                        <label>按住alt+1、2、3、4快速选择，按回车确认<br>
                        <input type="hidden" name="pic_path" value="%s">
                        <input type="hidden" name="pic_name" value="%s">
                        <input type="hidden" name="r" value="Activated">
                        <input type="hidden" name="mode" value="examine">
                        <input type="hidden" name="t" value="%s">
                        <input type="radio" name="s" value="13" id="RadioGroup1_0" accesskey="1">13+
                        <input type="radio" name="s" value="15" id="RadioGroup1_1" accesskey="2">15+
                        <input type="radio" name="s" value="17" id="RadioGroup1_2" accesskey="3">17+
                        <input type="radio" name="s" value="18" id="RadioGroup1_3" accesskey="4">18+
                        <input type="radio" name="s" value="deleted" id="RadioGroup1_4" accesskey="5">删除
                        </label>
                        <input type="submit" value="确认" accesskey="enter">
                        </form>
                    </td>
                    </tr>
                </tbody>
                </table>
                </td>
                <td colspan="2"><table width="100%%" border="1">
                <tbody>
                    <tr>
                    <td>年龄分级标准（仅供参考）：<br>
                    13+：不允许任何形式的性暗示、不允许露出内裤；不允许出现骷髅、血液；不允许突出胸部和下体的姿势 <br>
                    15+：允许一定的性暗示，允许露出内衣，但不能是情趣内衣；允许兔女郎；必须包臀；不允许出现情趣用品；不允许紧缚；不允许内衣透出隐私部位的形状，不允许排尿 <br>
                    17+：允许身体裸露，但不允许包含有任何形式的性行为（不允许性行为暗示：如阴道肛门插入；流精；性高潮；身上任何部位存在白色液体；不允许出现拆开的避孕套） <br>
                    18+：允许性行为等，但不允许任何形式的暴力恐怖
                    </td>
                    </tr>
                    <tr>
                    <td>%s</td>
                    </tr>
                </tbody>
                </table>
                </tr>
                <tr>
                    <td><a href="?mode=examine&r=FileCheck&t=%s">点击检测重复文件</a>
                    <td><a href=".\examined-handle-info.log">点击查看日志</a>
                    <a href="?mode=examine&r=compressingimages&t=%s">点击压缩图片</a></td>
                </tr>
        </tbody>
        </table>
        </body>
        </html>
        """%(showPicture,name,Fname(name),admin_token,otherPicture,admin_token,admin_token)

    print(html)
    os.close()#到这里结束程序



"""令牌生成程序
版本信息：v1.0.0722
这是令牌系统的第一个程序（共计三个），该程序用于网页的特殊模式（gettingtoken）。
主要用于向指定邮箱发送一枚令牌。
令牌生成算法：Simple_Dynamic_Password_version_2,SDPv2,基本动态密码第2版
生成操作：将数字与特征值进行异或加法，之后倒转后换成十六进制，再次倒转后换成24进制。
使用的自定义函数：dTA,aTD
"""
def dTA(num,n):#10进制转任意进制
    baseStr = {10:"a",11:"b",12:"c",13:"d",14:"e",15:"f",16:"g",17:"h",18:"i",19:"j",20:"k",21:"l",22:"m",23:"n"}
    new_num_str = ""
    while num != 0:
        remainder = num % n
        if remainder > 9:
            remainder_string = baseStr[remainder]
        else:
            remainder_string = str(remainder)
        new_num_str = remainder_string+new_num_str
        num = int(num/n)
    return new_num_str
    
def aTD(num,n):#任意进制转10进制
    baseStr = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"a":10,"b":11,"c":12,"d":13,"e":14,"f":15,"g":16,"h":17,"i":18,"j":19,"k":20,"l":21,"m":22,"n":23}
    new_num = 0
    nNum = len(num) - 1
    for i in num:         
        new_num = new_num  + baseStr[i]*pow(n,nNum)
        nNum = nNum -1 
    return new_num
    
if mode == "gettingtoken":
    print("""Please Note: the following information is from the token generator.<br>
Whether you fill in the correct email or leave it blank, the generator will return a token in this way.
If the transmission is successful, 704 is returned, otherwise 701 is returned.
If you encounter an error token(which will be specially marked), do not use it.<br>""")
    for i in range(0,15):
        present_time = int(str(time.strftime("%Y%m%d%H", time.localtime(time.time())))[2:]+str(random.randint(1,9)))#获取时间，并转化成特殊格式（年+月+日+时），如21072310并在后面增加一个随机数字
        valid_token = dTA(aTD(dTA(int(str(present_time^token_salt)[::-1]),16)[::-1],16),24).upper()#将时间转化成令牌
        if present_time == int(str(aTD(dTA(aTD(valid_token.lower(),24),16)[::-1],16))[::-1])^token_salt:#如果生成的令牌是假的，就重新生成，不超过15次。（确实有可能生成假令牌。不过一般再生成一次就可以了）
            print("<h3>Information from Token Generator:Your token is "+valid_token+".</h3>Return code:")#方便没有邮箱的人。
            break
        else:
            print("Error token:"+valid_token+"<br>")
    
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    try:
        config.read('config.ini')    
        mail_host = config.get('smtp','host')
        sender = mail_user = config.get('smtp','user')
        mail_pass = config.get('smtp','password')
        receivers = [form.getvalue('mail')]# 自定邮件接收者。

        letter = """
<style>
    .letter{
    border-radius: 37px;
    background: #e0e0e0;
    box-shadow:  36px 36px 72px #acacac,
                -36px -36px 72px #ffffff;
    }
</style>
<div id="letter"><table width="80%%" border="0" align="center" ><tr><td><h2>%s的用户，您好！</h2><h3>&nbsp; &nbsp; &nbsp; &nbsp;在刚才您申请了一枚用于访问的令牌，请在输入框内填入：</h3>
<center><span style="font-size: 24px">%s</span></center>
<h3 style="text-align: center">该令牌是即时生成的，具有24h的有效期（按照整点计算，因此时间可能会略小于一天），<br>在24h内你随时可以通过这枚令牌访问限制性内容且没有次数限制，因此您不必重复申请该令牌。</h3>
<h4>邮件发送时间：%s</h4></tr></td></div>"""%(title,valid_token,time.asctime(time.localtime(time.time())))

        message = MIMEText(letter,'html', 'utf-8')
        message['From'] = Header("%s<%s>"%(title,sender), 'utf-8')
        message['To'] =  Header(receivers[0], 'utf-8')
        message['Subject'] = Header('网站令牌口令', 'utf-8')

        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)#25为端口号
        smtpObj.login(mail_user,mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("704")
    except:
        print("701")#701表示服务器错误，邮件发送失败
    os.close()#到这里结束程序


"""反馈处理程序
网站会返回若干种代码表示反馈情况。
错误代码：701（服务器错误）、702、703、706（服务器返回的不是一般特征值）
测试代码：705（该代码仅用于测试）
成功代码：704
额外获取的表单信息：picdirectory
使用的函数：Fname
版本信息v3.1.0722
"""
if mode == "activatedfeedback":#提交，原理是发送一份包含有下架链接的邮件。
    import smtplib#导入邮箱smtp模块
    from email.mime.text import MIMEText
    from email.header import Header

    picdirectory = form.getvalue('picdirectory')#仍要注意区分变量pic_directory
    InCorrectClassification = form.getvalue('ICCF1')
    DislikeTheImage = form.getvalue('DLTI2')

    try:
        picname = Fname(picdirectory)
    except:
        info = "703"#703代码：错误：不能确定需要反馈的图片。
    else:
        if InCorrectClassification or DislikeTheImage:
            try:#尝试发送邮件
                admin_token = admin_token_spawner()
                config.read('config.ini')    
                mail_host = config.get('smtp','host')
                sender = mail_user = config.get('smtp','user')
                mail_pass = config.get('smtp','password')
                receivers = [config.get('smtp','receiver')]# 接收邮件，可设置为你的QQ邮箱或者其他邮箱
                
                letter = "尊敬的管理员，您好！\n服务器在刚才收到了一条来自用户的反馈。反馈内容如下：\n"
                letter += "图片信息："+ picdirectory +"\n"
                letter += "图片文件名称："+ picname+"\n"
                letter += "用户认为："
                if InCorrectClassification:
                    letter += "不合理的图片分级；"
                if DislikeTheImage:
                    letter += "不喜欢这张图片；"
                undocu_url = url + """?mode=examine&r=Undercarriage&pic_name=%s&t=%s"""%(picname,admin_token)#生成下架链接
                letter += "\n点击该链接将图片下架："+ undocu_url +"\n"
                letter += "在此处打开图片上架程序：%s?mode=examine&t=%s\n"%(url,admin_token)
                letter += "反馈时间：%s"%(time.asctime(time.localtime(time.time())))

                message = MIMEText(letter, 'plain', 'utf-8')
                message['From'] = Header("%s<%s>"%(title,sender), 'utf-8')
                message['To'] =  Header("管理员", 'utf-8')
                subject = '来自用户的反馈'
                message['Subject'] = Header(subject, 'utf-8')


                smtpObj = smtplib.SMTP() 
                smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
                smtpObj.login(mail_user,mail_pass)  
                smtpObj.sendmail(sender, receivers, message.as_string())
                info = "704"#704代码：表示邮件发送成功
            except:
                info = "701"#701代码：错误：SMTP服务器异常，邮件发送失败。
        else:
            info = "702"#702代码：错误：没有勾选反馈原因。
    print(info)       
    os.close()#到这里结束程序



"""生成图片列表
版本信息：v1.3.0722
使用的自定义函数：dirpath;ImgList
"""
FullFile = ['PictureFiles_13.html','PictureFiles_15.html','PictureFiles_17.html','PictureFiles_18.html']#图片遍历表目录

if not Classify:#0715版本新增：若分级系统关闭，则使用13+图库
    html_name = FullFile[0:1]
elif selected_age_level == "18":#选择18+等级会使用完整的图片遍历表
    html_name = FullFile
elif selected_age_level == "AO":#同时加载17+和18+
    html_name = FullFile[2:4]
elif selected_age_level == "17":
    html_name = FullFile[0:3]
elif selected_age_level == "15":
    html_name = FullFile[0:2]
else:
    selected_age_level = "13"#如果不存在则自动判定年龄等级为13+
    html_name = FullFile[0:1]#必须是一个列表

vice_image = ImgList(html_name,[],Classify)#执行ImgList函数，生成图片列表副表，副表在后面查找相同id的图片时有用

if link:#要求打开指定图片时，会使用完整的图片遍历表
    image = ImgList(FullFile,[],Classify)
else:
    image = vice_image


"""抽取图片或者打开指定图片
版本信息：v1.6.0721
描述：除了抽取随机图片外，还可以打开指定图片。每一步骤都有详细追踪。
变量解释：
filename:图片文件名，包括后缀
Extract_statement:标记提取状态，用于“打开指定图片”时使用，如果提取失败，则随机抽取图片
pic_directory:完整的图片目录，包括所在文件夹
使用的自定义函数：ImgList
"""
Extract_statement = False#当前提取状态：未成功
if not link:
    pic_directory = random.choice(image)#没有设置就随便抽一张图片
else:
    for i in image:
        try:
            re.findall(link,i)[0]#尝试完整匹配
            pic_directory = i
        except:
            try:
                re.findall(Fname(link),i)[0]#若匹配失败，则提取文件名后再匹配
                pic_directory = i
            except:
                pass
            else:
                Extract_statement = True#当前提取状态：成功
                break
        else:
            Extract_statement = True#当前提取状态：成功
            break

    if not Extract_statement:#如果提取失败
        pic_directory = random.choice(image)#则随便抽取一张


"""获取该图片的有关信息
版本信息：v1.2
描述：生成图片文件名、完整网络路径、图片年龄等级
使用的自定义函数：Fname
"""
filename = Fname(pic_directory)#重新生成文件名
o_pic_full_path = (url + pic_directory).replace("\\","/")#生成原始目录，在“查看原图”时有用#用于反转录(其实用\\\\也行)

try:
    picture_level = re.findall(r'\d+\+', pic_directory)[0]#获取图片年龄等级
except:
    picture_level = "13+"#若获取失败，说明是13+图片


"""替换原图片
版本信息：v1.1.0721
描述：判断选择的图片是否过大，如果图片过大，则替换为一张尺寸较小的图片，加快网页浏览速度。
"""
originpicbutton = "none"
if Compression:#如果开启了图片压缩
        outfile = "compressed-"+pic_directory#压缩图片都在compressedimgs文件夹中
        if os.path.exists(outfile):
            pic_directory = outfile#修改图片路径
            originpicbutton = "inline"


"""令牌系统通行检测
版本信息：v1.1.0722
描述：令牌系统的第二个程序。
用于判定是否给予访问权限。
阻挡未授权者访问高等级图片。
是否阻止与“年龄模式”有关，与图片等级本身无关。
解密操作：将令牌按照二十四进制转十六进制，倒转后转十进制，再倒转，最后与特征值进行异或加法。
使用的自定义函数：dTA,aTD
"""
if token_enable != "None":
    permission = False
    if (token_enable == "High" and not link) or selected_age_level == "17" or selected_age_level== "18" or selected_age_level == "AO":#在这三个等级下或者是强制令牌审查时需要验证。
        try:
            reg_time = str(int(str(aTD(dTA(aTD(token.lower(),24),16)[::-1],16))[::-1])^token_salt)#将token解密成时间
            timeStamp = int(time.mktime(time.strptime("20%s %s %s %s 00 00"%(reg_time[0:2],reg_time[2:4],reg_time[4:6],reg_time[6:8]),"%Y %m %d %H %M %S")))#将regtime分段转化成时间，然后用模块库的strptime改写，再用mktime封装成时间戳。
        except:
            pass
            
        else:
            if time.time()-timeStamp > 86400 or timeStamp>time.time():#如果时间大于一天，即token过期
                pass
            else:#若没有过期，则给予放行
                permission = True
    else:
        permission = True
else:
    permission = True
            

"""生成网页内容
版本信息：v1.9.1002
描述：生成图片原地址、分享链接、回退链接、标题、显示年龄等级
超文本版本信息：v4.1.1002
"""
showPictureCode = """background-image: url(%s);"""%(url+pic_directory.replace("\\","/"))#生成超文本图片显示代码
showSimilarpic = ""

if FromPixiv:
    picture_root = re.findall(r'\d{4,}', filename)[0]#获取图片id#Pixiv专用
    SameIDlist = []
    for i in vice_image:
        try:
            re.findall(picture_root,i)[0]#尝试查找相同的id文件
        except:
            continue
        else:
            if Fname(i) == Fname(pic_directory):#除去这个文件本身
                SameIDlist.append("""<a>%s</a>"""%(Fname(i)))
            else:
                SameIDlist.append("""<a href="javascript:post('.','%s','%s','%s')">%s</a>"""%(selected_age_level,token,i.replace("\\","/"),Fname(i)))##同时显示超链接
            if not len(SameIDlist)== 1:
                showSimilarpic = """找到了相同ID的图片:%s"""%(' '.join(SameIDlist))
    
    origin_link = '"https://www.pixiv.net/artworks/'+picture_root+'"'
    Hyperlink_account = "p站ID："

else:
    picture_root = ""
    origin_link = url
    Hyperlink_account = "&nbsp"#在html中表示空格

try:#判断是不是动图
    re.findall(r'compressed\S+.gif',pic_directory)[0]
except:
    pass
else:
    showSimilarpic = """该图片是动图，若要查看请点击点击“查看原图”。"""

if not sal_initial and link:#直接输入一个变量时，表示布尔值 相当于not True 和 True
    used_age_level = "[尚未定义]"
else:
    used_age_level = selected_age_level

if Classify:#0715更新，分级系统，修改第一行描述
    account = "当前年龄模式：%s+&nbsp&nbsp该图片等级：%s&nbsp&nbsp该模式当前包含%s张图片。单击图片打开下一张。%s<a href=%s target=_blank>%s</a>&nbsp&nbsp"%(used_age_level,picture_level,len(image),Hyperlink_account,origin_link,picture_root)

    #修改年龄等级的表单
    FormOFChangeAgeLevel ="""<form action="." method="post">更改年龄等级：
    <label>
    <input type='hidden' name='t' value='%s'/>
    <input type="radio" name="s" value="13" id="RadioGroup1_0">13+
    <input type="radio" name="s" value="15" id="RadioGroup1_1">15+
    <input type="radio" name="s" value="17" id="RadioGroup1_2">17+
    <input type="radio" name="s" value="18" id="RadioGroup1_3">18+
    <input type="radio" name="s" value="AO" id="RadioGroup1_4">Adult Only
    </label>
    <input type="submit" value="确认">
    </form>"""%(token)
else:
    account = "单击图片打开下一张。%s<a href=%s target=_blank>%s</a>&nbsp&nbsp"%(Hyperlink_account,origin_link,picture_root)
    FormOFChangeAgeLevel = ""

shared_url = url+"?link="+filename#创建分享链接
  
if link and not sal_initial:#使用分享链接时，修改标题，便于浏览器保存记录
    title = title + "-" + filename

"""令牌系统阻断程序
描述：令牌系统的第三个程序。
该程序会在所有程序就绪后工作，
如果未经授权，则阻止显示图片、显示“查看原图”按钮、显示类似图片；反馈系统不能获取图片信息。
"""
if not permission:#执行有关于令牌系统的后续操作
    main_page ="""</form><br><h1>很抱歉，启用该等级需要输入令牌</h1>
        <form action="." method="post">在此输入令牌口令：
        <input type='hidden' name='s' value='%s'/>
        <input type="text" class="txtbox" name="t" value="">
        <input type="submit" value="确认">
        </form>
        <h2>什么是令牌？</h2>
        <h3>令牌是一枚有效期为24h的口令，必须输入正确的口令才可以访问高等级的内容。</h3>
        <h4>在有效期内，令牌是可以无限次使用的，因此令牌不需要重复申请。</h4>
        <h5>网站不会记住你的登陆状态，因此在再次访问时，你需要重新填入之前的令牌。</h5>
        <form id="get_token_form">
            <input type="hidden" name="mode" value="gettingtoken">
            <h3>请输入邮箱来申请一枚令牌：</h3>
            <p>邮箱：<input type="text" name="mail" value=""> 
            <a href = "javascript:void(0)" onclick = "gettingtoken()"><input type="button" id="btn" value="获取令牌" onclick="settime(this)" /></a>
            </form></p><br>
            <h5>令牌生成算法基于SDPv2（基本动态密码v2）。</h5>
    """%(selected_age_level)
    originpicbutton = "none"
    showSimilarpic = ""
    pic_directory ="None"
else:
    main_page ="""    <a href='javascript:document.nextpic.submit();'>
                    <div id="picture" class="theframe"></div>
                </a>"""


html = """
<html>
<head>
<meta charset="gb2312">
<meta content="width=device-width,user-scalable=yes" name="viewport">
<title>%s</title>
<link rel="icon" href="./logo.png">
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<SCRIPT LANGUAGE="JavaScript">
    window.alert = function(name){//删除提示框显示域名
        var iframe = document.createElement("IFRAME");
        iframe.style.display="none";
        iframe.setAttribute("src", 'data:text/plain,');
        document.documentElement.appendChild(iframe);
        window.frames[0].window.alert(name);
        iframe.parentNode.removeChild(iframe);
    };

    function copyurl(){//复制分享链接
        var input=document.getElementById("shared_url");
        input.select(); 
        document.execCommand("Copy"); 
        alert("链接复制成功！");
    }

    function post(url,s,t,link) {//使用js代码实现隐藏form表单的实现
        var temp = document.createElement("form"); //创建form表单
        temp.action = url;
        temp.method = "post";
        temp.style.display = "none";//表单样式为隐藏
        var adds =document.createElement("input");  
            adds.type="hidden";  
            adds.name = "s";    
            adds.value = s;  
            temp.appendChild(adds);
        var addt =document.createElement("input");  
            addt.type="hidden"; 
            addt.name = "t";    
            addt.value = t;  
            temp.appendChild(addt);
        var addl =document.createElement("input"); 
            addl.type="hidden"; 
            addl.name = "link";   
            addl.value = link;   
            temp.appendChild(addl);
        
        document.body.appendChild(temp);
        temp.submit();
        return temp;
    }

    function openfeedback(){
        document.getElementById('feedback_content').style.display='block';
        document.getElementById('mainbox').style.display='block';//重置反馈模块
        document.getElementById('responsebox').style.display='none';
        document.getElementById('backoffbox').style.display='none';
    }

    function closefeedback(){
        document.getElementById('feedback_content').style.display='none';
    }

    function activatingfeedback(){
        document.getElementById('mainbox').style.display='none';
        document.getElementById("responsebox").innerHTML = "<font size='3px'>正在反馈中……</font>";
        document.getElementById('responsebox').style.display='block';
        var xmlhttp;
        xmlhttp=new XMLHttpRequest();
        xmlhttp.onreadystatechange=function(){
            var code;
            if (xmlhttp.readyState==4 && xmlhttp.status==200){
                code= xmlhttp.responseText;
                
                if(code != "" && code.search(701) != -1){
                    document.getElementById("responsebox").innerHTML = "<font color='red' size='3px'>错误701：SMTP服务器异常，反馈提交失败。</font>";
                }else if (code != "" && code.search(702) != -1){
                    document.getElementById("responsebox").innerHTML = "<font color='red' size='3px'>错误702：请勾选相关内容后再提交！</font>";
                }else if (code != "" && code.search(703) != -1){
                    document.getElementById("responsebox").innerHTML = "<font color='red' size='3px'>错误703：未能提取出所填写的图片名称。</font>";
                }else if (code != "" && code.search(704) != -1){
                    document.getElementById("responsebox").innerHTML = "<font color='green' size='3px'>反馈成功！</font>";
                    document.getElementById("submitbutton").innerHTML = "";
                    document.getElementById("backoffbox").innerHTML = "";
                }else if (code != "" && code.search(705) != -1){
                    document.getElementById("responsebox").innerHTML = "<font size='3px'>测试705：测试705</font>";
                }else{
                    document.getElementById("responsebox").innerHTML = "<font size='3px'>错误706：服务器无响应。</font>";
                }
                document.getElementById('backoffbox').style.display='block';
            }
        }  
        xmlhttp.open("post",".",true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded; charset=utf-8");
        xmlhttp.send($("#apply_link_form").serialize());
    }

    function gettingtoken(){
        var xmlhttp;
        xmlhttp=new XMLHttpRequest();
        xmlhttp.onreadystatechange=function(){
            var code;
            if (xmlhttp.readyState==4 && xmlhttp.status==200){
                code= xmlhttp.responseText;
            }
        }
        xmlhttp.open("post",".",true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded; charset=utf-8");
        xmlhttp.send($("#get_token_form").serialize());
    }

    function showorigin(){
        $('.theframe').css('background-image', 'url(%s)');
        document.getElementById('originpicbutton').style.display='none';
    }

    var countdown=60; 
    function settime(val) { 
        if (countdown == 0) { 
        val.removeAttribute("disabled"); 
        val.value="免费获取验证码"; 
        countdown = 60; 
        } else { 
        val.setAttribute("disabled", true); 
        val.value="重新发送(" + countdown + ")"; 
        countdown--; 
        } 
        setTimeout(function() { 
        settime(val) 
        },1000) 
    } 
    
</SCRIPT>
<style>
    .theframe{
        max-width: 100%%;
        height: calc(97vh - 30px);
        background-repeat: no-repeat;
        background-size: contain;
        background-position-x: center;
        %s
    }

    #shared_url {
        position: absolute;
        top: -100px;
    }

    #feedback_content { 
        display: none; 
        position: fixed; 
        top: 25%%; 
        left: 25%%; 
        width: 50%%; 
        height: 50%%; 
        padding: 20px; 
        border: 10px solid #989898; 
        background-color: white; 
        z-index:1002; 
        overflow: auto; 
    }

    .txtbox {
        color:#333;
        line-height:normal;font-style:normal;font-variant:normal;font-size-adjust:none;font-stretch:normal;font-weight:normal;
        margin-top:0px;margin-bottom:0px;margin-left:0px;
        padding-top:4px;padding-right:4px;padding-bottom:4px;padding-left:4px;
        font-size:15px;
        outline-width:medium;outline-style:none;outline-color:invert;
        border-top-left-radius:3px;border-top-right-radius:3px;border-bottom-left-radius:3px;border-bottom-right-radius:3px;
        text-shadow:0px 1px 2px #fff;
        background-attachment:scroll;background-repeat:repeat-x;background-position-x:left;background-position-y:top;background-size:auto;
        background-origin:padding-box;background-clip:border-box;background-color:rgb(255,255,255);
        margin-right:8px;
        border-top-color:#ccc;border-right-color:#ccc;border-bottom-color:#ccc;border-left-color:#ccc;border-top-width:1px;border-right-width:1px;
        border-bottom-width:1px;border-left-width:1px;border-top-style:solid;border-right-style:solid;border-bottom-style:solid;border-left-style:solid;
    }
</style>
</head>

<body>
    <table width="95%%" border="0" align="center">
    <tbody>
    <tr>
	    <td colspan="2">
	    <center>
	    <input type="button" id="originpicbutton" style="display: %s" value="查看原图" onclick="showorigin()">
        <a href="%s" target=_blank><input type="button" value="点击打开大图" onclick="showorigin()"></a>
	    <a>%s</a>
	    <input type="url" id="shared_url" value="%s">
	    <input type="button" title="点击以复制分享链接" value="一键分享图片" onclick="copyurl()">
	    </center>
        </td>
    </tr>
    <tr>
	    <td colspan="2" valign="top">
	        <center>
	        <form name='nextpic' action='.' method='post'>
            <input type='hidden' name='s' value='%s'/>
            <input type='hidden' name='t' value='%s'/>
            %s
            </form>
            </center>
        </td>
    </tr>
    <tr>
        <td align="center">
        <a>%s</a>
	    </td>
    </tr>
    <tr>
        <td align="center"><br>
            <form action="." method="post">打开指定图片：
            <input type='hidden' name='s' value='%s'/>
            <input type='hidden' name='t' value='%s'/>
            <input type="text" id="Target_url" class="txtbox" name="link" onkeyup="this.size=(this.value.length>25?this.value.length:25);" size="25" value="">
            <input type="submit" value="确认">
            </form>
        </td>
    </tr>
    <tr>
        <td>
            <table width="100%%" border="0" align="center">
            <tbody>
            <tr>
	            <td align="center">%s</td>
		        <td align="center">
                    <p><a href = "JavaScript:void(0)" onclick = "openfeedback()"><input type="button" value="我要反馈"></a></p> 

                    <div id="feedback_content">
                    <div id="mainbox">
                    <table>
                        <tr>
                            <td>
                                <form id="apply_link_form">
                                <input type="hidden" name="mode" value="activatedfeedback">
                                <center>图片信息：<input type="text" name="picdirectory" value="%s"><input type="reset" value="重置"></center>
                                <p>
                                <label><input type="checkbox" name="ICCF1" value="True">我认为分级有误</label><br>
                                <label><input type="checkbox" name="DLTI2" value="True">我不喜欢这张图片</label>
                                </p>
                                <div id="submitbutton"><center><a href = "javascript:void(0)" onclick = "activatingfeedback()"><input type="button" value="提交"></a></center></div>
                                </form>
                            </td>
                        </tr>
                    </table>
                    </div>
                    <div id="responsebox"></div>
                    <div id="backoffbox"><a href = "javascript:void(0)" onclick = "openfeedback()"><input type="button" value="回退"></a></div><br>
                    <a href = "javascript:void(0)" onclick = "closefeedback()">点这里关闭本窗口</a>
                    </div>
		        </td>
            </tr>
            </tbody>
            </table>
        </td>
    </tr>
</tbody>
</table>
</body>
</html>
"""%(title,o_pic_full_path,showPictureCode,originpicbutton,o_pic_full_path,account,shared_url,selected_age_level,token,main_page,showSimilarpic,selected_age_level,token,FormOFChangeAgeLevel,pic_directory)
#关于html的补充说明：在style中，img用来限制图片的尺寸，shared_url用来隐藏文本框（因为复制链接必须要有一个文本框，所以就把这个文本框放在了看不见的地方。）
#所有的百分比一定要打两个“%”！否则打不开

print(html)