"""anomaly_detector_notification_channel

Revision ID: 0f3086f58700
Revises: af4c4a817a73
Create Date: 2023-03-11 17:26:46.940563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f3086f58700'
down_revision = 'af4c4a817a73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('anomaly_detector_notification_channel')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anomaly_detector_notification_channel',
    sa.Column('anomaly_detector_id', sa.INTEGER(), nullable=True),
    sa.Column('notification_channel_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['anomaly_detector_id'], ['anomaly_detectors.id'], ),
    sa.ForeignKeyConstraint(['notification_channel_id'], ['checks.id'], )
    )
    # ### end Alembic commands ###