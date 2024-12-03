-- Rename token column to accessToken in Session table
ALTER TABLE "Session" RENAME COLUMN "token" TO "accessToken";
