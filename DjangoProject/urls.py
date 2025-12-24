from django.contrib import admin
from django.urls import path
from finance.views import enterprise_info, supplier_list, purchase_order_list, customer_list, sales_order_list
from finance.views import account_subject_list
from finance.views import generate_voucher, voucher_list
from finance.views import payment_list, collection_list
from finance.views import trial_balance
from finance.views import balance_sheet, income_statement, cash_flow
from finance.views import dashboard_stats

urlpatterns = [
    path('admin/', admin.site.urls),
    # 这一行定义接口地址：http://localhost:8000/api/enterprise
    path('api/enterprise', enterprise_info),
    path('api/supplier', supplier_list),
    path('api/purchase_order', purchase_order_list), # 采购订单 (新增)
    # 新增的两个
    path('api/customer', customer_list),
    path('api/sales_order', sales_order_list),
    path('api/subject', account_subject_list),
    path('api/generate_voucher', generate_voucher),
    path('api/voucher', voucher_list),
    path('api/payment', payment_list),
    path('api/collection', collection_list),
    path('api/trial_balance', trial_balance),
    path('api/balance_sheet', balance_sheet),
    path('api/income_statement', income_statement),
    path('api/cash_flow', cash_flow),
    path('api/dashboard', dashboard_stats), # 新增这一行
]








