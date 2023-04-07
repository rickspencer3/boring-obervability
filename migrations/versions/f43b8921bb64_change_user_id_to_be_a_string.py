"""change user.id to be a string

Revision ID: f43b8921bb64
Revises: 8bb2089db433
Create Date: 2023-04-07 19:39:33.306893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f43b8921bb64'
down_revision = '8bb2089db433'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=8),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=8),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
