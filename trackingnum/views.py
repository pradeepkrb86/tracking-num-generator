from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerOrderDataSerializer
from .utils import create_tracking_number
# Create your views here.
class NextTrackingNumberView(APIView):
    def get(self,request):
        serializer = CustomerOrderDataSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            try:
                tracking_number,created_at = create_tracking_number(
                                                                     origin_country_id=validated_data['origin_country_id'],
                                                                     destination_country_id=validated_data['destination_country_id'],
                                                                     customer_id=str(validated_data['customer_id']),
                                                                   )
                data = {
                        "tracking_number":tracking_number,
                        "created_at":created_at
                       }
                #print("before",data,status.HTTP_200_OK)
                return Response(data,status = status.HTTP_200_OK)
            except Exception as e:
               #print("e is",str(e))
               return Response({"error":str(e)},status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
