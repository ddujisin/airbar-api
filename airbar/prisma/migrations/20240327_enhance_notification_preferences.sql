-- Enhance notification preferences table
ALTER TABLE "NotificationPreference"
ADD COLUMN IF NOT EXISTS "mutedUntil" TIMESTAMP,
ADD COLUMN IF NOT EXISTS "priorityThreshold" INTEGER DEFAULT 0;

-- Add check constraint for priority threshold
ALTER TABLE "NotificationPreference"
ADD CONSTRAINT "priority_threshold_range"
CHECK ("priorityThreshold" >= 0 AND "priorityThreshold" <= 10);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS "notification_preference_user_id_idx"
ON "NotificationPreference"("userId");

CREATE INDEX IF NOT EXISTS "notification_preference_muted_until_idx"
ON "NotificationPreference"("mutedUntil");
