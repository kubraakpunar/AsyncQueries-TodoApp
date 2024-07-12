import time
import logging 

class ExecutionTimeMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response 
        self.logger = logging.getLogger(__name__)
    
    def __call__(self,request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        execution_time = end_time - start_time 

        self.logger.info(f"Request to {request.path} took {execution_time: .4f} seconds")
        return response 

