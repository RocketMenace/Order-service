"""Initial migration

Revision ID: f0ecaa8f00a7
Revises:
Create Date: 2026-01-19 20:32:29.474279

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f0ecaa8f00a7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix enum types if they exist with old uppercase values
    # This handles the case where the database was created with old enum values
    op.execute("""
        DO $$ 
        BEGIN
            -- Check if old enum types exist and need to be fixed
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'eventtypeenum') THEN
                -- Check if enum has old uppercase values
                IF EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'eventtypeenum')
                    AND enumlabel = 'ORDER_CREATED'
                ) THEN
                    -- Create new enum types with correct values
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'eventtypeenum_new') THEN
                        CREATE TYPE eventtypeenum_new AS ENUM (
                            'order.created', 
                            'order.paid', 
                            'order.cancelled', 
                            'order.shipped',
                            'payment.requested', 
                            'shipping.requested'
                        );
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'outboxeventstatusenum_new') THEN
                        CREATE TYPE outboxeventstatusenum_new AS ENUM ('pending', 'sent');
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'inboxeventstatusenum_new') THEN
                        CREATE TYPE inboxeventstatusenum_new AS ENUM ('pending', 'processed');
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatusenum_new') THEN
                        CREATE TYPE orderstatusenum_new AS ENUM ('new', 'paid', 'shipped', 'cancelled');
                    END IF;
                    
                    -- Convert outbox.event_type if table exists
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'outbox') THEN
                        ALTER TABLE outbox 
                        ALTER COLUMN event_type TYPE eventtypeenum_new 
                        USING CASE event_type::text
                            WHEN 'ORDER_CREATED' THEN 'order.created'::eventtypeenum_new
                            WHEN 'ORDER_PAID' THEN 'order.paid'::eventtypeenum_new
                            WHEN 'ORDER_CANCELLED' THEN 'order.cancelled'::eventtypeenum_new
                            WHEN 'PAYMENT_REQUESTED' THEN 'payment.requested'::eventtypeenum_new
                            WHEN 'SHIPPING_REQUESTED' THEN 'shipping.requested'::eventtypeenum_new
                            ELSE 'order.created'::eventtypeenum_new
                        END;
                        
                        ALTER TABLE outbox 
                        ALTER COLUMN status TYPE outboxeventstatusenum_new 
                        USING CASE status::text
                            WHEN 'PENDING' THEN 'pending'::outboxeventstatusenum_new
                            WHEN 'SENT' THEN 'sent'::outboxeventstatusenum_new
                            ELSE 'pending'::outboxeventstatusenum_new
                        END;
                    END IF;
                    
                    -- Convert inbox.event_type if table exists
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'inbox') THEN
                        ALTER TABLE inbox 
                        ALTER COLUMN event_type TYPE eventtypeenum_new 
                        USING CASE event_type::text
                            WHEN 'ORDER_CREATED' THEN 'order.created'::eventtypeenum_new
                            WHEN 'ORDER_PAID' THEN 'order.paid'::eventtypeenum_new
                            WHEN 'ORDER_CANCELLED' THEN 'order.cancelled'::eventtypeenum_new
                            WHEN 'PAYMENT_REQUESTED' THEN 'payment.requested'::eventtypeenum_new
                            WHEN 'SHIPPING_REQUESTED' THEN 'shipping.requested'::eventtypeenum_new
                            ELSE 'order.created'::eventtypeenum_new
                        END;
                        
                        ALTER TABLE inbox 
                        ALTER COLUMN status TYPE inboxeventstatusenum_new 
                        USING CASE status::text
                            WHEN 'PENDING' THEN 'pending'::inboxeventstatusenum_new
                            WHEN 'PROCESSED' THEN 'processed'::inboxeventstatusenum_new
                            ELSE 'pending'::inboxeventstatusenum_new
                        END;
                    END IF;
                    
                    -- Convert order_status.status if table exists
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'order_status') THEN
                        ALTER TABLE order_status 
                        ALTER COLUMN status TYPE orderstatusenum_new 
                        USING CASE status::text
                            WHEN 'NEW' THEN 'new'::orderstatusenum_new
                            WHEN 'PAID' THEN 'paid'::orderstatusenum_new
                            WHEN 'SHIPPED' THEN 'shipped'::orderstatusenum_new
                            WHEN 'CANCELLED' THEN 'cancelled'::orderstatusenum_new
                            ELSE 'new'::orderstatusenum_new
                        END;
                    END IF;
                    
                    -- Drop old enum types
                    DROP TYPE IF EXISTS eventtypeenum CASCADE;
                    DROP TYPE IF EXISTS outboxeventstatusenum CASCADE;
                    DROP TYPE IF EXISTS inboxeventstatusenum CASCADE;
                    DROP TYPE IF EXISTS orderstatusenum CASCADE;
                    
                    -- Rename new enum types to original names
                    ALTER TYPE eventtypeenum_new RENAME TO eventtypeenum;
                    ALTER TYPE outboxeventstatusenum_new RENAME TO outboxeventstatusenum;
                    ALTER TYPE inboxeventstatusenum_new RENAME TO inboxeventstatusenum;
                    ALTER TYPE orderstatusenum_new RENAME TO orderstatusenum;
                END IF;
            END IF;
        END $$;
    """)

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "orders",
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=19, scale=2), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("amount >= 0", name="positive_amount"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("idx_item_id", "orders", ["item_id"], unique=False)
    op.create_index("idx_user_id", "orders", ["user_id"], unique=False)
    op.create_table(
        "outbox",
        sa.Column(
            "event_type",
            sa.Enum(
                "order.created",
                "order.paid",
                "order.cancelled",
                "order.shipped",
                "payment.requested",
                "shipping.requested",
                name="eventtypeenum",
            ),
            nullable=False,
        ),
        sa.Column(
            "payload",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "sent", name="outboxeventstatusenum"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # sa.CheckConstraint("status IN ('PENDING', 'SENT')", name='valid_outbox_status'),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_event_type_status_type", "outbox", ["event_type", "status"], unique=False
    )
    op.create_index("idx_status", "outbox", ["status"], unique=False)
    op.create_table(
        "order_status",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("new", "paid", "shipped", "cancelled", name="orderstatusenum"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # sa.CheckConstraint("status IN ('new', 'paid', 'shipped', 'cancelled')", name='valid_order_status'),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_order_id", "order_status", ["order_id"], unique=False)
    op.create_index(
        "idx_order_id_status", "order_status", ["order_id", "status"], unique=False
    )
    op.create_table(
        "inbox",
        sa.Column(
            "event_type",
            sa.Enum(
                "order.created",
                "order.paid",
                "order.cancelled",
                "order.shipped",
                "payment.requested",
                "shipping.requested",
                name="eventtypeenum",
            ),
            nullable=False,
        ),
        sa.Column(
            "payload",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "processed", name="inboxeventstatusenum"),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # sa.CheckConstraint("status IN ('pending', 'sent')", name='valid_outbox_status'),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("idx_status_inbox", "inbox", ["status"], unique=False)
    op.create_table(
        "notifications",
        sa.Column(
            "payload",
            sa.JSON().with_variant(
                postgresql.JSONB(astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "sent", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("notifications")
    op.drop_index("idx_status", table_name="inbox")
    op.drop_table("inbox")
    op.drop_index("idx_order_id_status", table_name="order_status")
    op.drop_index("idx_order_id", table_name="order_status")
    op.drop_table("order_status")
    op.drop_index("idx_status", table_name="outbox")
    op.drop_index("idx_event_type_status_type", table_name="outbox")
    op.drop_table("outbox")
    op.drop_index("idx_user_id", table_name="orders")
    op.drop_index("idx_item_id", table_name="orders")
    op.drop_table("orders")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS eventtypeenum CASCADE;")
    op.execute("DROP TYPE IF EXISTS outboxeventstatusenum CASCADE;")
    op.execute("DROP TYPE IF EXISTS inboxeventstatusenum CASCADE;")
    op.execute("DROP TYPE IF EXISTS orderstatusenum CASCADE;")
    # ### end Alembic commands ###
