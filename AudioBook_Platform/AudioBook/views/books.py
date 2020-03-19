from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from common.models import Books, Types
from django.db.models import Q
from datetime import datetime
import time


def index(request):
    """商品信息主页面"""
    tlist = Types.objects.extra(select={
        'path_id': 'concat(path,id)'
    }).order_by('path_id')
    for ob in tlist:
        ob.pname = '. . .' * (ob.path.count(',') - 1)
    mod = Books.objects.order_by('id')
    mywhere = []

    # 获取、判断并封装关keyword键搜索
    kw = request.GET.get('keyword', None)
    if kw:
        # 查询商品名中只要含有关键字的都可以
        good_list = mod.filter(goods__contains=kw)
        mywhere.append('keyword=' + kw)
    else:
        good_list = mod.filter()
    # 获取、判断并封装商品类别typeid搜索条件
    typeid = request.GET.get('typeid', '0')
    if typeid != '0':
        tids = Types.objects.filter(Q(id=typeid) | Q(pid=typeid)).values_list(
            'id', flat=True)
        good_list = good_list.filter(typeid__in=tids)
        mywhere.append('typeid=' + typeid)
    # 获取、判断并封装商品状态state搜索条件
    state = request.GET.get('state', '')
    if state != '':
        good_list = good_list.filter(state=state)
        mywhere.append('state=' + state)

    # 获取商品类别名称
    for vo in good_list:
        ty = Types.objects.get(id=vo.typeid)
        vo.typename = ty.name

    # 实现分页功能
    paginator = Paginator(good_list, 10)  # 实例化Paginator, 每页显示10条数据
    page = request.GET.get('page', 1)
    Pag = paginator.page(page)

    context = {'goodslist': Pag, 'mywhere': mywhere, 'typelist': tlist}
    return render(request, 'backstage/goods/index.html', context)


def add(request):
    """添加商品信息"""
    # 获取商品类别信息
    type_list = Types.objects.extra(select={
        'path_id': 'concat(path, id)'
    }).order_by('path_id')

    for ob in type_list:
        ob.pname = '. . . ' * (ob.path.count(',') - 1)

    context = {'typelist': type_list}
    return render(request, 'backstage/goods/add.html', context)


def insert(request):
    """执行添加"""
    try:
        ob = Books()
        ob.typeid = request.POST['typeID']
        ob.author = request.POST['Author']
        ob.goods = request.POST['commodityName']
        ob.content = request.POST['productIntroduction']
        ob.addtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.novel = request.POST['Novel']
        ob.save()
        return redirect('/backstage/goods')
    except Exception as err:
        print(err)
        context = {'Info': 'Addition Failed', 'Detail': err}
        return render(request, 'backstage/info.html', context)


def edit(request, gid):
    """商品信息编辑"""
    try:
        ob = Books.objects.get(id=gid)
        context = {'goods': ob}
        return render(request, 'backstage/goods/edit.html', context)
    except Exception as err:
        print(err)
        context = {'Info': 'Cannnot fetch the page', 'Detail': err}
        return render(request, 'backstage/info.html', context)


def update(request, gid):
    """执行编辑"""
    ob = Books.objects.get(id=gid)
    ob.goods = request.POST['commodityName']
    ob.company = request.POST['Manufacturer']
    ob.price = request.POST['unitPrice']
    ob.store = request.POST['Inventory']
    ob.content = request.POST['productIntroduction']
    ob.save()
    return redirect('/backstage/goods')


def delete(request, gid):
    """商品信息删除"""
    try:
        ob = Books.objects.get(id=gid)
        ob.delete()
        return redirect('/backstage/goods')
    except Exception as err:
        print(err)
        context = {'Info': 'Delete Failed', 'Detail': err}
        return render(request, 'backstage/info.html', context)