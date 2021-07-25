#!(Write your python directory here)
#coding:utf-8

print("content-type:text/html")
print("")

import os,shutil,re,cgi,logging

import configparser
config = configparser.ConfigParser()
config.read("config.ini")#读取配置文件
FromPixiv= config.get('webinfo','frompixiv')

#日志系统
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("examined-handle-info.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""生成图片列表
版本信息：v1.1.0705
使用的自定义函数：dirpath;ImgList
"""
form = cgi.FieldStorage() # 创建 FieldStorage 的实例化
selected_age_level = used_age_level = form.getvalue('s')#获取?s=""数据，判断用户选择的年龄等级
status = form.getvalue('r')#判断是操作模式还是执行模式
pic_path = form.getvalue('pic_path')
pic_name = form.getvalue('pic_name')

def Fname(i):# 识别完整文件名
    f = re.findall(r'[^\\/=:. ]+\.[^\\/=:. ]+',i)[-1]#正则表达式
    return f
def Fpath(i):#识别年龄等级文件夹
    f = re.findall(r'\\imgs\S*',i)[0]
    return f

def dirpath(lpath, flist):#生成图片遍历表 #flist表示一个空的列表
    list = os.listdir(lpath)#找到每一个图片文件并生成列表
    for f in list:#排除其中混入的文件夹
        if os.path.isdir(os.path.join(lpath,f)):    #判断如果为文件夹则剔除
            continue
        else:
            flist.append(f)#将找到的每一个图片文件加入遍历表
    return flist

def movefile(srcfile,dstfile):
    if os.path.isfile(srcfile):
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件

def ImgList(flist):#生成图片列表
    for html in ['PictureFiles_13.html','PictureFiles_15.html','PictureFiles_17.html','PictureFiles_18.html']:#图片遍历表目录
        try:
            with open(html, "r") as f:#打开图片遍历表
                data = re.findall(r'\S+', f.read())# 找到并提取所有的图片文件和所在目录
                flist.extend(data)#生成图片列表
        except:
            pass
    return flist

def get_size(file):
# 获取文件大小:KB
    size = os.path.getsize(file)
    return size / 1024

"""执行模式"""
if status == "Activated":
    #根据输入信息生成图片移动的目标文件夹
    if selected_age_level == "13":
        storedPath = r"imgs/"
    if selected_age_level == "15":
        storedPath = r"imgs/15+/"
    if selected_age_level == "17":
        storedPath = r"imgs/17+/"
    if selected_age_level == "18":
        storedPath = r"imgs/18+/"
    if selected_age_level == "deleted":
        storedPath = r"undocumented-imgs/deleted-imgs/"
        
    targetPath = storedPath+pic_name
    movefile(pic_path,targetPath)#移动
    
    if selected_age_level == "deleted":
        logger.info("删除 %s -> %s"%(pic_path,targetPath))#写入日志

    else:
        logger.info("上架 %s -> %s"%(pic_path,targetPath))#写入日志
        try:
            srcFile= a = re.findall(r'\S+_\d+.\S+',targetPath)[0]
            
            #本地文件是否是Pixiv的图片
            if config.get('webinfo','frompixiv') == "True":
                pixivprogram = """dstFile = srcFile.replace("_","_p")"""
            else:
                pixivprogram = "pass"

            dstFile = srcFile.replace(" ","-")
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
        <meta http-equiv="refresh" content="0;url=examined.py">
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
        <center><input type="button" name="Submit2" value="返回" title="返回控制页面" onclick="location.href='\examined.py'"/>  
        </center>  
    </body>
    </html>
    """

#下架操作执行模式 当接收到下架指令则进行下架操作，将图片撤回到未公开列表
elif status == "Undercarriage":
    image = ImgList([])
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
        else:
            pass
    
    html="""
    <html>
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
    </html>
    """

#操作模式-检查有无重复文件
elif status == "FileCheck":
    def compare(path1, path2):
        dict1 = dirpath(path1,[])
        dict2 = dirpath(path2,[])
        for key in dict1:
            if key in dict2:
                print(key)

    path1 = r'imgs'
    path2 = r'imgs\15+'
    path3 = r'imgs\17+'
    path4 = r'imgs\18+'
 
    print("在13+和15+中同时找到了以下图片：")
    compare(path1, path2)
    print("在15+和17+中同时找到了以下图片：")
    compare(path2, path3)
    print("在17+和18+中同时找到了以下图片：")
    compare(path3, path4)
 
    html = """搜索完成。<a href=".\examined.py">返回</a>"""

#换名模式-将_换成_p(用于pixiv图片)和以及空格换成-
elif status == "namechange":
    #本地文件是否是Pixiv的图片
    if config.get('webinfo','frompixiv') == "True":
        pixivprogram = """dstFile = srcFile.replace("_","_p")"""
    else:
        pixivprogram = "pass"
    
    image = ImgList([])
    for f in image:
        try:
            srcFile=a = re.findall(r'\S+_\d+.\S+',f)[0]
            print(srcFile)
            exec(pixivprogram)#执行特殊命令
            dstFile = srcFile.replace(" ","-")
            try:
                if dstFile != srcFile:
                    os.rename(srcFile,dstFile)
                    logger.info("改名 %s -> %s"%(srcFile,dstFile))#写入日志
            except:
                targetPath = "undocumented-imgs\\deleted-imgs\\" + Fname(srcFile)#将图片删除
                movefile(srcFile,targetPath)
                logger.info("删除 %s -> %s"%(srcFile,targetPath))#写入日志
        except:
            continue
    html = """改名完成，重复的文件已经自动删除。<a href=".\examined.py">返回</a>"""

elif status == "compressingimages":
    from PIL import Image
    for i in ImgList([]):
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
    html = """完成 <a href=".\examined.py">返回</a>"""

#操作模式  
else:
    otherPicture = ""
    try:
        filelist = dirpath(r'undocumented-imgs', [])
        name = "undocumented-imgs\\" + filelist[0]
        showPicture = """<a>文件名：%s</a><br><img src="%s" height="840"alt=""/><br>"""%(Fname(name),name)
        if FromPixiv == True:
            picture_root = re.findall(r'\d{3,}', name)[0]#获取图片id#Pixiv专用
            SameIDlist = []
            for i in filelist:
                try:
                    re.findall(picture_root,i)[0]
                    showPicturecode = """<a>%s</a><br><img src="undocumented-imgs\\%s" width="540" alt=""/><br>"""%(i,i)
                    SameIDlist.append(showPicturecode)
                except:
                    break
            
            for i in ImgList([]):
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
					<form name="form1" method="get" action=".\examined.py">
            		<label>按住alt+1、2、3、4快速选择，按回车确认<br>
					<input type="hidden" name="pic_path" value="%s">
					<input type="hidden" name="pic_name" value="%s">
					<input type="hidden" name="r" value="Activated">
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
				13+：不允许任何形式的性暗示、不允许裸露（允许兔女郎，不允许露出内裤；不允许出现骷髅、血液；不允许突出胸部和下体的站姿） <br>
				15+：允许一定的性暗示，但不能过于裸露（允许露出内衣；允许兔女郎；不允许胸部大部分露出；不允许下体真空，不允许真空丝袜，允许真空旗袍；不允许出现情趣用品；不允许紧缚；不允许完全露出屁股;不允许内衣透出隐私部位的形状，不允许开腿露出内裤包括旗袍，不允许排尿） <br>
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
				<td><a href=".\examined.py?r=FileCheck">点击检测重复文件</a>
				<a href=".\examined.py?r=namechange">点击矫正文件名（加p,空格改-）</a></td>
				<td><a href=".\examined-handle-info.log">点击查看日志</a>
                <a href=".\examined.py?r=compressingimages">点击压缩图片</a></td>
			</tr>
	</tbody>
    </table>
    
    
    </body>
    </html>
    """%(showPicture,name,Fname(name),otherPicture)
    
print(html)