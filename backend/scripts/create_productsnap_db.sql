-- Create dedicated database for ProductSnap
-- Run this on your DigitalOcean Managed PostgreSQL

CREATE DATABASE productsnapdb
    WITH 
    OWNER = doadmin
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Connect to the new database
\c productsnapdb

-- Grant all privileges to doadmin user
GRANT ALL PRIVILEGES ON DATABASE productsnapdb TO doadmin;
GRANT ALL PRIVILEGES ON SCHEMA public TO doadmin;

-- Verify
\l productsnapdb
