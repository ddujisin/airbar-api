import pytest
from app.utils.notification_preferences import notification_preferences_manager
from app.utils.notification_manager import notification_manager
from app.models.notification_preferences import NotificationPreferences
from datetime import datetime, timedelta
import pytz

@pytest.fixture
async def test_user():
    """Create a test user with default preferences."""
    user_id = "test-user-123"
    preferences = NotificationPreferences(
        user_id=user_id,
        channels={
            "NEW_ORDER": ["websocket", "email"],
            "PAYMENT": ["websocket"],
            "LOW_STOCK": ["websocket", "email"]
        },
        enabled=True,
        priority_threshold=5
    )
    await notification_preferences_manager.update_preferences(user_id, preferences)
    return user_id

@pytest.mark.asyncio(loop_scope="session")
async def test_notification_preferences_crud(test_user):
    # Test creating and retrieving preferences
    user_id = await test_user  # Await the fixture
    prefs = await notification_preferences_manager.get_preferences(user_id)
    assert prefs.user_id == user_id
    assert "NEW_ORDER" in prefs.channels
    assert "websocket" in prefs.channels["NEW_ORDER"]

    # Test updating preferences
    prefs.channels["NEW_ORDER"] = ["websocket"]
    updated_prefs = await notification_preferences_manager.update_preferences(user_id, prefs)
    assert len(updated_prefs.channels["NEW_ORDER"]) == 1
    assert updated_prefs.channels["NEW_ORDER"][0] == "websocket"

@pytest.mark.asyncio(loop_scope="session")
async def test_notification_quiet_hours(test_user):
    # Test quiet hours functionality
    user_id = await test_user  # Await the fixture
    prefs = await notification_preferences_manager.get_preferences(user_id)
    current_day = datetime.now(pytz.UTC).strftime("%A").lower()

    # Set quiet hours for current day
    prefs.quiet_hours = {
        current_day: {
            "start": "00:00",
            "end": "23:59"
        }
    }
    await notification_preferences_manager.update_preferences(user_id, prefs)

    # Verify notification is blocked during quiet hours
    should_send = notification_preferences_manager.should_send_notification(
        prefs,
        "NEW_ORDER",
        "websocket"
    )
    assert not should_send

@pytest.mark.asyncio(loop_scope="session")
async def test_notification_creation_with_preferences(test_user):
    # Test notification creation respecting preferences
    user_id = await test_user  # Await the fixture
    notification = await notification_manager.create_notification(
        type="NEW_ORDER",
        message="Test notification",
        target_user=user_id
    )
    assert notification is not None

    # Disable notifications and verify no notification is created
    prefs = await notification_preferences_manager.get_preferences(user_id)
    prefs.enabled = False
    await notification_preferences_manager.update_preferences(user_id, prefs)

    notification = await notification_manager.create_notification(
        type="NEW_ORDER",
        message="Test notification",
        target_user=user_id
    )
    assert notification is None

@pytest.mark.asyncio(loop_scope="session")
async def test_notification_muting(test_user):
    """Test notification muting functionality."""
    user_id = await test_user
    prefs = await notification_preferences_manager.get_preferences(user_id)

    # Set mute for 30 minutes
    muted_until = datetime.now(pytz.UTC) + timedelta(minutes=30)
    prefs.muted_until = muted_until.isoformat()
    await notification_preferences_manager.update_preferences(user_id, prefs)

    # Verify notifications are blocked while muted
    should_send = notification_preferences_manager.should_send_notification(
        prefs,
        "NEW_ORDER",
        "websocket"
    )
    assert not should_send

    # Test unmuting
    prefs.muted_until = None
    await notification_preferences_manager.update_preferences(user_id, prefs)
    should_send = notification_preferences_manager.should_send_notification(
        prefs,
        "NEW_ORDER",
        "websocket"
    )
    assert should_send

@pytest.mark.asyncio(loop_scope="session")
async def test_priority_threshold(test_user):
    """Test priority threshold functionality."""
    user_id = await test_user
    prefs = await notification_preferences_manager.get_preferences(user_id)

    # Set priority threshold
    prefs.priority_threshold = 7
    await notification_preferences_manager.update_preferences(user_id, prefs)

    # Test notification below threshold
    should_send = notification_preferences_manager.should_send_notification(
        prefs,
        "NEW_ORDER",
        "websocket",
        priority=5
    )
    assert not should_send

    # Test notification above threshold
    should_send = notification_preferences_manager.should_send_notification(
        prefs,
        "NEW_ORDER",
        "websocket",
        priority=8
    )
    assert should_send
