-- =============================================
-- COMPLETE GEOFENCING CLEANUP SCRIPT
-- This script removes all geofencing features
-- =============================================

USE cgs;

-- Drop geofencing tables
DROP TABLE IF EXISTS site_visits;
DROP TABLE IF EXISTS company_settings;
DROP TABLE IF EXISTS geofence_requests;

-- Remove geofencing columns from users table
ALTER TABLE users 
DROP COLUMN IF EXISTS geofence_status,
DROP COLUMN IF EXISTS geofence_lat,
DROP COLUMN IF EXISTS geofence_lon,
DROP COLUMN IF EXISTS work_mode,
DROP COLUMN IF EXISTS remote_address,
DROP COLUMN IF EXISTS remote_latitude,
DROP COLUMN IF EXISTS remote_longitude;

-- Clean up any remaining geofencing data
-- (No additional cleanup needed for core tables)

SELECT 'Geofencing cleanup completed successfully!' as status;