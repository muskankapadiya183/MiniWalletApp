from rest_framework import status

SUCCESS_STATUS_CODE = status.HTTP_200_OK
ERROR_STATUS_CODE = status.HTTP_400_BAD_REQUEST
FAILURE_STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR


class ResponseHandler(object):
    def __init__(self):
        self.response_dict = dict()

    def success(
            self,
            data=None,
            error=None,
            msg="Object Manipulated Successfully",
            status_code=None,
    ):
        status_code = SUCCESS_STATUS_CODE
        self.response_dict.update(
            {
                "status": True,
                "status_code": status_code,
                "data": data,
                "error": error,
                "msg": msg,
            }
        )
        return self.response_dict, status_code

    def error(
            self, data=None, error=None, msg="Sorry, there was a problem.", status_code=None
    ):
        status_code = ERROR_STATUS_CODE
        self.response_dict.update(
            {
                "status": False,
                "status_code": status_code,
                "data": data,
                "error": error,
                "msg": msg,
            }
        )
        return self.response_dict, status_code

    def failure(
            self, data=None, error=None, msg="Something went wrong.", status_code=None
    ):
        status_code = FAILURE_STATUS_CODE
        self.response_dict.update(
            {
                "status": False,
                "status_code": status_code,
                "data": data,
                "error": error,
                "msg": msg,
            }
        )
        return self.response_dict, status_code

    def exception(
            self,
            data=None,
            error=None,
            msg="Something went wrong.",
            status_code=ERROR_STATUS_CODE,
    ):
        self.response_dict.update(
            {
                "status": False,
                "status_code": status_code,
                "data": data,
                "error": error,
                "msg": msg,
            }
        )
        return self.response_dict, status_code
