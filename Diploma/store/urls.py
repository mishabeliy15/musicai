from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('login/', views.loginPage, name="login"),
    path('signup/', views.singupPage, name="signup"),
    path('logout/', views.logoutUser, name="logout"),

    path('profile/', views.profile, name="profile"),
    path('my_music/', views.my_music, name="my_music"),
    path('product/', views.product, name="product"),
    path('composers/', views.composers, name="composers"),
    path('composer_order/', views.composerOrder, name="composer_order"),
    path('my_orders/', views.myOrders, name="my_orders"),
    path('get_product_ordered/', views.getProductOrdered, name="get_product_ordered"),
    path('freelance_order/', views.freelanceOrder, name="freelance_order"),
    path('freelance_list/', views.freelanceList, name="freelance_list"),
    path('my_freelance/', views.myFreelance, name="my_freelance"),
    path('freelance_order_info/', views.freelanceOrderInfo, name="freelance_order_info"),
    path('ai_order/', views.aiOrder, name="ai_order"),
    path('ai_prepare/', views.aiOrderPrepare, name="ai_prepare"),
    path('ai_generate/', views.aiGenerate, name="ai_generate"),
    path('reset_ai_order/', views.resetAiOrder, name="reset_ai_order"),
    path('accept_ai_order/', views.acceptAiOrder, name="accept_ai_order"),
    path('ai_order_payment_callback/', views.aiOrderPaymentCallback, name="ai_order_payment_callback"),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('checkout_callback/', views.checkoutCallback, name="checkout_callback"),
    path('hold_payment_form/', views.holdPaymentForm, name="hold_payment_form"),
    path('personal_order_hold_payment_callback/', views.personalOrderHoldPaymentCallback, name="personal_order_hold_payment_callback"),

    path('upload_profile_image/', views.uploadProfileImage, name="upload_profile_image"),
    path('profile_save/', views.profileSave, name="profile_save"),
    path('personalinfo_save/', views.personalInfoSave, name="personalinfo_save"),
    path('product_save/', views.productSave, name="product_save"),
    path('order_save/', views.orderSave, name="order_save"),
    path('freelance_order_save/', views.freelanceOrderSave, name="freelance_order_save"),
    path('order_confirm/', views.orderComposerConfirm, name="order_confirm"),
    path('order_customer_confirm/', views.orderCustomerConfirm, name="order_customer_confirm"),
    path('send_file/', views.sendFile, name="send_file"),
    path('accept_order/', views.acceptOrder, name="accept_order"),
    path('bet_save/', views.betSave, name="bet_save"),
    path('choose_composer/', views.chooseComposer, name="choose_composer"),
]
