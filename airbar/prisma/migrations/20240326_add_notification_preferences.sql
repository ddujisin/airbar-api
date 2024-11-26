-- Create notification preferences table
CREATE TABLE IF NOT EXISTS "NotificationPreference" (
    "id" SERIAL PRIMARY KEY,
    "userId" VARCHAR(255) NOT NULL UNIQUE,
    "enabledChannels" TEXT[] DEFAULT ARRAY['email', 'websocket'],
    "quietHoursStart" INTEGER,
    "quietHoursEnd" INTEGER,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add constraints
ALTER TABLE "NotificationPreference"
ADD CONSTRAINT "quiet_hours_range"
CHECK (
    ("quietHoursStart" IS NULL AND "quietHoursEnd" IS NULL) OR
    ("quietHoursStart" >= 0 AND "quietHoursStart" < 24 AND
     "quietHoursEnd" >= 0 AND "quietHoursEnd" < 24)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS "notification_preference_user_id_idx"
ON "NotificationPreference"("userId");

-- Add trigger for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW."updatedAt" = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_notification_preference_updated_at
    BEFORE UPDATE ON "NotificationPreference"
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
