# api/urls.py
from django.urls import path
from .views_governorate import GovernorateListView, GovernorateDetailView, GovernorateCitiesView
from .views_category import CategoryListView
from .views import (
    OnlineUsersSettingsView,
    OfferListView, 
    OfferDetailView, 
    FeaturedOfferListView, 
    CityListView,
    FavoriteListView,
    FavoriteToggleView,
    ReviewCreateView, ReviewUpdateView, MerchantReviewListView, LatestReviewsView,
    TopMerchantsView, MerchantDetailView, MerchantOffersView,
    NearbyOffersView,
    CheckAuthView
)
from .merchant_views import (
    CheckMerchantStatusView,
    MerchantRequestView,
    MerchantDashboardView,
    MerchantOffersListView,
    MerchantOfferCreateView,
    MerchantOfferUpdateView,
    MerchantOfferDeleteView,
    MerchantAnalyticsView,
    MerchantSettingsUpdateView
)
from .api_root import api_root

from .view_tracker import RecordOfferViewView

urlpatterns = [
    # API Root
    path('', api_root, name='api-root'),
    
    # Auth Check (للتصحيح)
    path('check-auth/', CheckAuthView.as_view(), name='check-auth'),
    
    # Governorates (المحافظات)
    path('governorates/', GovernorateListView.as_view(), name='governorate-list'),
    path('governorates/<int:pk>/', GovernorateDetailView.as_view(), name='governorate-detail'),
    path('governorates/<int:governorate_id>/cities/', GovernorateCitiesView.as_view(), name='governorate-cities'),
    
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    # Cities
    path('cities/', CityListView.as_view(), name='city-list'),
    
    # Offers
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offers/<int:offer_id>/view/', RecordOfferViewView.as_view(), name='record-offer-view'),
    path('featured-offers/', FeaturedOfferListView.as_view(), name='featured-offer-list'),
    path('nearby-offers/', NearbyOffersView.as_view(), name='nearby-offers'),

    # Favorites
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('offers/<int:offer_id>/favorite/', FavoriteToggleView.as_view(), name='favorite-toggle'),
    
    # Merchants (الجديد)
    path('top-merchants/', TopMerchantsView.as_view(), name='top-merchants'),
    path('merchants/<int:pk>/', MerchantDetailView.as_view(), name='merchant-detail'),
    path('merchants/<int:merchant_id>/offers/', MerchantOffersView.as_view(), name='merchant-offers'),
    path('merchants/<int:merchant_id>/reviews/', MerchantReviewListView.as_view(), name='merchant-review-list'),
    path('merchants/<int:merchant_id>/reviews/create/', ReviewCreateView.as_view(), name='review-create'),
    path('merchants/<int:merchant_id>/reviews/update/', ReviewUpdateView.as_view(), name='review-update'),
    
    # Merchant Dashboard (لوحة تحكم التجار)
    path('merchant/check-status/', CheckMerchantStatusView.as_view(), name='check-merchant-status'),
    path('merchant/request/', MerchantRequestView.as_view(), name='merchant-request'),
    path('merchant/dashboard/', MerchantDashboardView.as_view(), name='merchant-dashboard'),
    path('merchant/offers/', MerchantOffersListView.as_view(), name='merchant-offers-list'),
    path('merchant/offers/create/', MerchantOfferCreateView.as_view(), name='merchant-offer-create'),
    path('merchant/offers/<int:offer_id>/update/', MerchantOfferUpdateView.as_view(), name='merchant-offer-update'),
    path('merchant/offers/<int:offer_id>/delete/', MerchantOfferDeleteView.as_view(), name='merchant-offer-delete'),
    path('merchant/analytics/', MerchantAnalyticsView.as_view(), name='merchant-analytics'),
    path('merchant/settings/update/', MerchantSettingsUpdateView.as_view(), name='merchant-settings-update'),
    path('online-users-settings/', OnlineUsersSettingsView.as_view(), name='online-users-settings'),
]