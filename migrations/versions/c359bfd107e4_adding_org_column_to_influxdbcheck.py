"""adding org column to InfluxDBCheck

Revision ID: c359bfd107e4
Revises: 
Create Date: 2023-05-22 16:47:03.175887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c359bfd107e4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('checks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('org', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('checks', schema=None) as batch_op:
        batch_op.drop_column('org')

    # ### end Alembic commands ###
