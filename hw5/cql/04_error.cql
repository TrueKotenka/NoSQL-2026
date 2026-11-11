SELECT service, event_day, event_time, event_id, error_code, message
FROM shop_events.service_events
WHERE error_code = 'UPSTREAM_TIMEOUT';
