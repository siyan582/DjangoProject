from django.contrib import admin
from .models import Enterprise, Supplier, Customer, PurchaseOrder, PurchaseOrderItem

# 注册基础表
admin.site.register(Enterprise)
admin.site.register(Supplier)
admin.site.register(Customer)

# === 让后台支持“主子表”同时编辑 ===

# 定义子表（明细行）
class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1 # 默认显示一行空的，方便添加

# 定义主表，并将子表嵌入
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('order_no', 'supplier', 'total_amount', 'status', 'purchase_date')
    # 详情页嵌入明细表格
    inlines = [PurchaseOrderItemInline]