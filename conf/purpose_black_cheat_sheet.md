
CREATE USER purpose_black__user WITH PASSWORD '123456789';
CREATE DATABASE purpose_black_db OWNER purpose_black__user ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE template0;
GRANT ALL PRIVILEGES ON DATABASE purpose_black_db TO purpose_black__user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO purpose_black__user;
ALTER USER purpose_black__user CREATEDB;
ALTER ROLE purpose_black__user SUPERUSER;