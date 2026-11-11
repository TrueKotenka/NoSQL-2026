CREATE KEYSPACE IF NOT EXISTS shop_events
WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3}
AND durable_writes = true;

CREATE TABLE IF NOT EXISTS shop_events.service_events (
    service text,
    event_day date,
    event_time timestamp,
    event_id uuid,
    error_code text,
    message text,
    PRIMARY KEY ((service, event_day), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time ASC, event_id ASC);

CREATE INDEX IF NOT EXISTS service_events_error_code_idx
ON shop_events.service_events (error_code);
