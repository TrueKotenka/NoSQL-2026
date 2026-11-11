INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('catalog', '2026-11-10', '2026-11-10T09:58:00+0000', 00000000-0000-4000-8000-000000000001, null, 'Catalog sync started');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('catalog', '2026-11-10', '2026-11-10T10:07:00+0000', 00000000-0000-4000-8000-000000000002, null, 'Product indexed');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('catalog', '2026-11-10', '2026-11-10T10:32:00+0000', 00000000-0000-4000-8000-000000000003, 'UPSTREAM_TIMEOUT', 'Search backend timed out');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('catalog', '2026-11-10', '2026-11-10T11:00:00+0000', 00000000-0000-4000-8000-000000000004, null, 'Catalog sync finished');

INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('catalog', '2026-11-11', '2026-11-11T10:05:00+0000', 00000000-0000-4000-8000-000000000005, null, 'Inventory snapshot loaded');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('catalog', '2026-11-11', '2026-11-11T10:40:00+0000', 00000000-0000-4000-8000-000000000006, 'UPSTREAM_TIMEOUT', 'Pricing backend timed out');

INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-10', '2026-11-10T09:59:00+0000', 00000000-0000-4000-8000-000000000007, null, 'Checkout opened');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-10', '2026-11-10T10:15:00+0000', 00000000-0000-4000-8000-000000000008, null, 'Order created');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-10', '2026-11-10T10:15:00+0000', 00000000-0000-4000-8000-000000000009, null, 'Inventory reserved');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-10', '2026-11-10T10:45:00+0000', 00000000-0000-4000-8000-00000000000a, 'UPSTREAM_TIMEOUT', 'Payment gateway timed out');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-10', '2026-11-10T11:00:00+0000', 00000000-0000-4000-8000-00000000000b, null, 'Order retried');

INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-11', '2026-11-11T10:12:00+0000', 00000000-0000-4000-8000-00000000000c, null, 'Payment authorized');
INSERT INTO shop_events.service_events (service, event_day, event_time, event_id, error_code, message)
VALUES ('checkout', '2026-11-11', '2026-11-11T10:51:00+0000', 00000000-0000-4000-8000-00000000000d, null, 'Order completed');
