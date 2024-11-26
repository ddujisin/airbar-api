-- Add new columns for enhanced notification preferences
ALTER TABLE "NotificationPreference"
ADD COLUMN IF NOT EXISTS "mutedUntil" TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS "priorityThreshold" INTEGER DEFAULT 0;

-- Add constraint for priority threshold
ALTER TABLE "NotificationPreference"
ADD CONSTRAINT "priority_threshold_range"
CHECK ("priorityThreshold" >= 0 AND "priorityThreshold" <= 10);

-- Add index for muted_until for efficient querying
CREATE INDEX IF NOT EXISTS "notification_preference_muted_until_idx"
ON "NotificationPreference"("mutedUntil");

-- Add index for priority threshold
CREATE INDEX IF NOT EXISTS "notification_preference_priority_idx"
ON "NotificationPreference"("priorityThreshold");

-- Add function to automatically clear expired mutes
CREATE OR REPLACE FUNCTION clear_expired_mutes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW."mutedUntil" < CURRENT_TIMESTAMP THEN
        NEW."mutedUntil" = NULL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER clear_expired_notification_mutes
    BEFORE INSERT OR UPDATE ON "NotificationPreference"
    FOR EACH ROW
    EXECUTE FUNCTION clear_expired_mutes();
