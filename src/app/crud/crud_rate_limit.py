from fastcrud import FastCRUD

from ..models.rate_limit import RateLimit, RateLimitDelete, RateLimitUpdate, RateLimitUpdateInternal

CRUDRateLimit = FastCRUD[
    RateLimit, RateLimitUpdate, RateLimitUpdateInternal, RateLimitDelete
]
crud_rate_limits = CRUDRateLimit(RateLimit)
