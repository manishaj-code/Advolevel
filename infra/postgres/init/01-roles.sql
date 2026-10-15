-- Local only. Two roles, as in spec 12 §5:
--   advolevel       owner, runs migrations (POSTGRES_USER)
--   advolevel_app   the API/worker role: no BYPASSRLS, DML only
CREATE ROLE advolevel_app LOGIN PASSWORD 'advolevel_app' NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT ON DATABASE advolevel TO advolevel_app;
GRANT USAGE ON SCHEMA public TO advolevel_app;
ALTER DEFAULT PRIVILEGES FOR ROLE advolevel IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO advolevel_app;
ALTER DEFAULT PRIVILEGES FOR ROLE advolevel IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO advolevel_app;
