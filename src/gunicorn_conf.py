from multiprocessing import cpu_count

bind = "0.0.0.0:8000"
workers = cpu_count() * 2 + 1
limit_request_fields = 32000
limit_request_field_size = 0
