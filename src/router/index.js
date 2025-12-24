import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EnterpriseView from '../views/EnterpriseView.vue'
import SupplierView from '../views/SupplierView.vue'
// 1. 【关键】引入你刚才写的页面
import PurchaseOrderView from '../views/PurchaseOrderView.vue'
import CustomerView from '../views/CustomerView.vue'
import SalesOrderView from '../views/SalesOrderView.vue'
import SubjectView from '../views/SubjectView.vue'
import VoucherView from '../views/VoucherView.vue'
import PaymentView from '../views/PaymentView.vue'
import CollectionView from '../views/CollectionView.vue'
import ReconciliationView from '../views/ReconciliationView.vue'
import BalanceSheetView from '../views/BalanceSheetView.vue'
import IncomeStatementView from '../views/IncomeStatementView.vue'
import CashFlowView from '../views/CashFlowView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/enterprise',
      name: 'enterprise',
      component: EnterpriseView
    },
    {
      path: '/supplier',
      name: 'supplier',
      component: SupplierView
    },
    // 2. 【关键】这里就是缺的那条路！
    {
      path: '/purchase_order',
      name: 'purchase_order',
      component: PurchaseOrderView
    },
    // 3. 预留给未来的（防止报错）
    {
      path: '/customer',
      name: 'customer',
      component: () => import('../views/HomeView.vue') // 暂时先指向首页
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/customer',
      name: 'customer',
      component: CustomerView
    },
    {
      path: '/sales_order', // 注意：这里对应 App.vue 里的 index
      name: 'sales_order',
      component: SalesOrderView
    },
    {
      path: '/subject',
      name: 'subject',
      component: SubjectView
    },
    {
      path: '/voucher',  // 注意：这里要对应 App.vue 里的菜单 index
      name: 'voucher',
      component: VoucherView
    },
    {
      path: '/payment',
      name: 'payment',
      component: PaymentView
    },
    {
      path: '/collection',
      name: 'collection',
      component: CollectionView
    },
    {
      path: '/report',
      name: 'report',
      component: ReconciliationView
    },
    { path: '/balance_sheet', component: BalanceSheetView },
    { path: '/income_statement', component: IncomeStatementView },
    { path: '/cash_flow', component: CashFlowView },
  ],
})

export default router







