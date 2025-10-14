| RiskID | Описание                         | Связь (F/NFR) | L | I | Risk | Стратегия | Владелец | Срок  | Критерий закрытия                 |
|--------|----------------------------------|---------------|---|---|------|-----------|----------|-------|-----------------------------------|
| R1     | Подделка внешнего приложения     | F1, NFR-01, NFR-03 | 3 | 4 | 12   | Снизить   | @Dmitry-Alekseev01   | 2025-12-20 | Security review + аутентификация API |
| R2     | Подмена TLS соединения           | F1, NFR-06    | 2 | 5 | 10   | Снизить   | @Dmitry-Alekseev01   | 2025-12-15 | TLS 1.3 + code review SQLAlchemy |
| R3     | Утечка PII в внутренней сети     | F2, NFR-02    | 3 | 4 | 12   | Снизить   | @Dmitry-Alekseev01   | 2025-12-25 | Контракт-тесты RFC7807 + маскирование |
| R4     | SQL-инъекции в запросах          | F3, NFR-06    | 4 | 5 | 20   | Снизить   | @Dmitry-Alekseev01   | 2025-12-10 | Unit-тесты SQLAlchemy ORM |
| R5     | Неавторизованный доступ к данным | F3, NFR-01    | 3 | 5 | 15   | Снизить   | @Dmitry-Alekseev01   | 2025-12-18 | Tесты хеширования паролей |
| R6     | Перегрузка базы данных           | Database, NFR-03, NFR-04 | 3 | 4 | 12   | Снизить   | @Dmitry-Alekseev01   | 2025-12-30 | Нагрузочные тесты p95 ≤ 300ms |
| R7     | Отсутствие аудита операций       | Service, NFR-02 | 2 | 3 | 6    | Снизить   | @Dmitry-Alekseev01   | 2025-12-22 | Structured logging + correlation_id |
| R8     | Потеря данных БД                 | Database, NFR-08 | 2 | 5 | 10   | Снизить   |@Dmitry-Alekseev01   | 2025-12-28 | Скрипты резервного копирования |
| R9     | DDoS атака на API Gateway        | API Gateway, NFR-03, NFR-04 | 3 | 4 | 12   | Снизить   | @Dmitry-Alekseev01   | 2025-12-15 | Rate limiting + тесты 50 RPS |
| R10    | Уязвимости в зависимостях        | Requirements.txt, NFR-05 | 4 | 4 | 16   | Снизить   | @Dmitry-Alekseev01   | 2025-12-12 | Dependabot + CI security scan |
| R11    | Кража файла БД                   | SQLite файл, NFR-08 | 2 | 5 | 10   | Снизить   | @Dmitry-Alekseev01   | 2025-12-25 | Проверка бэкапов |
| R12    | DDoS на эндпоинт пользователей   | /users, NFR-03 | 3 | 3 | 9    | Снизить   | @Dmitry-Alekseev01   | 2025-12-20 | Rate limiting + нагрузочный тест |
| R13    | DDoS на эндпоинт медиа           | /media, NFR-04 | 3 | 3 | 9    | Снизить   | @Dmitry-Alekseev01  | 2025-12-20 | Rate limiting + нагрузочный тест |
