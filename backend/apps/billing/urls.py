from django.urls import path

from apps.billing.views import AuthorizationView, BillingDayView, HealthInsurerListView, PaymentView

urlpatterns = [
    path("billing/day/", BillingDayView.as_view(), name="billing-day"),
    path("billing/insurers/", HealthInsurerListView.as_view(), name="billing-insurers"),
    path(
        "billing/encounters/<uuid:encounter_id>/payment/",
        PaymentView.as_view(),
        name="billing-payment",
    ),
    path(
        "billing/encounters/<uuid:encounter_id>/authorization/",
        AuthorizationView.as_view(),
        name="billing-authorization",
    ),
]
