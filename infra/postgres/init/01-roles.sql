-- Local only. Two roles, as in spec 12 §5:
--   advolevel       owner, runs migrations (POSTGRES_USER)
--   advolevel_app   the API/worker role: no BYPASSRLS; table privileges come from migrations
CREATE ROLE advolevel_app LOGIN PASSWORD 'advolevel_app' NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT ON DATABASE advolevel TO advolevel_app;
