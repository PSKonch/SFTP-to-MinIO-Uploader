# SFTP-to-MinIO-Uploader

# О подводных камнях и edge-cases:

1. Асинхронность vs Celery (и почему Dramatiq):
  По заданию требовалось использовать Celery, но изначально я делал проект асинхронным (огромная ошибка), поэтому SFTP и БД были подобраны под async-стек. На практике Celery не поддерживает асинхронные таски из   коробки. Вызов await внутри обычной таски приводит к ошибкам, а попытка запускать event loop поверх delay/apply_async к гонкам за loop
  Я пробовал вызывать асинхронную функцию изнутри celery-таски через asyncio.run() или loop.run_until_complete(), но это ведёт к блокировке воркера или ошибке “This event loop is already running” (моя основная    проблема, из-за которой в итоге было принято решение сменить библиотеку)
  В результате проект был переведён на Dramatiq (асинхронный брокер задач) и APScheduler (планировщик для регулярного запуска)

2. Race Condition и борьба воркеров за файлы
  Когда несколько воркеров одновременно мониторят одни и те же каталоги на серверах, возникает риск гонки за файлы:
  Одни и те же файлы могут быть обнаружены сразу несколькими воркерами, что приводит к появлению дубликатов в БД и MinIO, а заодно снижает общую скорость работы системы.
  Возможны случаи, когда несколько воркеров параллельно обрабатывают один и тот же файл, расходуя ресурсы впустую.

Что я сделал:
  Разбил задачи на подтаски, чтобы каждая отвечала только за один сервер и стриминг одного файла — это резко снижает вероятность коллизий
  Использовал статусы файлов в базе данных и максимально быстро менял их при старте обработки, чтобы другие воркеры видели, что файл уже занят
  Помимо проверки наличия файла в БД, имеет смысл проверять его и в MinIO — это помогает избежать появления зависших или потерянных файлов в результате аварий

3. Недоступность SFTP/MinIO
Иногда SFTP может быть временно недоступен (например, если сервер упал, либо его просто не существует — ошибка в БД). MinIO, в свою очередь, может быть переполнен или недоступен по сети

Мои выводы и рекомендации:
Использовать retry-логику с backoff, чтобы не терять файлы из-за временных проблем
Никогда не удалять исходный файл с SFTP до подтверждённой загрузки в MinIO
Логировать любые неудачные операции, чтобы можно было потом провести разбор ошибок или дообработку вручную
Настроить хотя бы базовый мониторинг, чтобы видеть, когда что-то идет не так (телега, email, Sentry и т.д.)

4. Параллельный стриминг больших файлов
С большими файлами ситуация ещё интереснее: несколько воркеров могут начать скачивать и загружать один и тот же файл параллельно. Это не только создаёт дубликаты и тормозит весь процесс, но и чревато повреждением файла при перетягивании каната

Как минимизировать проблему:
При старте обработки файл получает статус DOWNLOADING в БД — это сигнал для остальных воркеров “не трогай, уже занимаются”
Только один воркер может начать скачивание — остальные пропускают файл, если видят этот статус

P.S: Структура проекта сильно изменилась, файл project-structure.txt может быть не актуален 

# Функции, алгоритмы и технологии 

1. Сканирование серверов на наличие новых файлов
1.1. scan_and_store_files(uow)
Получает список всех серверов из БД (uow.servers.get_all_servers())
Для каждого сервера вызывает scan_files_on_server(uow, server)
После обхода всех серверов коммитит изменения в БД

1.2. scan_files_on_server(uow, server)
Устанавливает SFTP-соединение с сервером (через asyncssh)
Получает список файлов в целевой папке (await sftp.listdir(server.folder_path))
Для каждого файла:
Получает информацию о файле (await sftp.stat(file_path))
Проверяет, есть ли уже такой файл в БД (uow.files.get_filtered(...))
Если файла нет в БД — создает запись с статусом PENDING

2. Скачивание и загрузка файлов с SFTP в MinIO
2.1. streaming_files_from_sftp_to_minio(uow, minio_client)
Получает список всех файлов из БД (uow.files.get_all_files())
Для каждого файла со статусом PENDING или ERROR вызывает download_and_upload_file(uow, file, minio_client)
2.2. stream_file_from_sftp_to_minio(uow, file_id, minio_client)
Берет конкретный файл по ID (uow.files.take_a_file_to_put_in_minio(file_id))
Если файл найден, вызывает download_and_upload_file(uow, file, minio_client)

2.3. download_and_upload_file(uow, file, minio_client)
Обновляет статус файла на DOWNLOADING
Устанавливает SFTP-соединение, открывает файл на сервере
Читает файл по частям (чанками), собирает в память
Загружает файл в MinIO (minio_client.put_object(...))
Если успешно — обновляет статус файла на DOWNLOADED
В случае ошибки — помечает файл как ERROR, логирует ошибку

3. Задачи через Dramatiq (Actors)
scan_server_task(server_id) — асинхронно сканирует конкретный сервер
scan_all_servers_task() — инициирует задачу сканирования для всех серверов, по одному на задачу
stream_file_task(file_id) — асинхронно загружает конкретный файл из SFTP в MinIO
stream_all_files_task() — инициирует задачу загрузки всех файлов (по одному на задачу)

4. Планировщик задач (APScheduler)
start_scheduler()
Каждые 5 минут вызывает:
scan_all_servers_task.send() — сканирует все сервера на новые файлы
stream_all_files_task.send() — отправляет все файлы на скачивание/заливку в MinIO
Работает бесконечно, пока не будет остановлен вручную

Общий поток работы
Планировщик запускает сканирование серверов и заливку файлов
Сканирование ищет новые файлы и создает записи в БД
Заливка обрабатывает все новые/ошибочные файлы: скачивает их и заливает в MinIO, обновляя статусы
Ошибки логируются, а файлы получают статус ERROR для повторной попытки на следующем цикле

Взаимодействие компонентов:
UnitOfWork гарантирует атомарность операций с БД.
MinIO — конечное хранилище файлов
SFTP — источник файлов
Dramatiq — асинхронное выполнение задач
APScheduler — автоматизация и периодический запуск задач
RabbitMQ — Уведомляет об успехах/ошибках
