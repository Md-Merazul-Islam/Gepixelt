from rest_framework import status
from rest_framework.response import Response

def success_response(message, data, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": data
    }, status=status_code)


def failure_response(message, error, status_code=status.HTTP_400_BAD_REQUEST):
    if 'non_field_errors' in error:
        error_message = error['non_field_errors'][0] 
    else:
        error_message = error  
    
    return Response({
        "success": False,
        "statusCode": status_code,
        "message": message,
        "error": {
            "message": error_message
        }
    }, status=status_code)