"""Adding links table

Revision ID: 9d69ed3d4c1f
Revises: 3b7b64abf9a3
Create Date: 2020-06-06 13:31:27.268481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d69ed3d4c1f"
down_revision = "3b7b64abf9a3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("link", sa.String(length=16), nullable=True),
        sa.Column("visits", sa.Integer(), nullable=True),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("link"),
        sa.UniqueConstraint("url"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("links")
    # ### end Alembic commands ###