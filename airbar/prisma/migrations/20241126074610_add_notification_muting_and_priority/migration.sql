-- AlterTable
ALTER TABLE "notification_preferences" ADD COLUMN     "mutedUntil" TIMESTAMP(3),
ADD COLUMN     "priorityThreshold" INTEGER NOT NULL DEFAULT 5;
