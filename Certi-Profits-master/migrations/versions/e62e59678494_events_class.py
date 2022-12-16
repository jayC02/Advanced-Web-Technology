"""events class

Revision ID: e62e59678494
Revises: 3ef49dbc89f6
Create Date: 2018-11-18 13:28:53.049020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e62e59678494'
down_revision = '3ef49dbc89f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('date', sa.DateTime(), nullable=True))
    op.add_column('post', sa.Column('time', sa.DateTime(), nullable=True))
    op.add_column('post', sa.Column('title', sa.String(length=25), nullable=True))
    op.add_column('post', sa.Column('venue', sa.String(length=70), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'venue')
    op.drop_column('post', 'title')
    op.drop_column('post', 'time')
    op.drop_column('post', 'date')
    # ### end Alembic commands ###