from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    String, Text, Float, Boolean, Integer, Date, JSON,
    ForeignKey, DECIMAL, TIMESTAMP, CheckConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_settings: Mapped[Optional[dict]] = mapped_column(JSON, default={
        "push_enabled": True,
        "email_enabled": False,
        "notify_days_before": [1, 3, 7],
        "daily_digest_time": "09:00",
        "digest_enabled": True
    })
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    owned_households: Mapped[list["Household"]] = relationship(back_populates="owner")
    memberships: Mapped[list["HouseholdMember"]] = relationship(back_populates="user")
    added_products: Mapped[list["Product"]] = relationship(back_populates="added_by")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    added_shopping_items: Mapped[list["ShoppingItem"]] = relationship(back_populates="added_by")
    consumption_logs: Mapped[list["ConsumptionLog"]] = relationship(back_populates="user")


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="owned_households")
    members: Mapped[list["HouseholdMember"]] = relationship(back_populates="household")
    products: Mapped[list["Product"]] = relationship(back_populates="household")
    shopping_lists: Mapped[list["ShoppingList"]] = relationship(back_populates="household")


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="member")
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    household: Mapped["Household"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")

    __table_args__ = (
        CheckConstraint("role IN ('owner', 'member')", name="check_member_role"),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    icon: Mapped[str] = mapped_column(String(50))
    default_shelf_life_days: Mapped[int] = mapped_column(Integer, default=30)

    products: Mapped[list["Product"]] = relationship(back_populates="category")
    product_templates: Mapped[list["ProductTemplate"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    added_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    storage_location: Mapped[str] = mapped_column(String(50), default="refrigerator")
    expiry_date: Mapped[date] = mapped_column(Date, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(20), default="шт")
    price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    household: Mapped["Household"] = relationship(back_populates="products")
    added_by: Mapped["User"] = relationship(back_populates="added_products")
    category: Mapped[Optional["Category"]] = relationship(back_populates="products")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="product")
    consumption_logs: Mapped[list["ConsumptionLog"]] = relationship(back_populates="product")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'expiring_soon', 'expired', 'consumed', 'discarded')",
            name="check_product_status"
        ),
        CheckConstraint(
            "storage_location IN ('refrigerator', 'freezer', 'pantry', 'shelf', 'other')",
            name="check_storage_location"
        ),
    )


class ProductTemplate(Base):
    __tablename__ = "product_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    barcode: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(50), default="manual")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    category: Mapped[Optional["Category"]] = relationship(back_populates="product_templates")

    __table_args__ = (
        CheckConstraint(
            "source IN ('chestnyznak', 'openfoodfacts', 'manual')",
            name="check_template_source"
        ),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), index=True)
    type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    sent_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")
    product: Mapped[Optional["Product"]] = relationship(back_populates="notifications")

    __table_args__ = (
        CheckConstraint(
            "type IN ('expiring_soon', 'expired', 'daily_digest', 'welcome', 'invite')",
            name="check_notification_type"
        ),
    )


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), default="Основной список")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    household: Mapped["Household"] = relationship(back_populates="shopping_lists")
    items: Mapped[list["ShoppingItem"]] = relationship(back_populates="shopping_list")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    list_id: Mapped[int] = mapped_column(ForeignKey("shopping_lists.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(20), default="шт")
    is_purchased: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    added_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    shopping_list: Mapped["ShoppingList"] = relationship(back_populates="items")
    added_by: Mapped["User"] = relationship(back_populates="added_shopping_items")


class ConsumptionLog(Base):
    __tablename__ = "consumption_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, index=True)

    product: Mapped["Product"] = relationship(back_populates="consumption_logs")
    user: Mapped["User"] = relationship(back_populates="consumption_logs")

    __table_args__ = (
        CheckConstraint(
            "action IN ('consumed', 'discarded', 'partial_use')",
            name="check_consumption_action"
        ),
    )
