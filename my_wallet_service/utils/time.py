from datetime import datetime, timezone
import pytz
from my_wallet_service.utils.config import settings

'''ISO 8601'''
# 2025-08-27T13:45:00 (без часового пояса)
# 2025-08-27T13:45:00+03:00 (с часовым поясом)

'''Unix Timestamp (целое число секунд/миллисекунд с 1970-01-01 UTC)'''

# 2025-08-27 13:31:00.645200+00:00
def now_utc() -> datetime:
    """Возвращает текущее UTC время с tzinfo."""
    return datetime.now(timezone.utc)

# 2025-08-27 16:31:00.663714+03:00
def now_local() -> datetime:
    """Возвращает текущее локальное время в таймзоне из настроек."""
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz)

# 2025-08-27T16:31:00.663728+03:00
def now_local_str() -> str:
    """Возвращает текущее локальное время в виде строки ISO 8601."""
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz).isoformat()

# utc_time = now_utc()
# local_time = now_local()
# now_local_str = now_local_str()
# print("UTC:", utc_time)
# print("Local:", local_time)
# print("now_local_str:", now_local_str)