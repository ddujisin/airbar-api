# API Paths Verification

## Auth Routes
Frontend Path | Backend Path | Status | Notes
-------------|--------------|--------|-------
/api/auth/login | /api/auth/login | ✅ Match |
/api/auth/register | /api/auth/register | ✅ Match |
/api/auth/verify | /api/auth/verify | ✅ Match |
/api/auth/logout | /api/auth/logout | ✅ Match |

## Admin Routes
Frontend Path | Backend Path | Status | Notes
-------------|--------------|--------|-------
/api/admin/reservations | ❌ Missing | ❌ Not Found | Need to implement reservation routes
/api/admin/hosts | /api/admin/hosts | ✅ Match |
/api/admin/guests | ❌ Missing | ❌ Not Found | Need to implement guest routes
/api/admin/menu/items | /api/menu | ❌ Mismatch | Frontend uses wrong path

## Menu Routes
Frontend Path | Backend Path | Status | Notes
-------------|--------------|--------|-------
/api/menu/items | /api/menu | ❌ Mismatch | Frontend path incorrect
/api/menu/items/:id | /api/menu/:id | ❌ Mismatch | Frontend path incorrect
/api/admin/menu/items | /api/menu | ❌ Mismatch | Frontend uses wrong path structure

## Order Routes
Frontend Path | Backend Path | Status | Notes
-------------|--------------|--------|-------
/api/orders | /api/orders | ✅ Match |
/api/admin/reservations/:id/orders | ❌ Missing | ❌ Not Found | Need to implement reservation order routes

## Required Changes
1. Update menu item routes in frontend:
   - Change `/api/admin/menu/items` to `/api/menu`
   - Change `/api/menu/items` to `/api/menu`
   - Change `/api/menu/items/:id` to `/api/menu/:id`

2. Implement missing backend routes:
   - Reservation routes
   - Guest routes
   - Reservation order routes
