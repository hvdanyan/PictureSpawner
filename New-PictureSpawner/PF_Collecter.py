#!(Write your python directory here)
#coding:utf-8

print("content-type:text/html")
print("")

import os,time,cgi,random,re

url = "(Write your url here)"

if not url.endswith("/"):#若url末尾没有以下划线结尾：
    url += "/"#则追加一个下划线，以防后面的链接出错

def dirpath(lpath, lfilelist):
    list = os.listdir(lpath)
    for f in list:
        if os.path.isdir(os.path.join(lpath,f)):    #判断如果为文件夹则放弃
            continue
        else:
            lfilelist.append(f)
    return lfilelist
    
def ImgList(html_name,flist):#更新图片遍历表文件、生成图片列表
    for html in html_name:
        if os.path.exists(html) == False or time.time()-os.stat(html).st_mtime>30:#图片遍历表的有效期为30s，超过后自动重写

            if html == 'PictureFiles_13.html':#共有四个图片遍历表
                directory = r'imgs'
            elif html == 'PictureFiles_15.html':
                directory = r'imgs\15+'
            elif html == 'PictureFiles_17.html':
                directory = r'imgs\17+'
            elif html == 'PictureFiles_18.html':
                directory = r'imgs\18+'

            with open(html,'w') as f:#图片遍历表写入及更新
                for i in dirpath(directory, []):
                    i = directory + "\\" + i 
                    f.write(i+'\r')

        with open(html, "r") as f:#打开图片遍历表
            data = re.findall(r'\S+', f.read())# 找到并提取所有的图片文件和所在目录
            flist.extend(data)#生成图片列表
    return flist

def Fname(i):# 识别完整文件名
    return re.findall(r'[^\\/=:. ]+\.[^\\/=:. ]+',i)[-1]#正则表达式

form = cgi.FieldStorage() # 创建 FieldStorage 的实例化
age_level = form.getvalue('standard')#获取数据，判断文件表等级
method = form.getvalue('method')#获取调用方式

if age_level== "18":
    html_name = ['PictureFiles_13.html','PictureFiles_15.html','PictureFiles_17.html','PictureFiles_18.html']
elif age_level== "17":
    html_name = ['PictureFiles_13.html','PictureFiles_15.html','PictureFiles_17.html']
elif age_level== "15":
    html_name = ['PictureFiles_13.html','PictureFiles_15.html']
else:
    html_name = ['PictureFiles_13.html']


if method == "listall":
    #遍历imgs文件夹以生成文件表，文件表存在超过30s后（在每次被调用时）自动更新。
    for html in html_name:
        if os.path.exists(html) == False or time.time()-os.stat(html).st_mtime>30:
    
            if html == 'PictureFiles_13.html':
                directory = r'imgs'
            elif html == 'PictureFiles_15.html':
                directory = r'imgs\15+'
            elif html == 'PictureFiles_17.html':
                directory = r'imgs\17+'
            elif html == 'PictureFiles_18.html':
                directory = r'imgs\18+'
    
            with open(html,'w') as f:
                for i in dirpath(directory, []):
                    i = directory + "\\" + i 
                    f.write(i+'\r')
    
    
        with open(html, "r") as f:    #打开文件
            data = f.read()   #读取文件
            print(data)

if method == "chooseone":
    image = ImgList(html_name,[])#执行ImgList函数，生成图片列表
    pic_directory = random.choice(image)#从图片列表随机抽取一张
    filename = Fname(pic_directory)#重新生成文件名
    pic_full_path = url+pic_directory#确认图片完整路径

    html = """{
  "code": 200,
  "file_name": "%s"
  "picture_path": "%s"
}"""%(filename,pic_full_path)

    print(html)