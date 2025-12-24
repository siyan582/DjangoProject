from django.db import models
from django.utils import timezone
import uuid


# ==========================================
# 1. 基础信息域
# ==========================================
class Enterprise(models.Model):
    """企业信息表"""
    name = models.CharField(max_length=100, unique=True, verbose_name="企业名称")
    type = models.CharField(max_length=20, verbose_name="企业类型")
    registered_capital = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="注册资金")
    establish_date = models.DateField(null=True, blank=True, verbose_name="成立日期")
    industry = models.CharField(max_length=50, null=True, blank=True, verbose_name="所属行业")
    tax_no = models.CharField(max_length=20, null=True, blank=True, verbose_name="税务登记号")

    # [新增] 财务年度起始月，缺省为1月
    fiscal_year_start_month = models.IntegerField(default=1, verbose_name="财务年度起始月")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 't_enterprise'


class Supplier(models.Model):
    """供应商表"""
    name = models.CharField(max_length=100, verbose_name="供应商名称")
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="联系人")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="电话")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="地址")

    # [新增] 刚才报错缺少的字段
    bank_account = models.CharField(max_length=50, null=True, blank=True, verbose_name="银行账户")
    default_credit_period = models.IntegerField(default=0, verbose_name="默认账期(天)")

    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'finance_supplier'


class Customer(models.Model):
    """客户表"""
    name = models.CharField(max_length=100, verbose_name="客户名称")
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="联系人")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="电话")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="地址")

    # [新增] 刚才报错缺少的字段
    default_credit_period = models.IntegerField(default=0, verbose_name="默认账期(天)")

    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 't_customer'


# ==========================================
# 2. 会计科目域
# ==========================================
class AccountSubject(models.Model):
    """会计科目表"""
    code = models.CharField(max_length=20, unique=True, verbose_name="科目编码")
    name = models.CharField(max_length=50, verbose_name="科目名称")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name="父级科目")

    TYPE_CHOICES = [('ASSET', '资产'), ('LIABILITY', '负债'), ('EQUITY', '权益'), ('COST', '成本'),
                    ('PROFIT_LOSS', '损益')]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="科目类别")

    DIRECTION_CHOICES = [('DEBIT', '借'), ('CREDIT', '贷')]
    balance_direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, verbose_name="余额方向")

    class Meta:
        db_table = 'finance_account_subject'
        ordering = ['code']


# ==========================================
# 3. 业务单据域 (采购/销售)
# ==========================================
class PurchaseOrder(models.Model):
    """采购订单主表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name="订单编号")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="供应商")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="总金额")

    status = models.CharField(max_length=20, default='APPROVED', verbose_name="审核状态")
    is_posted = models.BooleanField(default=False, verbose_name="是否过账")
    is_settled = models.BooleanField(default=False, verbose_name="是否结清")

    purchase_date = models.DateField(default=timezone.now, verbose_name="采购日期")
    credit_period = models.IntegerField(default=0, verbose_name="账期(天)")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'finance_purchase_order'


class PurchaseOrderItem(models.Model):
    """采购订单明细项"""
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=100)

    # [新增] 必须指定支出科目，用于生成凭证
    expense_subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, verbose_name="支出科目", null=True)

    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # [新增] 税率
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000, verbose_name="税率")

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    remark = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'finance_purchase_order_item'


class SalesOrder(models.Model):
    """销售订单主表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name="订单编号")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="客户")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="总金额")

    status = models.CharField(max_length=20, default='APPROVED', verbose_name="审核状态")
    is_posted = models.BooleanField(default=False, verbose_name="是否过账")
    is_settled = models.BooleanField(default=False, verbose_name="是否结清")

    sales_date = models.DateField(default=timezone.now, verbose_name="销售日期")
    credit_period = models.IntegerField(default=0, verbose_name="账期(天)")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'finance_sales_order'


class SalesOrderItem(models.Model):
    """销售订单明细项"""
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=100)

    # [新增] 必须指定收入科目，用于生成凭证
    income_subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, verbose_name="收入科目", null=True)

    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # [新增] 税率
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000, verbose_name="税率")

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    remark = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'finance_sales_order_item'


# ==========================================
# 4. 财务凭证与收付
# ==========================================
class AccountingVoucher(models.Model):
    """会计凭证"""
    voucher_no = models.CharField(max_length=50, unique=True, verbose_name="凭证号")
    voucher_date = models.DateField(default=timezone.now, verbose_name="凭证日期")
    source_document = models.CharField(max_length=50, null=True, blank=True, verbose_name="来源单据")
    creator = models.CharField(max_length=50, default='系统自动')
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'finance_accounting_voucher'
        ordering = ['-voucher_date', '-create_time']


class VoucherDetail(models.Model):
    """凭证分录"""
    voucher = models.ForeignKey(AccountingVoucher, on_delete=models.CASCADE, related_name='details')
    summary = models.CharField(max_length=200, verbose_name="摘要")
    subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, verbose_name="科目")
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="借方金额")
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="贷方金额")

    class Meta:
        db_table = 'finance_voucher_detail'


class PaymentRecord(models.Model):
    """付款单"""
    payment_no = models.CharField(max_length=50, unique=True, verbose_name="付款单号")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="供应商")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name="关联采购单")

    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="付款金额")
    pay_date = models.DateField(default=timezone.now, verbose_name="付款日期")

    # [新增] 付款科目（如银行存款），生成凭证时贷方科目
    payment_method_subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, null=True, blank=True,
                                               verbose_name="付款科目")

    is_settled = models.BooleanField(default=False, verbose_name="是否已付款")
    status = models.CharField(max_length=20, default='CREATED')
    remark = models.CharField(max_length=200, null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'finance_payment_record'
        ordering = ['-pay_date', '-create_time']


class CollectionRecord(models.Model):
    """收款单"""
    collection_no = models.CharField(max_length=50, unique=True, verbose_name="收款单号")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="客户")
    related_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="关联销售单")

    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="收款金额")
    collect_date = models.DateField(default=timezone.now, verbose_name="收款日期")

    # [新增] 收款科目（如银行存款）
    collection_method_subject = models.ForeignKey(AccountSubject, on_delete=models.PROTECT, null=True, blank=True,
                                                  verbose_name="收款科目")

    status = models.CharField(max_length=20, default='CREATED')
    remark = models.CharField(max_length=200, null=True, blank=True)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'finance_collection_record'