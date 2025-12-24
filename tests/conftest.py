"""
Pytest configuration and fixtures for FoodTracker database model tests.
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import (
    Base, User, Household, HouseholdMember, Category, Product,
    ProductTemplate, Notification, ShoppingList, ShoppingItem, ConsumptionLog
)


@pytest.fixture(scope="function")
def engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine):
    """Create a new database session for a test."""
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def sample_user(session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password_123",
        name="Test User"
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def sample_user_2(session):
    """Create a second sample user for testing."""
    user = User(
        email="test2@example.com",
        password_hash="hashed_password_456",
        name="Test User 2"
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def sample_household(session, sample_user):
    """Create a sample household for testing."""
    household = Household(
        name="Test Household",
        owner_id=sample_user.id,
        invite_code="ABC123"
    )
    session.add(household)
    session.commit()
    return household


@pytest.fixture
def sample_category(session):
    """Create a sample category for testing."""
    category = Category(
        name="Dairy",
        icon="milk",
        default_shelf_life_days=14
    )
    session.add(category)
    session.commit()
    return category


@pytest.fixture
def sample_product(session, sample_household, sample_user, sample_category):
    """Create a sample product for testing."""
    product = Product(
        household_id=sample_household.id,
        added_by_id=sample_user.id,
        name="Milk",
        barcode="1234567890123",
        category_id=sample_category.id,
        storage_location="refrigerator",
        expiry_date=date.today() + timedelta(days=7),
        quantity=1,
        unit="л",
        price=Decimal("89.99"),
        status="active"
    )
    session.add(product)
    session.commit()
    return product


@pytest.fixture
def sample_shopping_list(session, sample_household):
    """Create a sample shopping list for testing."""
    shopping_list = ShoppingList(
        household_id=sample_household.id,
        name="Weekly Shopping"
    )
    session.add(shopping_list)
    session.commit()
    return shopping_list
