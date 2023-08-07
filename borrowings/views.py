from rest_framework import generics, mixins

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingDetailSerializer


class BorrowingViewSet(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingDetailSerializer
