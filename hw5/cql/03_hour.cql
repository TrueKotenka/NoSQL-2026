SELECT service, event_day, event_time, event_id, error_code, message
FROM shop_events.service_events
WHERE service = 'checkout'
  AND event_day = '2026-11-10'
  AND event_time >= '2026-11-10T10:00:00+0000'
  AND event_time < '2026-11-10T11:00:00+0000'
ORDER BY event_time ASC;
