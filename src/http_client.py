import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://rpn.gov.ru"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/153.0.0.0 Safari/537.36"
)

REQUEST_DELAY = 0.5
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


logger = logging.getLogger(__name__)


class FkkoClient:
    """Обертка над requests.Session c паузой, retry и таймаутом."""
    def __init__(self, delay: float = REQUEST_DELAY, timeout: int = REQUEST_TIMEOUT):
        self.delay = delay
        self.timeout = timeout
        self._last_request_time = 0.0
        self.session = requests.Session()

    def _build_session(self) -> requests.Session:
        """Создает Session с заголовками и авто-повторами."""
        session = requests.Session()

        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
        })

        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _wait(self):
        """Выдерживает паузу между запросами."""
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def get(self, url: str, **kwargs) -> requests.Response | None:
        """GET-запрос с паузой, таймаутом и обработкой ошибок.
        Принимает как полный URL, так и путь ('/fkko/').
        Возвращает requests.Response или None при фатальной ошибке."""
        if not url.startswith(("http://", "https://")):
            url = BASE_URL + url

        self._wait()
        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            self._last_request_time = time.monotonic()
            return response
        except requests.RequestException as exc:
            logger.error("Запрос не удался: %s - %s", url, exc)
            return None
        