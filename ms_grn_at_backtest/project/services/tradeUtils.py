
import math

def get_tick_size(price, method="floor"):
    """원화마켓 주문 가격 단위 

    Args:
        price (float]): 주문 가격 
        method (str, optional): 주문 가격 계산 방식. Defaults to "floor".

    Returns:
        float: 업비트 원화 마켓 주문 가격 단위로 조정된 가격 
    """

    if method == "floor":
        func = math.floor
    elif method == "round":
        func = round 
    else:
        func = math.ceil 

    if price >= 2000000:
        tick_size = func(price / 1000) * 1000
    elif price >= 1000000:
        tick_size = func(price / 500) * 500
    elif price >= 500000:
        tick_size = func(price / 100) * 100
    elif price >= 100000:
        tick_size = func(price / 50) * 50
    elif price >= 10000:
        tick_size = func(price / 10) * 10
    elif price >= 1000:
        tick_size = func(price / 5) * 5
    elif price >= 100:
        tick_size = func(price / 1) * 1
    elif price >= 10:
        tick_size = func(price / 0.1) / 10
    else:
        tick_size = func(price / 0.01) / 100

    return tick_size