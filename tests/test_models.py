"""
Comprehensive tests for FoodTracker SQLAlchemy ORM models.

Tests cover:
- Model creation and attributes
- Default values
- Relationships between models
- Check constraints validation
- Unique constraints
- CRUD operations
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from db.models import (
    Base, User, Household, HouseholdMember, Category, Product,
    ProductTemplate, Notification, ShoppingList, ShoppingItem, ConsumptionLog
)


# ============================================================================
# User Model Tests
# ============================================================================

class TestUserModel:
    """Tests for the User model."""

    def test_create_user_with_required_fields(self, session):
        """Test creating a user with only required fields."""
        user = User(
            email="user@example.com",
            password_hash="hashed_password",
            name="John Doe"
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.email == "user@example.com"
        assert user.password_hash == "hashed_password"
        assert user.name == "John Doe"

    def test_user_default_values(self, session):
        """Test that user default values are set correctly."""
        user = User(
            email="default@example.com",
            password_hash="hashed",
            name="Default User"
        )
        session.add(user)
        session.commit()

        assert user.is_verified is False
        assert user.is_blocked is False
        assert user.avatar_url is None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_notification_settings_default(self, session):
        """Test default notification settings for user."""
        user = User(
            email="notify@example.com",
            password_hash="hashed",
            name="Notify User"
        )
        session.add(user)
        session.commit()

        expected_settings = {
            "push_enabled": True,
            "email_enabled": False,
            "notify_days_before": [1, 3, 7],
            "daily_digest_time": "09:00",
            "digest_enabled": True
        }
        assert user.notification_settings == expected_settings

    def test_user_custom_notification_settings(self, session):
        """Test user with custom notification settings."""
        custom_settings = {
            "push_enabled": False,
            "email_enabled": True,
            "notify_days_before": [2, 5],
            "daily_digest_time": "18:00",
            "digest_enabled": False
        }
        user = User(
            email="custom@example.com",
            password_hash="hashed",
            name="Custom User",
            notification_settings=custom_settings
        )
        session.add(user)
        session.commit()

        assert user.notification_settings == custom_settings

    def test_user_email_unique_constraint(self, session):
        """Test that email must be unique."""
        user1 = User(
            email="unique@example.com",
            password_hash="hash1",
            name="User 1"
        )
        session.add(user1)
        session.commit()

        user2 = User(
            email="unique@example.com",
            password_hash="hash2",
            name="User 2"
        )
        session.add(user2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_user_with_optional_fields(self, session):
        """Test user creation with all optional fields."""
        user = User(
            email="full@example.com",
            password_hash="hashed",
            name="Full User",
            avatar_url="https://example.com/avatar.jpg",
            is_verified=True,
            is_blocked=False
        )
        session.add(user)
        session.commit()

        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.is_verified is True

    def test_user_relationships_initialization(self, session):
        """Test that user relationships are initialized as empty lists."""
        user = User(
            email="relations@example.com",
            password_hash="hashed",
            name="Relations User"
        )
        session.add(user)
        session.commit()

        assert user.owned_households == []
        assert user.memberships == []
        assert user.added_products == []
        assert user.notifications == []
        assert user.added_shopping_items == []
        assert user.consumption_logs == []


# ============================================================================
# Household Model Tests
# ============================================================================

class TestHouseholdModel:
    """Tests for the Household model."""

    def test_create_household(self, session, sample_user):
        """Test creating a household."""
        household = Household(
            name="My Home",
            owner_id=sample_user.id,
            invite_code="XYZ789"
        )
        session.add(household)
        session.commit()

        assert household.id is not None
        assert household.name == "My Home"
        assert household.owner_id == sample_user.id
        assert household.invite_code == "XYZ789"
        assert household.created_at is not None

    def test_household_owner_relationship(self, session, sample_user):
        """Test household-owner relationship."""
        household = Household(
            name="Family Home",
            owner_id=sample_user.id,
            invite_code="FAM123"
        )
        session.add(household)
        session.commit()

        assert household.owner == sample_user
        assert household in sample_user.owned_households

    def test_household_invite_code_unique(self, session, sample_user):
        """Test that invite code must be unique."""
        household1 = Household(
            name="Home 1",
            owner_id=sample_user.id,
            invite_code="SAME123"
        )
        session.add(household1)
        session.commit()

        household2 = Household(
            name="Home 2",
            owner_id=sample_user.id,
            invite_code="SAME123"
        )
        session.add(household2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_household_relationships_initialization(self, session, sample_user):
        """Test household relationships are initialized correctly."""
        household = Household(
            name="Empty Home",
            owner_id=sample_user.id,
            invite_code="EMPTY1"
        )
        session.add(household)
        session.commit()

        assert household.members == []
        assert household.products == []
        assert household.shopping_lists == []


# ============================================================================
# HouseholdMember Model Tests
# ============================================================================

class TestHouseholdMemberModel:
    """Tests for the HouseholdMember model."""

    def test_create_household_member_default_role(self, session, sample_household, sample_user_2):
        """Test creating a household member with default role."""
        member = HouseholdMember(
            household_id=sample_household.id,
            user_id=sample_user_2.id
        )
        session.add(member)
        session.commit()

        assert member.id is not None
        assert member.role == "member"
        assert member.joined_at is not None

    def test_create_household_member_owner_role(self, session, sample_household, sample_user):
        """Test creating a household member with owner role."""
        member = HouseholdMember(
            household_id=sample_household.id,
            user_id=sample_user.id,
            role="owner"
        )
        session.add(member)
        session.commit()

        assert member.role == "owner"

    def test_household_member_relationships(self, session, sample_household, sample_user_2):
        """Test household member relationships."""
        member = HouseholdMember(
            household_id=sample_household.id,
            user_id=sample_user_2.id,
            role="member"
        )
        session.add(member)
        session.commit()

        assert member.household == sample_household
        assert member.user == sample_user_2
        assert member in sample_household.members
        assert member in sample_user_2.memberships


# ============================================================================
# Category Model Tests
# ============================================================================

class TestCategoryModel:
    """Tests for the Category model."""

    def test_create_category(self, session):
        """Test creating a category."""
        category = Category(
            name="Vegetables",
            icon="carrot"
        )
        session.add(category)
        session.commit()

        assert category.id is not None
        assert category.name == "Vegetables"
        assert category.icon == "carrot"

    def test_category_default_shelf_life(self, session):
        """Test default shelf life for category."""
        category = Category(
            name="Grains",
            icon="wheat"
        )
        session.add(category)
        session.commit()

        assert category.default_shelf_life_days == 30

    def test_category_custom_shelf_life(self, session):
        """Test custom shelf life for category."""
        category = Category(
            name="Meat",
            icon="steak",
            default_shelf_life_days=5
        )
        session.add(category)
        session.commit()

        assert category.default_shelf_life_days == 5

    def test_category_name_unique(self, session):
        """Test that category name must be unique."""
        category1 = Category(name="Dairy", icon="milk")
        session.add(category1)
        session.commit()

        category2 = Category(name="Dairy", icon="cheese")
        session.add(category2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_category_relationships(self, session):
        """Test category relationships initialization."""
        category = Category(name="Fruits", icon="apple")
        session.add(category)
        session.commit()

        assert category.products == []
        assert category.product_templates == []


# ============================================================================
# Product Model Tests
# ============================================================================

class TestProductModel:
    """Tests for the Product model."""

    def test_create_product_with_required_fields(self, session, sample_household, sample_user):
        """Test creating a product with required fields."""
        product = Product(
            household_id=sample_household.id,
            added_by_id=sample_user.id,
            name="Bread",
            expiry_date=date.today() + timedelta(days=5)
        )
        session.add(product)
        session.commit()

        assert product.id is not None
        assert product.name == "Bread"

    def test_product_default_values(self, session, sample_household, sample_user):
        """Test product default values."""
        product = Product(
            household_id=sample_household.id,
            added_by_id=sample_user.id,
            name="Default Product",
            expiry_date=date.today()
        )
        session.add(product)
        session.commit()

        assert product.storage_location == "refrigerator"
        assert product.quantity == 1
        assert product.unit == "шт"
        assert product.status == "active"
        assert product.barcode is None
        assert product.price is None
        assert product.image_url is None

    def test_product_all_storage_locations(self, session, sample_household, sample_user):
        """Test all valid storage locations."""
        locations = ["refrigerator", "freezer", "pantry", "shelf", "other"]

        for i, location in enumerate(locations):
            product = Product(
                household_id=sample_household.id,
                added_by_id=sample_user.id,
                name=f"Product {i}",
                storage_location=location,
                expiry_date=date.today()
            )
            session.add(product)

        session.commit()

        products = session.query(Product).all()
        stored_locations = [p.storage_location for p in products]
        for location in locations:
            assert location in stored_locations

    def test_product_all_statuses(self, session, sample_household, sample_user):
        """Test all valid product statuses."""
        statuses = ["active", "expiring_soon", "expired", "consumed", "discarded"]

        for i, status in enumerate(statuses):
            product = Product(
                household_id=sample_household.id,
                added_by_id=sample_user.id,
                name=f"Product {i}",
                status=status,
                expiry_date=date.today()
            )
            session.add(product)

        session.commit()

        products = session.query(Product).all()
        stored_statuses = [p.status for p in products]
        for status in statuses:
            assert status in stored_statuses

    def test_product_with_price(self, session, sample_household, sample_user):
        """Test product with decimal price."""
        product = Product(
            household_id=sample_household.id,
            added_by_id=sample_user.id,
            name="Expensive Item",
            expiry_date=date.today(),
            price=Decimal("1234.56")
        )
        session.add(product)
        session.commit()

        assert product.price == Decimal("1234.56")

    def test_product_relationships(self, session, sample_household, sample_user, sample_category):
        """Test product relationships."""
        product = Product(
            household_id=sample_household.id,
            added_by_id=sample_user.id,
            name="Related Product",
            category_id=sample_category.id,
            expiry_date=date.today()
        )
        session.add(product)
        session.commit()

        assert product.household == sample_household
        assert product.added_by == sample_user
        assert product.category == sample_category
        assert product in sample_household.products
        assert product in sample_user.added_products
        assert product in sample_category.products

    def test_product_without_category(self, session, sample_household, sample_user):
        """Test product can be created without a category."""
        product = Product(
            household_id=sample_household.id,
            added_by_id=sample_user.id,
            name="Uncategorized",
            expiry_date=date.today()
        )
        session.add(product)
        session.commit()

        assert product.category is None
        assert product.category_id is None


# ============================================================================
# ProductTemplate Model Tests
# ============================================================================

class TestProductTemplateModel:
    """Tests for the ProductTemplate model."""

    def test_create_product_template(self, session):
        """Test creating a product template."""
        template = ProductTemplate(
            barcode="1234567890123",
            name="Generic Milk"
        )
        session.add(template)
        session.commit()

        assert template.id is not None
        assert template.barcode == "1234567890123"
        assert template.name == "Generic Milk"

    def test_product_template_default_source(self, session):
        """Test default source for product template."""
        template = ProductTemplate(
            barcode="9876543210987",
            name="Default Template"
        )
        session.add(template)
        session.commit()

        assert template.source == "manual"

    def test_product_template_all_sources(self, session):
        """Test all valid template sources."""
        sources = ["chestnyznak", "openfoodfacts", "manual"]

        for i, source in enumerate(sources):
            template = ProductTemplate(
                barcode=f"000000000000{i}",
                name=f"Template {i}",
                source=source
            )
            session.add(template)

        session.commit()

        templates = session.query(ProductTemplate).all()
        stored_sources = [t.source for t in templates]
        for source in sources:
            assert source in stored_sources

    def test_product_template_barcode_unique(self, session):
        """Test that barcode must be unique."""
        template1 = ProductTemplate(barcode="1111111111111", name="Template 1")
        session.add(template1)
        session.commit()

        template2 = ProductTemplate(barcode="1111111111111", name="Template 2")
        session.add(template2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_product_template_with_category(self, session, sample_category):
        """Test product template with category relationship."""
        template = ProductTemplate(
            barcode="2222222222222",
            name="Categorized Template",
            category_id=sample_category.id,
            brand="BrandName",
            image_url="https://example.com/image.jpg"
        )
        session.add(template)
        session.commit()

        assert template.category == sample_category
        assert template in sample_category.product_templates
        assert template.brand == "BrandName"


# ============================================================================
# Notification Model Tests
# ============================================================================

class TestNotificationModel:
    """Tests for the Notification model."""

    def test_create_notification(self, session, sample_user, sample_product):
        """Test creating a notification."""
        notification = Notification(
            user_id=sample_user.id,
            product_id=sample_product.id,
            type="expiring_soon",
            title="Product Expiring",
            body="Your Milk will expire in 3 days"
        )
        session.add(notification)
        session.commit()

        assert notification.id is not None
        assert notification.type == "expiring_soon"
        assert notification.title == "Product Expiring"

    def test_notification_default_values(self, session, sample_user):
        """Test notification default values."""
        notification = Notification(
            user_id=sample_user.id,
            type="welcome",
            title="Welcome!",
            body="Welcome to FoodTracker"
        )
        session.add(notification)
        session.commit()

        assert notification.is_read is False
        assert notification.is_sent is False
        assert notification.scheduled_at is None
        assert notification.sent_at is None
        assert notification.created_at is not None

    def test_notification_all_types(self, session, sample_user):
        """Test all valid notification types."""
        types = ["expiring_soon", "expired", "daily_digest", "welcome", "invite"]

        for i, notif_type in enumerate(types):
            notification = Notification(
                user_id=sample_user.id,
                type=notif_type,
                title=f"Title {i}",
                body=f"Body {i}"
            )
            session.add(notification)

        session.commit()

        notifications = session.query(Notification).all()
        stored_types = [n.type for n in notifications]
        for notif_type in types:
            assert notif_type in stored_types

    def test_notification_without_product(self, session, sample_user):
        """Test notification can be created without a product."""
        notification = Notification(
            user_id=sample_user.id,
            type="welcome",
            title="Welcome",
            body="Welcome to the app"
        )
        session.add(notification)
        session.commit()

        assert notification.product is None

    def test_notification_with_scheduling(self, session, sample_user):
        """Test notification with scheduling and sending."""
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        sent_time = datetime.utcnow()

        notification = Notification(
            user_id=sample_user.id,
            type="daily_digest",
            title="Daily Digest",
            body="Your daily summary",
            scheduled_at=scheduled_time,
            sent_at=sent_time,
            is_sent=True,
            is_read=True
        )
        session.add(notification)
        session.commit()

        assert notification.scheduled_at == scheduled_time
        assert notification.sent_at == sent_time
        assert notification.is_sent is True
        assert notification.is_read is True

    def test_notification_relationships(self, session, sample_user, sample_product):
        """Test notification relationships."""
        notification = Notification(
            user_id=sample_user.id,
            product_id=sample_product.id,
            type="expired",
            title="Expired",
            body="Product has expired"
        )
        session.add(notification)
        session.commit()

        assert notification.user == sample_user
        assert notification.product == sample_product
        assert notification in sample_user.notifications
        assert notification in sample_product.notifications


# ============================================================================
# ShoppingList Model Tests
# ============================================================================

class TestShoppingListModel:
    """Tests for the ShoppingList model."""

    def test_create_shopping_list(self, session, sample_household):
        """Test creating a shopping list."""
        shopping_list = ShoppingList(
            household_id=sample_household.id,
            name="Groceries"
        )
        session.add(shopping_list)
        session.commit()

        assert shopping_list.id is not None
        assert shopping_list.name == "Groceries"

    def test_shopping_list_default_values(self, session, sample_household):
        """Test shopping list default values."""
        shopping_list = ShoppingList(
            household_id=sample_household.id
        )
        session.add(shopping_list)
        session.commit()

        assert shopping_list.name == "Основной список"
        assert shopping_list.is_active is True
        assert shopping_list.created_at is not None

    def test_shopping_list_relationships(self, session, sample_household):
        """Test shopping list relationships."""
        shopping_list = ShoppingList(
            household_id=sample_household.id,
            name="Weekly"
        )
        session.add(shopping_list)
        session.commit()

        assert shopping_list.household == sample_household
        assert shopping_list in sample_household.shopping_lists
        assert shopping_list.items == []

    def test_shopping_list_inactive(self, session, sample_household):
        """Test creating an inactive shopping list."""
        shopping_list = ShoppingList(
            household_id=sample_household.id,
            name="Old List",
            is_active=False
        )
        session.add(shopping_list)
        session.commit()

        assert shopping_list.is_active is False


# ============================================================================
# ShoppingItem Model Tests
# ============================================================================

class TestShoppingItemModel:
    """Tests for the ShoppingItem model."""

    def test_create_shopping_item(self, session, sample_shopping_list, sample_user):
        """Test creating a shopping item."""
        item = ShoppingItem(
            list_id=sample_shopping_list.id,
            name="Apples",
            added_by_id=sample_user.id
        )
        session.add(item)
        session.commit()

        assert item.id is not None
        assert item.name == "Apples"

    def test_shopping_item_default_values(self, session, sample_shopping_list, sample_user):
        """Test shopping item default values."""
        item = ShoppingItem(
            list_id=sample_shopping_list.id,
            name="Item",
            added_by_id=sample_user.id
        )
        session.add(item)
        session.commit()

        assert item.quantity == 1
        assert item.unit == "шт"
        assert item.is_purchased is False
        assert item.created_at is not None

    def test_shopping_item_with_all_fields(self, session, sample_shopping_list, sample_user):
        """Test shopping item with all fields."""
        item = ShoppingItem(
            list_id=sample_shopping_list.id,
            name="Bananas",
            quantity=6,
            unit="кг",
            is_purchased=True,
            added_by_id=sample_user.id
        )
        session.add(item)
        session.commit()

        assert item.quantity == 6
        assert item.unit == "кг"
        assert item.is_purchased is True

    def test_shopping_item_relationships(self, session, sample_shopping_list, sample_user):
        """Test shopping item relationships."""
        item = ShoppingItem(
            list_id=sample_shopping_list.id,
            name="Oranges",
            added_by_id=sample_user.id
        )
        session.add(item)
        session.commit()

        assert item.shopping_list == sample_shopping_list
        assert item.added_by == sample_user
        assert item in sample_shopping_list.items
        assert item in sample_user.added_shopping_items


# ============================================================================
# ConsumptionLog Model Tests
# ============================================================================

class TestConsumptionLogModel:
    """Tests for the ConsumptionLog model."""

    def test_create_consumption_log(self, session, sample_product, sample_user):
        """Test creating a consumption log."""
        log = ConsumptionLog(
            product_id=sample_product.id,
            user_id=sample_user.id,
            action="consumed"
        )
        session.add(log)
        session.commit()

        assert log.id is not None
        assert log.action == "consumed"

    def test_consumption_log_default_quantity(self, session, sample_product, sample_user):
        """Test default quantity for consumption log."""
        log = ConsumptionLog(
            product_id=sample_product.id,
            user_id=sample_user.id,
            action="consumed"
        )
        session.add(log)
        session.commit()

        assert log.quantity == 1
        assert log.created_at is not None

    def test_consumption_log_all_actions(self, session, sample_product, sample_user):
        """Test all valid consumption actions."""
        actions = ["consumed", "discarded", "partial_use"]

        for action in actions:
            log = ConsumptionLog(
                product_id=sample_product.id,
                user_id=sample_user.id,
                action=action,
                quantity=1
            )
            session.add(log)

        session.commit()

        logs = session.query(ConsumptionLog).all()
        stored_actions = [l.action for l in logs]
        for action in actions:
            assert action in stored_actions

    def test_consumption_log_custom_quantity(self, session, sample_product, sample_user):
        """Test consumption log with custom quantity."""
        log = ConsumptionLog(
            product_id=sample_product.id,
            user_id=sample_user.id,
            action="partial_use",
            quantity=3
        )
        session.add(log)
        session.commit()

        assert log.quantity == 3

    def test_consumption_log_relationships(self, session, sample_product, sample_user):
        """Test consumption log relationships."""
        log = ConsumptionLog(
            product_id=sample_product.id,
            user_id=sample_user.id,
            action="discarded"
        )
        session.add(log)
        session.commit()

        assert log.product == sample_product
        assert log.user == sample_user
        assert log in sample_product.consumption_logs
        assert log in sample_user.consumption_logs


# ============================================================================
# Integration Tests - Complex Scenarios
# ============================================================================

class TestIntegration:
    """Integration tests for complex model interactions."""

    def test_full_household_workflow(self, session):
        """Test complete household creation with members and products."""
        # Create owner
        owner = User(
            email="owner@example.com",
            password_hash="hash",
            name="Owner"
        )
        session.add(owner)
        session.commit()

        # Create household
        household = Household(
            name="Smith Family",
            owner_id=owner.id,
            invite_code="SMITH1"
        )
        session.add(household)
        session.commit()

        # Add owner as member
        owner_member = HouseholdMember(
            household_id=household.id,
            user_id=owner.id,
            role="owner"
        )
        session.add(owner_member)

        # Create another user and add as member
        member_user = User(
            email="member@example.com",
            password_hash="hash",
            name="Member"
        )
        session.add(member_user)
        session.commit()

        member = HouseholdMember(
            household_id=household.id,
            user_id=member_user.id,
            role="member"
        )
        session.add(member)
        session.commit()

        # Create category and product
        category = Category(name="Dairy", icon="milk")
        session.add(category)
        session.commit()

        product = Product(
            household_id=household.id,
            added_by_id=owner.id,
            name="Milk",
            category_id=category.id,
            expiry_date=date.today() + timedelta(days=5)
        )
        session.add(product)
        session.commit()

        # Verify relationships
        assert len(household.members) == 2
        assert len(household.products) == 1
        assert product.household == household
        assert product.category == category

    def test_shopping_list_with_items(self, session, sample_household, sample_user):
        """Test shopping list with multiple items."""
        shopping_list = ShoppingList(
            household_id=sample_household.id,
            name="Weekly Shopping"
        )
        session.add(shopping_list)
        session.commit()

        items = [
            ShoppingItem(list_id=shopping_list.id, name="Milk", quantity=2, added_by_id=sample_user.id),
            ShoppingItem(list_id=shopping_list.id, name="Bread", quantity=1, added_by_id=sample_user.id),
            ShoppingItem(list_id=shopping_list.id, name="Eggs", quantity=12, unit="шт", added_by_id=sample_user.id),
        ]
        for item in items:
            session.add(item)
        session.commit()

        assert len(shopping_list.items) == 3
        assert all(item.shopping_list == shopping_list for item in items)

    def test_product_lifecycle(self, session, sample_household, sample_user, sample_category):
        """Test product through its lifecycle with notifications and consumption."""
        # Create product
        product = Product(
            household_id=sample_household.id,
            added_by_id=sample_user.id,
            name="Yogurt",
            category_id=sample_category.id,
            expiry_date=date.today() + timedelta(days=7),
            status="active"
        )
        session.add(product)
        session.commit()

        # Add expiring soon notification
        notification = Notification(
            user_id=sample_user.id,
            product_id=product.id,
            type="expiring_soon",
            title="Yogurt Expiring",
            body="Yogurt will expire in 3 days"
        )
        session.add(notification)
        session.commit()

        # Log partial consumption
        log1 = ConsumptionLog(
            product_id=product.id,
            user_id=sample_user.id,
            action="partial_use",
            quantity=1
        )
        session.add(log1)

        # Update product status
        product.status = "expiring_soon"
        session.commit()

        # Log full consumption
        log2 = ConsumptionLog(
            product_id=product.id,
            user_id=sample_user.id,
            action="consumed",
            quantity=1
        )
        session.add(log2)
        product.status = "consumed"
        session.commit()

        # Verify
        assert product.status == "consumed"
        assert len(product.notifications) == 1
        assert len(product.consumption_logs) == 2
        assert product.notifications[0].type == "expiring_soon"

    def test_multiple_households_per_user(self, session):
        """Test user can own multiple households."""
        user = User(
            email="multi@example.com",
            password_hash="hash",
            name="Multi Owner"
        )
        session.add(user)
        session.commit()

        households = []
        for i in range(3):
            household = Household(
                name=f"Home {i}",
                owner_id=user.id,
                invite_code=f"CODE{i}"
            )
            session.add(household)
            households.append(household)
        session.commit()

        assert len(user.owned_households) == 3

    def test_user_membership_in_multiple_households(self, session):
        """Test user can be member of multiple households."""
        owner = User(email="owner2@example.com", password_hash="hash", name="Owner")
        member = User(email="member2@example.com", password_hash="hash", name="Member")
        session.add_all([owner, member])
        session.commit()

        # Create multiple households
        for i in range(3):
            household = Household(
                name=f"Household {i}",
                owner_id=owner.id,
                invite_code=f"INVITE{i}"
            )
            session.add(household)
            session.commit()

            membership = HouseholdMember(
                household_id=household.id,
                user_id=member.id,
                role="member"
            )
            session.add(membership)

        session.commit()

        assert len(member.memberships) == 3


# ============================================================================
# Model Metadata Tests
# ============================================================================

class TestModelMetadata:
    """Tests for model table metadata and structure."""

    def test_all_models_have_tablenames(self):
        """Test all models have proper table names."""
        expected_tables = {
            "users", "households", "household_members", "categories",
            "products", "product_templates", "notifications",
            "shopping_lists", "shopping_items", "consumption_logs"
        }
        actual_tables = set(Base.metadata.tables.keys())
        assert expected_tables == actual_tables

    def test_user_table_columns(self, engine):
        """Test User table has expected columns."""
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("users")}
        expected = {
            "id", "email", "password_hash", "name", "avatar_url",
            "is_verified", "is_blocked", "notification_settings",
            "created_at", "updated_at"
        }
        assert expected.issubset(columns)

    def test_product_table_columns(self, engine):
        """Test Product table has expected columns."""
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("products")}
        expected = {
            "id", "household_id", "added_by_id", "name", "barcode",
            "category_id", "storage_location", "expiry_date", "quantity",
            "unit", "price", "status", "image_url", "created_at", "updated_at"
        }
        assert expected.issubset(columns)

    def test_indexes_exist(self, engine):
        """Test that important indexes exist."""
        inspector = inspect(engine)

        # Check users table indexes
        user_indexes = inspector.get_indexes("users")
        user_index_columns = [idx["column_names"] for idx in user_indexes]
        assert ["email"] in user_index_columns

        # Check products table indexes
        product_indexes = inspector.get_indexes("products")
        product_index_columns = [idx["column_names"] for idx in product_indexes]
        assert ["name"] in product_index_columns
        assert ["status"] in product_index_columns
        assert ["expiry_date"] in product_index_columns
