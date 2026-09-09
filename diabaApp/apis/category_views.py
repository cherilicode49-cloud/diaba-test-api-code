from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random , calendar
from datetime import datetime, timedelta
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, F
import json
from django.http import JsonResponse
from django.db.models import Max, Min
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate

import  requests
from diabaApp.serializer import CategoryDetailSerializer, SubCategoryListSerializer, SubCategoryDetailSerializer, SuperSubCategoryDetailSerializer, \
    ProductTypeSerializer, ProductPackagingBySerializer



@csrf_exempt
def category_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    category = python_data.get('category')
    category_french = python_data.get('category_french')
    image = python_data.get('image', None)
    check_category = models.CategoryDetail.objects.filter(category = category).count()
    if check_category == 0:
        category_create = models.CategoryDetail.objects.create(
            category = category,
            category_french = category_french,
            image = image,
            status = 'Active'
            ).save()
        res = {
            'message':'Category create successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        res = {
            'message':'Category already registerd.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def category_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    id = python_data.get('id')
    category = python_data.get('category')
    category_french = python_data.get('category_french')
    image = python_data.get('image', None)
    status = python_data.get('status', None)

    check_category = models.CategoryDetail.objects.filter(id = id, category = category,category_french = category_french ).count()
    if check_category == 1:
        category_update = models.CategoryDetail.objects.get(id = id)
        category_update.category = python_data.get('category', category_update.category)
        category_update.category_french = python_data.get('category_french', category_update.category_french)
        if type(python_data.get('image')) != str:
            category_update.image = image
        category_update.status = python_data.get('status', category_update.status)
        category_update.save()
        res = {
            'message':'Category Update successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        check_category = models.CategoryDetail.objects.filter(category = category,category_french = category_french ).count()
        if check_category == 0:
            category_update = models.CategoryDetail.objects.get(id = id)
            category_update.category = python_data.get('category', category_update.category)
            category_update.category_french = python_data.get('category_french', category_update.category_french)
            if type(python_data.get('image')) != str:
                category_update.image = image
            category_update.status = python_data.get('status', category_update.status)
            category_update.save()
            res = {
                'message':'Category Update successfully.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':'Category already registerd.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def category_delete(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        category = python_data.get('id')

        check_category = models.CategoryDetail.objects.filter(id= category).count()
        if check_category == 1:
            delete_product = models.ProductDetail.objects.filter(category = category)
            delete_product.delete()
            
            delete_subcategory = models.SubCategoryDetail.objects.filter(category = category)
            delete_subcategory.delete()
            
            delete_category = models.CategoryDetail.objects.get(id = category)
            delete_category.delete()
        
            res={
                'message':'Category along with related Subcategory and Product deleted succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def category_status_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        category = python_data.get('id')
        status = python_data.get('status')

        check_category = models.CategoryDetail.objects.filter(id= category).count()
        if check_category == 1:
            if status == 'Active':
                update_category = models.CategoryDetail.objects.get(id= category)
                update_category.status = status
                update_category.save()

            elif status == 'Inactive':
                update_category = models.CategoryDetail.objects.get(id= category)
                update_category.status = status
                update_category.save()

                get_all_subcategory = models.SubCategoryDetail.objects.filter(category=category).update(status=status)
                get_all_product = models.ProductDetail.objects.filter(category=category).update(status=status)
          
            res={
                'message':'Category Status update Succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def all_category_list(request):
    all_category = models.CategoryDetail.objects.all().order_by('-id')
    serializer = CategoryDetailSerializer(all_category, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def category_with_subcategory_data(request):
    if request.method == 'POST':
        
        # all_category = models.CategoryDetail.objects.filter(status = 'Active').exclude(category='Intimate Universe and Comfort')
        all_category = models.CategoryDetail.objects.filter(status = 'Active')
        # print(all_category, 'all_category')
        list_data = []
        for category in all_category:
            check_subcategory_count = models.SubCategoryDetail.objects.filter(category = category.id).count()
            if check_subcategory_count > 0:
                category_data = models.CategoryDetail.objects.get(id = category.id) 
                category_serializer = CategoryDetailSerializer(category_data).data

                subcategory_list = models.SubCategoryDetail.objects.filter(category = category.id, status = 'Active')
                subcategory_serializer = SubCategoryListSerializer(subcategory_list, many=True).data

                category_serializer.update({'items':subcategory_serializer})
                list_data.append(category_serializer)
        
        res={
            'data':list_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def subcategory_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    category = python_data.get('category_id')
    subcategory = python_data.get('subcategory')
    subcategory_french = python_data.get('subcategory_french')
    image = python_data.get('image', None)
    check_category = models.SubCategoryDetail.objects.filter(category = category, subcategory= subcategory).count()
    # print(check_category, 'check_category', python_data)
    if check_category == 0:
        category_create = models.SubCategoryDetail.objects.create(
            category_id = category,
            subcategory = subcategory,
            subcategory_french = subcategory_french,
            image = image,
            status = 'Active'
            ).save()
        res = {
            'message':'Sub Category create successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        res = {
            'message':'Sub Category already registerd.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def subcategory_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    id = python_data.get('id')
    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    subcategory_french = python_data.get('subcategory_french')
    image = python_data.get('image', None)
    status = python_data.get('status', None)

    check_subcategory = models.SubCategoryDetail.objects.filter(id = id, category = category, subcategory = subcategory, subcategory_french = subcategory_french ).count()
    if check_subcategory == 1:
        subcategory_update = models.SubCategoryDetail.objects.get(id = id)
        subcategory_update.category_id = python_data.get('category', subcategory_update.category)
        subcategory_update.subcategory = python_data.get('subcategory', subcategory_update.subcategory)
        subcategory_update.subcategory_french = python_data.get('subcategory_french', subcategory_update.subcategory_french)
        if type(python_data.get('image')) != str:
            subcategory_update.image = image
        subcategory_update.status = python_data.get('status', subcategory_update.status)
        subcategory_update.save()
        res = {
            'message':'Subcategory Update successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        check_subcategory = models.SubCategoryDetail.objects.filter(category = category, subcategory = subcategory, subcategory_french = subcategory_french).count()
        if check_subcategory == 0:
            subcategory_update = models.SubCategoryDetail.objects.get(id = id)
            subcategory_update.category_id = python_data.get('category', subcategory_update.category)
            subcategory_update.subcategory = python_data.get('subcategory', subcategory_update.subcategory)
            subcategory_update.subcategory_french = python_data.get('subcategory_french', subcategory_update.subcategory_french)
            if type(python_data.get('image')) != str:
                subcategory_update.image = image
            subcategory_update.status = python_data.get('status', subcategory_update.status)
            subcategory_update.save()
            res = {
                'message':'Subcategory Update successfully.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':'Subcategory already registerd.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def subcategory_delete(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        subcategory = python_data.get('id')

        check_category = models.SubCategoryDetail.objects.filter(id= subcategory).count()
        if check_category == 1:
            delete_product = models.ProductDetail.objects.filter(subcategory = subcategory)
            delete_product.delete()
            
            delete_subcategory = models.SubCategoryDetail.objects.get(id = subcategory)
            delete_subcategory.delete()
            
            res={
                'message':'Subcategory along with related Product deleted succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def subcategory_status_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        subcategory = python_data.get('id')
        status = python_data.get('status')

        check_category = models.SubCategoryDetail.objects.filter(id= subcategory).count()
        if check_category == 1:
            if status == 'Active':
                update_category = models.SubCategoryDetail.objects.get(id= subcategory)
                update_category.status = status
                update_category.save()

            elif status == 'Inactive':
                update_category = models.SubCategoryDetail.objects.get(id= subcategory)
                update_category.status = status
                update_category.save()

                get_all_product = models.ProductDetail.objects.filter(subcategory=subcategory).update(status=status)
          
            res={
                'message':'Subcategory Status update Succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)        

        
@csrf_exempt
def all_subcategory_list(request):
    all_category = models.SubCategoryDetail.objects.all().order_by('-id')
    serializer = SubCategoryDetailSerializer(all_category, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def super_subcategory_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    category = python_data.get('category_id')
    subcategory = python_data.get('subcategory_id')
    super_subcategory = python_data.get('super_subcategory')
    image = python_data.get('image', None)
    check_category = models.SuperSubCategoryDetail.objects.filter(category = category, subcategory= subcategory, super_subcategory= super_subcategory).count()
    if check_category == 0:
        category_create = models.SuperSubCategoryDetail.objects.create(
            category_id = category,
            subcategory_id = subcategory,
            super_subcategory = super_subcategory,
            image = image,
            status = 'Active'
            ).save()
        res = {
            'message':'Super Sub Category create successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        res = {
            'message':'Super Sub Category already registerd.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def all_super_subcategory_list(request):
    all_super_category = models.SuperSubCategoryDetail.objects.all()
    serializer = SuperSubCategoryDetailSerializer(all_super_category, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def product_type_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        product_type = python_data.get('product_type')
        
        if models.ProductType.objects.filter(product_type = product_type).count() == 0:
            create = models.ProductType.objects.create(
                product_type = product_type
            ).save()
            res = {
                'message':'Product Type Added succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something Went Wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def product_type_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        product_type = python_data.get('product_type')
        
        if models.ProductType.objects.filter(product_type=product_type, id = id).count() == 1:
            res = {
                'message':'Type update succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        elif models.ProductType.objects.filter(product_type=product_type).count() != 0:
            res = {
                'message':'Type already added.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        else:
            type_count = models.ProductType.objects.filter(product_type=product_type).count()
            if type_count == 0:
                type_update = models.ProductType.objects.get(id = id)
                type_update.product_type = product_type 
                type_update.save()
                res = {
                    'message':'Type update succesfully.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
            else:
                res = {
                    'message':'Something Went Wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def product_type_list(request):
    if request.method == "POST":

        all_type = models.ProductType.objects.all()
        serialiser = ProductTypeSerializer(all_type, many=True).data
        
        res = {
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def product_packaging_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        product_packaging = python_data.get('product_packaging')
        
        if models.ProductPackagingBy.objects.filter(product_packaging = product_packaging).count() == 0:
            create = models.ProductPackagingBy.objects.create(
                product_packaging = product_packaging
            ).save()
            res = {
                'message':'Product Type Added succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something Went Wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def product_packaging_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        product_packaging = python_data.get('product_packaging')
        
        if models.ProductPackagingBy.objects.filter(product_packaging=product_packaging, id = id).count() == 1:
            res = {
                'message':'Type update succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        elif models.ProductPackagingBy.objects.filter(product_packaging=product_packaging).count() != 0:
            res = {
                'message':'Type already added.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        else:
            type_count = models.ProductPackagingBy.objects.filter(product_packaging=product_packaging).count()
            if type_count == 0:
                type_update = models.ProductPackagingBy.objects.get(id = id)
                type_update.product_packaging = product_packaging 
                type_update.save()
                res = {
                    'message':'Type update succesfully.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
            else:
                res = {
                    'message':'Something Went Wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def product_packaging_list(request):
    if request.method == "POST":

        all_type = models.ProductPackagingBy.objects.all()
        serialiser = ProductPackagingBySerializer(all_type, many=True).data
        
        res = {
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
