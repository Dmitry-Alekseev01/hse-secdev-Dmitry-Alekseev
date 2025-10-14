| Поток/Элемент | Угроза (STRIDE) | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|------|----------|---------------|-------------------|
| F1: HTTP | S: Spoofing | R1 | Аутентификация API ключей + rate limiting | NFR-01, NFR-03 | Security review + нагрузочный тест |
| F1: HTTP | T: Tampering | R2 | TLS 1.3 | NFR-06 | Code review SQLAlchemy |
| F2: HTTP | I: Information Disclosure | R3 | Внутренний TLS + маскирование PII | NFR-02 | Контракт-тесты ошибок RFC7807 |
| F3: SQL | T: Tampering | R4 | Параметризованные запросы SQLAlchemy | NFR-06 | Unit-тесты SQLAlchemy ORM |
| F3: SQL | E: Elevation of Privilege | R5 | RBAC + проверка прав доступа | NFR-01 | Тесты хеширования паролей |
| Database | D: Denial of Service | R6 | Rate limiting + индексы БД | NFR-03, NFR-04 | Нагрузочные тесты p95 ≤ 300ms |
| Service | R: Repudiation | R7 | Structured logging + correlation_id | NFR-02 | Мониторинг формата ошибок |
| Database | I: Information Disclosure | R8 | Бэкапы | NFR-08 | Скрипты резервного копирования |
| API Gateway | D: Denial of Service | R9 | Rate limiting + WAF | NFR-03, NFR-04 | Нагрузочные тесты 50 RPS |
| Requirements.txt | T: Tampering | R10 | Dependabot | NFR-05 | CI security scan (safety) |
| SQLite файл | I: Information Disclosure | R11 | Шифрование файла БД | NFR-08 | Проверка бэкапов |
| /users endpoint | D: Denial of Service | R12 | Rate limiting + кэширование | NFR-03 | Нагрузочный тест /users |
| /media endpoint | D: Denial of Service | R13 | Rate limiting + кэширование | NFR-04 | Нагрузочный тест /media |
