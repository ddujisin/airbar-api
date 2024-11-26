"""Tests for notification preferences functionality."""
import pytest
from datetime import datetime, timedelta
from app.models.notification_preferences import NotificationPreference
from app.utils.notification_preferences import NotificationPreferencesManager

@pytest.fixture
def test_user():
    """Create a test user ID."""
    return "test_user_123"

@pytest.mark.asyncio
async def test_notification_preferences_crud(test_user):
    """Test CRUD operations for notification preferences."""
    # Create preferences
    prefs = NotificationPreference(
        user_id=test_user,
        enabled_channels=["email", "websocket"],
        quiet_hours_start=22,
        quiet_hours_end=7
    )

    # Save preferences
    saved_prefs = await NotificationPreferencesManager.update_preferences(test_user, prefs)
    assert saved_prefs.user_id == test_user
    assert saved_prefs.quiet_hours_start == 22

    # Get preferences
    retrieved_prefs = await NotificationPreferencesManager.get_preferences(test_user)
    assert retrieved_prefs.user_id == test_user
    assert retrieved_prefs.quiet_hours_start == 22

@pytest.mark.asyncio
async def test_notification_quiet_hours(test_user):
    """Test quiet hours functionality."""
    current_hour = datetime.now().hour
    quiet_start = (current_hour - 1) % 24
    quiet_end = (current_hour + 1) % 24

    prefs = NotificationPreference(
        user_id=test_user,
        quiet_hours_start=quiet_start,
        quiet_hours_end=quiet_end
    )

    saved_prefs = await NotificationPreferencesManager.update_preferences(test_user, prefs)
    should_notify = NotificationPreferencesManager.should_notify(saved_prefs, "email")
    assert not should_notify

@pytest.mark.asyncio
async def test_notification_muting(test_user):
    """Test notification muting functionality."""
    # Set up initial preferences
    prefs = await NotificationPreferencesManager.get_preferences(test_user)
    assert NotificationPreferencesManager.should_notify(prefs, "email")

    # Mute notifications
    muted_prefs = await NotificationPreferencesManager.mute_notifications(test_user, 30)
    assert not NotificationPreferencesManager.should_notify(muted_prefs, "email")

@pytest.mark.asyncio
async def test_priority_threshold(test_user):
    """Test priority threshold functionality."""
    prefs = NotificationPreference(
        user_id=test_user,
        priority_threshold=5
    )

    saved_prefs = await NotificationPreferencesManager.update_preferences(test_user, prefs)

    # Test low priority notification
    assert not NotificationPreferencesManager.should_notify(saved_prefs, "email", priority=3)

    # Test high priority notification
    assert NotificationPreferencesManager.should_notify(saved_prefs, "email", priority=7)
