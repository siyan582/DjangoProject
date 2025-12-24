import json
import time
import random
from datetime import datetime
from django.db import transaction, IntegrityError
from django.db.models import Q, ProtectedError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import *


# ==========================================
# 通用工具：简单删除处理
# ==========================================
def handle_delete(model_class, obj_id):
    try:
        obj = model_class.objects.get(id=obj_id)
        obj.delete()
        return JsonResponse({"code": 200, "message": "删除成功"})
    except model_class.DoesNotExist:
        return JsonResponse({"code": 404, "message": "数据不存在"})
    except ProtectedError:
        return JsonResponse({"code": 403, "message": "无法删除：该数据被其他记录引用"})
    except Exception as e:
        return JsonResponse({"code": 500, "message": str(e)})


# ==========================================
# 1. 基础资料接口
# ==========================================
@csrf_exempt
def enterprise_info(request):
    if request.method == 'GET':
        obj = Enterprise.objects.first()
        data = None
        if obj:
            data = {
                "name": obj.name, "type": obj.type,
                "registered_capital": obj.registered_capital,
                "establish_date": obj.establish_date,
                "industry": obj.industry, "tax_no": obj.tax_no
            }
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        data = json.loads(request.body)

        # === 关键修复：处理空日期字符串 ===
        # 如果前端传过来的是空字符串 ""，强行改成 None，这样数据库就能接受了
        if data.get('establish_date') == "":
            data['establish_date'] = None
        # ==============================

        Enterprise.objects.update_or_create(id=1, defaults=data)
        return JsonResponse({"code": 200, "message": "保存成功"})


# finance/views.py

@csrf_exempt
def supplier_list(request):
    if request.method == 'GET':
        objs = Supplier.objects.all().order_by('-create_time')
        data = [{
            "id": o.id,
            "name": o.name,
            "contact": o.contact,
            "phone": o.phone,
            "address": o.address,
            # [新增] 返回新增字段
            "bank_account": o.bank_account,
            "default_credit_period": o.default_credit_period,
            "remark": o.remark
        } for o in objs]
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        Supplier.objects.create(**json.loads(request.body))
        return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        try:
            obj = Supplier.objects.get(id=data['id'])
            obj.name = data['name']
            obj.contact = data.get('contact', '')
            obj.phone = data.get('phone', '')
            obj.address = data.get('address', '')
            # [新增] 更新新增字段
            obj.bank_account = data.get('bank_account', '')
            obj.default_credit_period = data.get('default_credit_period', 0)

            obj.remark = data.get('remark', '')
            obj.save()
            return JsonResponse({"code": 200, "message": "修改成功"})
        except Supplier.DoesNotExist:
            return JsonResponse({"code": 404, "message": "数据不存在"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})

    elif request.method == 'DELETE':
        return handle_delete(Supplier, request.GET.get('id'))


@csrf_exempt
def customer_list(request):
    if request.method == 'GET':
        objs = Customer.objects.all().order_by('-create_time')
        data = [{
            "id": o.id,
            "name": o.name,
            "contact": o.contact,
            "phone": o.phone,
            "address": o.address,
            # [新增] 返回新增字段
            "default_credit_period": o.default_credit_period,
            "remark": o.remark
        } for o in objs]
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        Customer.objects.create(**json.loads(request.body))
        return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        try:
            obj = Customer.objects.get(id=data['id'])
            obj.name = data['name']
            obj.contact = data.get('contact', '')
            obj.phone = data.get('phone', '')
            obj.address = data.get('address', '')
            # [新增] 更新新增字段
            obj.default_credit_period = data.get('default_credit_period', 0)

            obj.remark = data.get('remark', '')
            obj.save()
            return JsonResponse({"code": 200, "message": "修改成功"})
        except Customer.DoesNotExist:
            return JsonResponse({"code": 404, "message": "数据不存在"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})

    elif request.method == 'DELETE':
        return handle_delete(Customer, request.GET.get('id'))


# ==========================================
# 2. 会计科目
# ==========================================
@csrf_exempt
def account_subject_list(request):
    if request.method == 'GET':
        objs = AccountSubject.objects.all().order_by('code')
        data = []
        for o in objs:
            data.append({
                "id": o.id, "code": o.code, "name": o.name,
                "type": o.get_type_display(),
                "type_code": o.type,
                "direction": o.get_balance_direction_display(),
                "parent_id": o.parent_id
            })
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        data = json.loads(request.body)
        if data.get('action') == 'init':
            defaults = [
                {'code': '1001', 'name': '库存现金', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1002', 'name': '银行存款', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1122', 'name': '应收账款', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1123', 'name': '预付账款', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1221', 'name': '其他应收款', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1403', 'name': '原材料', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1405', 'name': '库存商品', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '1601', 'name': '固定资产', 'type': 'ASSET', 'balance_direction': 'DEBIT'},
                {'code': '2001', 'name': '短期借款', 'type': 'LIABILITY', 'balance_direction': 'CREDIT'},
                {'code': '2202', 'name': '应付账款', 'type': 'LIABILITY', 'balance_direction': 'CREDIT'},
                {'code': '2203', 'name': '预收账款', 'type': 'LIABILITY', 'balance_direction': 'CREDIT'},
                {'code': '2211', 'name': '应付职工薪酬', 'type': 'LIABILITY', 'balance_direction': 'CREDIT'},
                {'code': '2221', 'name': '应交税费', 'type': 'LIABILITY', 'balance_direction': 'CREDIT'},
                {'code': '4001', 'name': '实收资本', 'type': 'EQUITY', 'balance_direction': 'CREDIT'},
                {'code': '4002', 'name': '资本公积', 'type': 'EQUITY', 'balance_direction': 'CREDIT'},
                {'code': '4103', 'name': '本年利润', 'type': 'EQUITY', 'balance_direction': 'CREDIT'},
                {'code': '4104', 'name': '利润分配', 'type': 'EQUITY', 'balance_direction': 'CREDIT'},
                {'code': '5001', 'name': '生产成本', 'type': 'COST', 'balance_direction': 'DEBIT'},
                {'code': '5101', 'name': '制造费用', 'type': 'COST', 'balance_direction': 'DEBIT'},
                {'code': '6001', 'name': '主营业务收入', 'type': 'PROFIT_LOSS', 'balance_direction': 'CREDIT'},
                {'code': '6051', 'name': '其他业务收入', 'type': 'PROFIT_LOSS', 'balance_direction': 'CREDIT'},
                {'code': '6401', 'name': '主营业务成本', 'type': 'PROFIT_LOSS', 'balance_direction': 'DEBIT'},
                {'code': '6601', 'name': '销售费用', 'type': 'PROFIT_LOSS', 'balance_direction': 'DEBIT'},
                {'code': '6602', 'name': '管理费用', 'type': 'PROFIT_LOSS', 'balance_direction': 'DEBIT'},
                {'code': '6603', 'name': '财务费用', 'type': 'PROFIT_LOSS', 'balance_direction': 'DEBIT'},
            ]
            added_count = 0
            for item in defaults:
                obj, created = AccountSubject.objects.get_or_create(
                    code=item['code'],
                    defaults={'name': item['name'], 'type': item['type'],
                              'balance_direction': item['balance_direction']}
                )
                if created: added_count += 1
            return JsonResponse({"code": 200, "message": f"初始化完成，已补全 {added_count} 个科目"})
        else:
            AccountSubject.objects.create(
                code=data['code'], name=data['name'],
                type=data['type'], balance_direction=data['balance_direction'],
                parent_id=data.get('parent_id')
            )
            return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'DELETE':
        return handle_delete(AccountSubject, request.GET.get('id'))


# ==========================================
# 3. 采购订单 (新增修改与级联删除)
# ==========================================
@csrf_exempt
def purchase_order_list(request):
    if request.method == 'GET':
        objs = PurchaseOrder.objects.select_related('supplier').prefetch_related(
            'items__expense_subject').all().order_by('-create_time')
        data = []
        for obj in objs:
            items = [{
                "product_name": i.product_name,
                "quantity": i.quantity,
                "price": i.price,
                "tax_rate": i.tax_rate,  # [新增]
                "subject_id": i.expense_subject_id,  # [新增]
                "subject_name": i.expense_subject.name if i.expense_subject else "",
                "amount": i.amount,
                "remark": i.remark
            } for i in obj.items.all()]

            data.append({
                "id": obj.id,
                "order_no": obj.order_no,
                "supplier_id": obj.supplier.id,
                "supplier_name": obj.supplier.name,
                "purchase_date": obj.purchase_date.strftime('%Y-%m-%d'),
                "total_amount": obj.total_amount,
                "status": "已审核",  # 简化处理
                "is_posted": obj.is_posted,
                "is_settled": obj.is_settled,
                "credit_period": obj.credit_period,
                "items": items
            })
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        data = json.loads(request.body)
        with transaction.atomic():
            order = PurchaseOrder.objects.create(
                order_no=f"PO{time.strftime('%Y%m%d%H%M%S')}{random.randint(10, 99)}",
                supplier_id=data['supplier_id'],
                purchase_date=data['purchase_date'],
                credit_period=data.get('credit_period', 0),
                status='APPROVED'
            )
            total = 0
            for item in data['items']:
                # 计算含税金额：数量 * 单价 * (1 + 税率)
                rate = float(item.get('tax_rate', 0))
                amt = float(item['quantity']) * float(item['price']) * (1 + rate)
                total += amt

                PurchaseOrderItem.objects.create(
                    order=order,
                    product_name=item['product_name'],
                    expense_subject_id=item.get('subject_id'),  # [新增] 保存科目
                    quantity=item['quantity'],
                    price=item['price'],
                    tax_rate=rate,  # [新增] 保存税率
                    amount=amt,
                    remark=item.get('remark', '')
                )
            order.total_amount = total
            order.save()
        return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        order_id = data.get('id')
        with transaction.atomic():
            try:
                order = PurchaseOrder.objects.get(id=order_id)
                if order.is_posted or order.is_settled:
                    return JsonResponse({"code": 403, "message": "订单已过账或已付款，禁止修改！"})

                order.supplier_id = data['supplier_id']
                order.purchase_date = data['purchase_date']
                order.credit_period = data.get('credit_period', 0)

                order.items.all().delete()
                total = 0
                for item in data['items']:
                    rate = float(item.get('tax_rate', 0))
                    amt = float(item['quantity']) * float(item['price']) * (1 + rate)
                    total += amt

                    PurchaseOrderItem.objects.create(
                        order=order,
                        product_name=item['product_name'],
                        expense_subject_id=item.get('subject_id'),  # [新增]
                        quantity=item['quantity'],
                        price=item['price'],
                        tax_rate=rate,  # [新增]
                        amount=amt,
                        remark=item.get('remark', '')
                    )
                order.total_amount = total
                order.save()
                return JsonResponse({"code": 200, "message": "修改成功"})
            except PurchaseOrder.DoesNotExist:
                return JsonResponse({"code": 404, "message": "订单不存在"})
            except Exception as e:
                return JsonResponse({"code": 500, "message": str(e)})

    elif request.method == 'DELETE':
        # 保持之前的级联删除逻辑不变
        o_id = request.GET.get('id')
        try:
            with transaction.atomic():
                order = PurchaseOrder.objects.get(id=o_id)
                AccountingVoucher.objects.filter(source_document=order.order_no).delete()
                related_payments = PaymentRecord.objects.filter(purchase_order=order)
                for pay in related_payments:
                    AccountingVoucher.objects.filter(source_document=pay.payment_no).delete()
                related_payments.delete()
                order.delete()
            return JsonResponse({"code": 200, "message": "删除成功"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


# ==========================================
# 4. 销售订单 (支持修改 + 级联删除)
# ==========================================
# finance/views.py

@csrf_exempt
def sales_order_list(request):
    if request.method == 'GET':
        objs = SalesOrder.objects.select_related('customer').prefetch_related('items__income_subject').all().order_by(
            '-create_time')
        data = []
        for obj in objs:
            items = [{
                "product_name": i.product_name,
                "quantity": i.quantity,
                "price": i.price,
                "tax_rate": i.tax_rate,  # [新增]
                "subject_id": i.income_subject_id,  # [新增]
                "subject_name": i.income_subject.name if i.income_subject else "",
                "amount": i.amount,
                "remark": i.remark
            } for i in obj.items.all()]

            data.append({
                "id": obj.id,
                "order_no": obj.order_no,
                "customer_id": obj.customer.id,
                "customer_name": obj.customer.name,
                "sales_date": obj.sales_date.strftime('%Y-%m-%d'),
                "total_amount": obj.total_amount,
                "status": obj.status,
                "is_posted": obj.is_posted,
                "is_settled": obj.is_settled,
                "credit_period": obj.credit_period,
                "items": items
            })
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        data = json.loads(request.body)
        with transaction.atomic():
            order = SalesOrder.objects.create(
                order_no=f"SO{time.strftime('%Y%m%d%H%M%S')}{random.randint(10, 99)}",
                customer_id=data['customer_id'],
                sales_date=data['sales_date'],
                credit_period=data.get('credit_period', 0),
                status='APPROVED'
            )
            total = 0
            for item in data['items']:
                rate = float(item.get('tax_rate', 0))
                amt = float(item['quantity']) * float(item['price']) * (1 + rate)
                total += amt

                SalesOrderItem.objects.create(
                    order=order,
                    product_name=item['product_name'],
                    income_subject_id=item.get('subject_id'),  # [新增]
                    quantity=item['quantity'],
                    price=item['price'],
                    tax_rate=rate,  # [新增]
                    amount=amt,
                    remark=item.get('remark', '')
                )
            order.total_amount = total
            order.save()
        return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        with transaction.atomic():
            try:
                order = SalesOrder.objects.get(id=data['id'])
                if order.is_posted or order.is_settled:
                    return JsonResponse({"code": 403, "message": "订单已过账或已收款，禁止修改！"})

                order.customer_id = data['customer_id']
                order.sales_date = data['sales_date']
                order.credit_period = data.get('credit_period', 0)

                order.items.all().delete()
                total = 0
                for item in data['items']:
                    rate = float(item.get('tax_rate', 0))
                    amt = float(item['quantity']) * float(item['price']) * (1 + rate)
                    total += amt

                    SalesOrderItem.objects.create(
                        order=order,
                        product_name=item['product_name'],
                        income_subject_id=item.get('subject_id'),  # [新增]
                        quantity=item['quantity'],
                        price=item['price'],
                        tax_rate=rate,  # [新增]
                        amount=amt,
                        remark=item.get('remark', '')
                    )
                order.total_amount = total
                order.save()
                return JsonResponse({"code": 200, "message": "修改成功"})
            except SalesOrder.DoesNotExist:
                return JsonResponse({"code": 404, "message": "订单不存在"})

    elif request.method == 'DELETE':
        # 保持之前的级联删除逻辑不变
        o_id = request.GET.get('id')
        try:
            with transaction.atomic():
                order = SalesOrder.objects.get(id=o_id)
                AccountingVoucher.objects.filter(source_document=order.order_no).delete()
                related_cols = CollectionRecord.objects.filter(related_order=order)
                for col in related_cols:
                    AccountingVoucher.objects.filter(source_document=col.collection_no).delete()
                related_cols.delete()
                order.delete()
            return JsonResponse({"code": 200, "message": "删除成功"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


# ==========================================
# 5. 凭证生成 (包含状态联动)
# ==========================================
# finance/views.py

# finance/views.py

@csrf_exempt
def generate_voucher(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            order_type = data.get('type')
            row_list = data.get('rows')
            remark = data.get('remark', '')
            voucher_date = data.get('date', timezone.now().strftime('%Y-%m-%d'))

            with transaction.atomic():
                # === 【安全锁】防止重复生成 ===
                if order_type == 'COLLECTION':
                    obj = CollectionRecord.objects.select_for_update().get(id=order_id)
                    if obj.status == 'POSTED':
                        return JsonResponse({"code": 400, "message": "该收款单已过账，请勿重复操作！"})
                elif order_type == 'PAYMENT':
                    obj = PaymentRecord.objects.select_for_update().get(id=order_id)
                    if obj.is_settled: # 或 check status == 'POSTED'
                        return JsonResponse({"code": 400, "message": "该付款单已过账，请勿重复操作！"})
                elif order_type == 'SALES':
                    obj = SalesOrder.objects.select_for_update().get(id=order_id)
                    if obj.is_posted:
                        return JsonResponse({"code": 400, "message": "该销售单已过账！"})
                elif order_type == 'PURCHASE':
                    obj = PurchaseOrder.objects.select_for_update().get(id=order_id)
                    if obj.is_posted:
                        return JsonResponse({"code": 400, "message": "该采购单已过账！"})
                # ============================

                # 1. 创建凭证主表
                voucher = AccountingVoucher.objects.create(
                    voucher_no=f"PZ-{time.strftime('%Y%m%d')}-{random.randint(100, 999)}",
                    creator="会计",
                    remark=remark,
                    voucher_date=voucher_date,
                    source_document=''
                )
                # 2. 创建分录
                for row in row_list:
                    VoucherDetail.objects.create(
                        voucher=voucher,
                        summary=row.get('summary'),
                        subject_id=row.get('subject_id'),
                        debit_amount=row.get('debit', 0),
                        credit_amount=row.get('credit', 0)
                    )

                # 3. 状态联动
                source_no = ""
                if order_type == 'SALES':
                    obj = SalesOrder.objects.get(id=order_id)
                    obj.is_posted = True
                    obj.save()
                    source_no = obj.order_no

                elif order_type == 'PURCHASE':
                    obj = PurchaseOrder.objects.get(id=order_id)
                    obj.is_posted = True
                    obj.save()
                    source_no = obj.order_no

                elif order_type == 'COLLECTION':
                    obj = CollectionRecord.objects.get(id=order_id)
                    obj.status = 'POSTED'
                    obj.related_voucher = voucher
                    obj.save()
                    source_no = obj.collection_no
                    if obj.related_order:
                        obj.related_order.is_settled = True
                        obj.related_order.save()

                elif order_type == 'PAYMENT':
                    obj = PaymentRecord.objects.get(id=order_id)
                    obj.status = 'POSTED'
                    obj.is_settled = True
                    obj.related_voucher = voucher
                    obj.save()
                    source_no = obj.payment_no
                    if obj.purchase_order:
                        obj.purchase_order.is_settled = True
                        obj.purchase_order.save()

                elif order_type == 'MANUAL':
                    source_no = "手动录入"

                voucher.source_document = source_no
                voucher.save()

            return JsonResponse({"code": 200, "message": "凭证生成成功"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


@csrf_exempt
def voucher_list(request):
    if request.method == 'GET':
        # ... (GET 逻辑保持不变) ...
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        subject_kw = request.GET.get('subject')
        remark_kw = request.GET.get('remark')
        qs = AccountingVoucher.objects.prefetch_related('details__subject').all()
        if start_date: qs = qs.filter(voucher_date__gte=start_date)
        if end_date: qs = qs.filter(voucher_date__lte=end_date)
        if remark_kw: qs = qs.filter(remark__icontains=remark_kw)
        if subject_kw: qs = qs.filter(details__subject__name__icontains=subject_kw).distinct()
        qs = qs.order_by('-voucher_date', '-create_time')
        data = []
        for v in qs:
            details = [{
                "summary": d.summary,
                "subject_name": f"{d.subject.code} {d.subject.name}",
                "debit": d.debit_amount,
                "credit": d.credit_amount
            } for d in v.details.all()]
            data.append({
                "id": v.id,
                "voucher_no": v.voucher_no,
                "date": v.voucher_date,
                "source": v.source_document,
                "remark": v.remark,
                "details": details
            })
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'DELETE':
        # === 凭证删除的回滚逻辑 ===
        v_id = request.GET.get('id')
        try:
            with transaction.atomic():
                voucher = AccountingVoucher.objects.get(id=v_id)
                source = voucher.source_document

                # 1. 销售单凭证删除 -> 回滚 SalesOrder.is_posted
                if source and source.startswith('SO'):
                    SalesOrder.objects.filter(order_no=source).update(is_posted=False)

                # 2. 采购单凭证删除 -> 回滚 PurchaseOrder.is_posted
                elif source and source.startswith('PO'):
                    PurchaseOrder.objects.filter(order_no=source).update(is_posted=False)

                # 3. 收款凭证删除 -> 回滚 CollectionRecord 和 SalesOrder
                elif source and source.startswith('COL'):
                    cols = CollectionRecord.objects.filter(collection_no=source)
                    for c in cols:
                        c.status = 'CREATED'  # 回滚状态
                        c.related_voucher = None
                        c.save()
                        # 回滚关联订单状态
                        if c.related_order:
                            c.related_order.is_settled = False
                            c.related_order.save()

                # 4. 付款凭证删除 -> 回滚 PaymentRecord 和 PurchaseOrder
                elif source and source.startswith('PAY'):
                    pays = PaymentRecord.objects.filter(payment_no=source)
                    for p in pays:
                        p.is_settled = False  # 回滚状态
                        p.status = 'CREATED'
                        p.related_voucher = None
                        p.save()
                        # 回滚关联订单状态
                        if p.purchase_order:
                            p.purchase_order.is_settled = False
                            p.purchase_order.save()

                # 最后删除凭证
                voucher.delete()
            return JsonResponse({"code": 200, "message": "删除成功，相关单据状态已回滚"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


# ==========================================
# 6. 资金收付 (付款单/收款单)
# ==========================================
@csrf_exempt
def payment_list(request):
    if request.method == 'GET':
        objs = PaymentRecord.objects.select_related('supplier', 'purchase_order', 'payment_method_subject').all()
        data = [{
            "id": o.id,
            "payment_no": o.payment_no,
            "supplier_name": o.supplier.name if o.supplier else '',
            "purchase_order_no": o.purchase_order.order_no if o.purchase_order else '',
            "payment_date": o.pay_date.strftime('%Y-%m-%d'),
            "amount": o.amount,
            "remark": o.remark,
            "is_settled": o.is_settled,
            # 【建议】虽然前端主要用 is_settled，但为了统一，也返回原始 status
            "status": o.status
        } for o in objs]
        return JsonResponse({"code": 200, "data": data})

    # ... (POST 和 DELETE 保持不变，不需要修改) ...
    elif request.method == 'POST':
        data = json.loads(request.body)
        with transaction.atomic():
            payment_no = f"PAY{time.strftime('%Y%m%d%H%M%S')}{random.randint(10, 99)}"
            PaymentRecord.objects.create(
                payment_no=payment_no,
                supplier_id=data['supplier_id'],
                purchase_order_id=data.get('purchase_order_id'),
                pay_date=data['payment_date'],
                amount=data['amount'],
                payment_method_subject_id=data['payment_method_subject_id'],
                remark=data.get('remark', ''),
                is_settled=False,
                status='CREATED'
            )
        return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'DELETE':
        try:
            p_id = request.GET.get('id')
            with transaction.atomic():
                pay = PaymentRecord.objects.get(id=p_id)
                if pay.payment_no:
                    vouchers = AccountingVoucher.objects.filter(source_document=pay.payment_no)
                    vouchers.delete()
                if pay.purchase_order:
                    pay.purchase_order.is_settled = False
                    pay.purchase_order.save()
                pay.delete()
            return JsonResponse({"code": 200, "message": "删除成功"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


@csrf_exempt
def collection_list(request):
    if request.method == 'GET':
        objs = CollectionRecord.objects.select_related('customer', 'related_order').all().order_by('-create_time')
        data = [{
            "id": o.id,
            "collection_no": o.collection_no,
            "customer_name": o.customer.name,
            "order_no": o.related_order.order_no if o.related_order else "-",
            "amount": o.amount,
            "date": o.collect_date.strftime('%Y-%m-%d'),
            # 【核心修复】这里直接返回原始状态码 o.status (CREATED/POSTED)，不要转中文
            "status": o.status,
            "remark": o.remark
        } for o in objs]
        return JsonResponse({"code": 200, "data": data})

    elif request.method == 'POST':
        # ... (POST 逻辑保持不变)
        data = json.loads(request.body)
        with transaction.atomic():
            CollectionRecord.objects.create(
                collection_no=f"COL{time.strftime('%Y%m%d%H%M%S')}",
                customer_id=data['customer_id'],
                related_order_id=data.get('order_id'),
                amount=data['amount'],
                collect_date=data['date'],
                remark=data.get('remark', ''),
                status='CREATED'
            )
        return JsonResponse({"code": 200, "message": "保存成功"})

    elif request.method == 'DELETE':
        # ... (DELETE 逻辑保持不变)
        c_id = request.GET.get('id')
        try:
            with transaction.atomic():
                col = CollectionRecord.objects.get(id=c_id)
                if col.collection_no:
                    AccountingVoucher.objects.filter(source_document=col.collection_no).delete()
                if col.related_order:
                    col.related_order.is_settled = False
                    col.related_order.save()
                col.delete()
            return JsonResponse({"code": 200, "message": "删除成功"})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


# ==========================================
# 7. 报表接口 (保持不变)
# ==========================================
@csrf_exempt
def trial_balance(request):
    if request.method == 'GET':
        subjects = AccountSubject.objects.all().order_by('code')
        data = []
        total_debit = 0
        total_credit = 0
        for sub in subjects:
            details = VoucherDetail.objects.filter(subject=sub)
            current_debit = sum(d.debit_amount for d in details)
            current_credit = sum(d.credit_amount for d in details)
            balance = 0
            if sub.balance_direction == 'DEBIT':
                balance = current_debit - current_credit
            else:
                balance = current_credit - current_debit
            if current_debit != 0 or current_credit != 0 or balance != 0:
                data.append({
                    "code": sub.code,
                    "name": sub.name,
                    "direction": sub.get_balance_direction_display(),
                    "period_debit": current_debit,
                    "period_credit": current_credit,
                    "end_balance": balance
                })
                total_debit += current_debit
                total_credit += current_credit
        return JsonResponse({
            "code": 200,
            "data": {
                "rows": data,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "is_balanced": total_debit == total_credit
            }
        })


@csrf_exempt
def balance_sheet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            current_date = datetime.strptime(date_str, '%Y-%m-%d')
            year_start_str = f"{current_date.year}-01-01"
            subjects = AccountSubject.objects.all().order_by('code')
            assets = []
            liabilities = []
            equity = []
            total_asset_end = 0;
            total_asset_begin = 0
            total_liab_end = 0;
            total_liab_begin = 0
            total_equity_end = 0;
            total_equity_begin = 0

            def get_balance_at(sub_obj, deadline_str):
                details = VoucherDetail.objects.filter(subject=sub_obj, voucher__voucher_date__lte=deadline_str)
                d = sum(x.debit_amount for x in details)
                c = sum(x.credit_amount for x in details)
                if sub_obj.type in ['ASSET', 'COST']:
                    return d - c
                else:
                    return c - d

            for sub in subjects:
                end_bal = get_balance_at(sub, date_str)
                begin_bal = get_balance_at(sub, year_start_str)
                item = {"code": sub.code, "name": sub.name, "closing_balance": end_bal, "opening_balance": begin_bal}
                if sub.type == 'ASSET':
                    assets.append(item)
                    total_asset_end += end_bal
                    total_asset_begin += begin_bal
                elif sub.type == 'LIABILITY':
                    liabilities.append(item)
                    total_liab_end += end_bal
                    total_liab_begin += begin_bal
                elif sub.type == 'EQUITY':
                    equity.append(item)
                    total_equity_end += end_bal
                    total_equity_begin += begin_bal

            profit_loss_subs = AccountSubject.objects.filter(Q(type='PROFIT_LOSS') | Q(type='COST'))
            net_profit_end = 0;
            net_profit_begin = 0
            for sub in profit_loss_subs:
                details_end = VoucherDetail.objects.filter(subject=sub, voucher__voucher_date__lte=date_str)
                d_end = sum(x.debit_amount for x in details_end)
                c_end = sum(x.credit_amount for x in details_end)
                details_begin = VoucherDetail.objects.filter(subject=sub, voucher__voucher_date__lte=year_start_str)
                d_begin = sum(x.debit_amount for x in details_begin)
                c_begin = sum(x.credit_amount for x in details_begin)
                net_profit_end += (c_end - d_end)
                net_profit_begin += (c_begin - d_begin)

            equity.append({"code": "9999", "name": "未分配利润(本年净利)", "closing_balance": net_profit_end,
                           "opening_balance": net_profit_begin})
            total_equity_end += net_profit_end
            total_equity_begin += net_profit_begin

            return JsonResponse({
                "code": 200,
                "data": {
                    "assets": assets,
                    "liabilities_equity": liabilities + equity,
                    "total_asset_end": total_asset_end,
                    "total_asset_begin": total_asset_begin,
                    "total_le_end": total_liab_end + total_equity_end,
                    "total_le_begin": total_liab_begin + total_equity_begin,
                    "is_balanced": abs(total_asset_end - (total_liab_end + total_equity_end)) < 0.01
                }
            })
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


@csrf_exempt
def income_statement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            subjects = AccountSubject.objects.filter(Q(type='PROFIT_LOSS') | Q(type='COST')).order_by('code')
            rows = []
            total_income = 0
            total_cost = 0
            for sub in subjects:
                details = VoucherDetail.objects.filter(subject=sub, voucher__voucher_date__gte=start_date,
                                                       voucher__voucher_date__lte=end_date)
                d = sum(x.debit_amount for x in details)
                c = sum(x.credit_amount for x in details)
                amount = 0
                if sub.balance_direction == 'CREDIT':
                    amount = c - d
                    total_income += amount
                else:
                    amount = d - c
                    total_cost += amount
                rows.append({"code": sub.code, "name": sub.name, "amount": amount,
                             "type": "收入" if sub.balance_direction == 'CREDIT' else "费用"})
            return JsonResponse({"code": 200,
                                 "data": {"rows": rows, "total_income": total_income, "total_cost": total_cost,
                                          "net_profit": total_income - total_cost}})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})


@csrf_exempt
def cash_flow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        cash_subjects = AccountSubject.objects.filter(code__in=['1001', '1002'])
        opening_balance = 0
        for sub in cash_subjects:
            prev_details = VoucherDetail.objects.filter(subject=sub, voucher__voucher_date__lt=start_date)
            d = sum(x.debit_amount for x in prev_details)
            c = sum(x.credit_amount for x in prev_details)
            opening_balance += (d - c)
        inflow = 0;
        outflow = 0;
        rows = []
        details = VoucherDetail.objects.filter(subject__in=cash_subjects, voucher__voucher_date__gte=start_date,
                                               voucher__voucher_date__lte=end_date).order_by('voucher__voucher_date')
        for d in details:
            if d.debit_amount > 0:
                inflow += d.debit_amount
                rows.append(
                    {"date": d.voucher.voucher_date, "type": "流入", "desc": d.summary, "amount": d.debit_amount})
            if d.credit_amount > 0:
                outflow += d.credit_amount
                rows.append(
                    {"date": d.voucher.voucher_date, "type": "流出", "desc": d.summary, "amount": d.credit_amount})
        net_change = inflow - outflow
        closing_balance = opening_balance + net_change
        return JsonResponse({
            "code": 200,
            "data": {
                "opening_balance": opening_balance,
                "inflow": inflow,
                "outflow": outflow,
                "net_change": net_change,
                "closing_balance": closing_balance,
                "rows": rows
            }
        })


# finance/views.py (追加到文件末尾)

# ==========================================
# 8. 首页仪表盘聚合接口
# ==========================================
@csrf_exempt
def dashboard_stats(request):
    if request.method == 'GET':
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)

        # 1. 获取企业名称
        ent = Enterprise.objects.first()
        company_name = ent.name if ent else "未命名企业"

        # 2. 计算资金余额 (现金1001 + 银行存款1002)
        # 逻辑：借方总额 - 贷方总额
        cash_subjects = AccountSubject.objects.filter(code__in=['1001', '1002'])
        details = VoucherDetail.objects.filter(subject__in=cash_subjects)
        debit = details.aggregate(sum=models.Sum('debit_amount'))['sum'] or 0
        credit = details.aggregate(sum=models.Sum('credit_amount'))['sum'] or 0
        total_cash = debit - credit

        # 3. 计算应收账款余额 (1122) - 资产类：借-贷
        rec_sub = AccountSubject.objects.filter(code='1122').first()
        total_receivable = 0
        if rec_sub:
            rec_details = VoucherDetail.objects.filter(subject=rec_sub)
            r_debit = rec_details.aggregate(sum=models.Sum('debit_amount'))['sum'] or 0
            r_credit = rec_details.aggregate(sum=models.Sum('credit_amount'))['sum'] or 0
            total_receivable = r_debit - r_credit

        # 4. 计算应付账款余额 (2202) - 负债类：贷-借
        pay_sub = AccountSubject.objects.filter(code='2202').first()
        total_payable = 0
        if pay_sub:
            pay_details = VoucherDetail.objects.filter(subject=pay_sub)
            p_debit = pay_details.aggregate(sum=models.Sum('debit_amount'))['sum'] or 0
            p_credit = pay_details.aggregate(sum=models.Sum('credit_amount'))['sum'] or 0
            total_payable = p_credit - p_debit

        # 5. 本月经营数据 (基于订单表)
        # 本月销售额
        month_sales = SalesOrder.objects.filter(
            sales_date__gte=first_day_of_month,
            status='APPROVED'
        ).aggregate(sum=models.Sum('total_amount'))['sum'] or 0

        # 本月采购额
        month_purchase = PurchaseOrder.objects.filter(
            purchase_date__gte=first_day_of_month,
            status='APPROVED'
        ).aggregate(sum=models.Sum('total_amount'))['sum'] or 0

        # 6. 最近5条凭证动态
        recent_vouchers = AccountingVoucher.objects.all().order_by('-voucher_date', '-create_time')[:5]
        voucher_list = [{
            "date": v.voucher_date.strftime('%Y-%m-%d'),
            "no": v.voucher_no,
            "summary": v.details.first().summary if v.details.exists() else "无摘要",
            "amount": v.details.aggregate(sum=models.Sum('debit_amount'))['sum'] or 0
        } for v in recent_vouchers]

        return JsonResponse({
            "code": 200,
            "data": {
                "company_name": company_name,
                "total_cash": total_cash,
                "total_receivable": total_receivable,
                "total_payable": total_payable,
                "month_sales": month_sales,
                "month_purchase": month_purchase,
                "recent_vouchers": voucher_list
            }
        })